import copy
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from workload.app import ContractError, evaluate, metrics_text, validate_request

ROOT = Path(__file__).resolve().parents[1]


def request():
    return json.loads((ROOT / "contracts/examples/allowed-request.json").read_text())


class WorkloadTests(unittest.TestCase):
    def test_complete_rehearsal_allows_review_without_ai_claim(self):
        response, evidence = evaluate(request())
        self.assertEqual(response["outcome"], "ALLOW_REVIEW")
        self.assertEqual(response["source_state"], "REHEARSAL")
        self.assertFalse(response["ai_participated"])
        self.assertEqual(response["evidence_id"], evidence["evidence_id"])

    def test_identity_mismatch_refuses_before_other_checks(self):
        payload = request()
        payload["observed"]["identity"]["vm_name"] = "different-vm"
        response, _ = evaluate(payload)
        self.assertEqual(response["outcome"], "REFUSE")
        self.assertEqual(response["reason_codes"], ["IDENTITY_MISMATCH"])
        self.assertEqual(response["checks"]["network"], "NOT_RUN")
        self.assertNotIn("advisory", response)

    def test_network_mismatch_refuses(self):
        payload = request()
        payload["observed"]["destination"]["service"] = "undeclared"
        response, _ = evaluate(payload)
        self.assertEqual((response["outcome"], response["reason_codes"]), ("REFUSE", ["NETWORK_MISMATCH"]))

    def test_missing_correlation_abstains(self):
        payload = request()
        payload["observed"]["observability"]["correlation_id"] = "30100000-0000-4000-8000-000000000999"
        response, _ = evaluate(payload)
        self.assertEqual((response["outcome"], response["reason_codes"]), ("ABSTAIN", ["OBSERVABILITY_INCOMPLETE"]))

    def test_missing_placement_abstains(self):
        payload = request()
        payload["observed"]["placement"].pop("node_name")
        response, _ = evaluate(payload)
        self.assertEqual((response["outcome"], response["reason_codes"]), ("ABSTAIN", ["PLACEMENT_UNKNOWN"]))

    def test_wrong_placement_refuses(self):
        payload = request()
        payload["observed"]["placement"]["architecture"] = "arm64"
        response, _ = evaluate(payload)
        self.assertEqual((response["outcome"], response["reason_codes"]), ("REFUSE", ["PLACEMENT_MISMATCH"]))

    def test_model_unavailable_abstains(self):
        response, _ = evaluate(request(), "model-unavailable")
        self.assertEqual((response["outcome"], response["reason_codes"]), ("ABSTAIN", ["MODEL_UNAVAILABLE"]))
        self.assertNotIn("advisory", response)

    def test_live_without_identity_abstains(self):
        with patch.dict(os.environ, {"ADAPTER_MODE": "live"}, clear=True):
            response, _ = evaluate(request())
        self.assertEqual(response["source_state"], "OFFLINE")
        self.assertFalse(response["ai_participated"])

    def test_secret_field_is_rejected(self):
        payload = request()
        payload["observed"]["token"] = "forbidden"
        with self.assertRaises(ContractError):
            validate_request(payload)

    def test_metrics_are_counts_not_performance_claims(self):
        text = metrics_text()
        self.assertIn("decisions_total", text)
        self.assertNotIn("latency", text.lower())


if __name__ == "__main__":
    unittest.main()
