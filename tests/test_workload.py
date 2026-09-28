import copy
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from workload.app import ContractError, canonical_operation_digest, evaluate, load_ledger, metrics_text, validate_request

ROOT = Path(__file__).resolve().parents[1]


def request(name="approved-migration-request.json"):
    return json.loads((ROOT / "contracts/examples" / name).read_text())


class OperationsAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.temp.name) / "evidence.jsonl"
        self.env = patch.dict(os.environ, {"ADAPTER_MODE": "rehearsal", "LEDGER_PATH": str(self.ledger)}, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def test_approved_migration_completes_seven_state_journey(self):
        response, evidence = evaluate(request())
        self.assertEqual(response["decision"], "ALLOW_REVIEW")
        self.assertEqual(response["source_state"], "REHEARSAL")
        self.assertEqual(response["validation"]["status"], "PASS")
        self.assertEqual(response["validation"]["infrastructure"], "PASS")
        self.assertEqual(response["validation"]["application"], "PASS")
        self.assertEqual([item["state"] for item in evidence], ["OBSERVE", "PREFLIGHT", "PROPOSE", "APPROVE", "EXECUTE", "VALIDATE", "LEARN"])
        self.assertFalse(response["authority"]["automated_action_performed"])

    def test_complete_preflight_without_approval_stops_at_propose(self):
        payload = request()
        payload["approval"] = None
        response, evidence = evaluate(payload)
        self.assertEqual(response["decision"], "ALLOW_REVIEW")
        self.assertEqual(response["reason_codes"], ["HUMAN_APPROVAL_REQUIRED"])
        self.assertEqual(response["validation"]["status"], "NOT_RUN")
        self.assertEqual([item["state"] for item in evidence], ["OBSERVE", "PREFLIGHT", "PROPOSE"])

    def test_known_incompatibility_refuses_before_execution(self):
        payload = request()
        payload["preflight"]["storage_compatible"] = False
        response, evidence = evaluate(payload)
        self.assertEqual((response["decision"], response["reason_codes"]), ("REFUSE", ["STORAGE_INCOMPATIBLE"]))
        self.assertNotIn("EXECUTE", [item["state"] for item in evidence])

    def test_stale_or_incomplete_evidence_abstains(self):
        for field in ("evidence_fresh", "correlation_complete"):
            payload = request()
            payload["preflight"][field] = False
            response, _ = evaluate(payload)
            self.assertEqual(response["decision"], "ABSTAIN")

    def test_approval_digest_and_expiry_are_enforced(self):
        payload = request()
        payload["approval"]["operation_digest"] = "sha256:" + "0" * 64
        self.assertEqual(evaluate(payload)[0]["reason_codes"], ["APPROVAL_DIGEST_MISMATCH"])
        payload = request()
        payload["approval"]["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        self.assertEqual(evaluate(payload)[0]["reason_codes"], ["APPROVAL_EXPIRED"])

    def test_dependency_outage_is_degraded_without_ai_claim(self):
        response, _ = evaluate(request("dependency-outage-request.json"))
        self.assertEqual((response["decision"], response["validation"]["status"]), ("ABSTAIN", "INCOMPLETE"))
        self.assertEqual(response["reason_codes"], ["AI_DEPENDENCY_UNAVAILABLE"])
        self.assertIsNone(response["explanation"])
        self.assertFalse(response["ai_participated"])

    def test_infrastructure_success_does_not_mask_application_failure(self):
        response, _ = evaluate(request("application-failure-request.json"))
        self.assertEqual(response["validation"]["infrastructure"], "PASS")
        self.assertEqual(response["validation"]["application"], "FAIL")
        self.assertEqual((response["decision"], response["reason_codes"]), ("REFUSE", ["APPLICATION_FAILED_AFTER_INFRA_SUCCESS"]))

    def test_ledger_is_reloadable(self):
        response, evidence = evaluate(request())
        reloaded = load_ledger(self.ledger)
        self.assertEqual(len(reloaded), len(evidence))
        self.assertEqual(reloaded[-1]["request_id"], response["request_id"])
        self.assertTrue(all(item["digest"].startswith("sha256:") for item in reloaded))

    def test_live_mode_never_claims_live_without_complete_observations(self):
        payload = request()
        payload["evidence_snapshot"][0]["source_state"] = "LIVE"
        with patch.dict(os.environ, {"ADAPTER_MODE": "live", "LEDGER_PATH": str(self.ledger)}, clear=True):
            response, _ = evaluate(payload)
        self.assertEqual(response["source_state"], "OFFLINE")

    def test_secret_fields_are_rejected(self):
        payload = request()
        payload["token"] = "forbidden"
        with self.assertRaises(ContractError):
            validate_request(payload)

    def test_digest_excludes_approval_and_is_stable(self):
        payload = request()
        expected = payload["approval"]["operation_digest"]
        self.assertEqual(canonical_operation_digest(payload), expected)
        changed = copy.deepcopy(payload)
        changed["approval"]["approved_by"] = "another-human"
        self.assertEqual(canonical_operation_digest(changed), expected)

    def test_metrics_are_counts_only(self):
        text = metrics_text()
        self.assertIn("decisions_total", text)
        for forbidden in ("latency", "utilization", "throughput"):
            self.assertNotIn(forbidden, text.lower())


if __name__ == "__main__":
    unittest.main()
