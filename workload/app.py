from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REQUEST_VERSION = "demo-story.redhat-intel.com/virtualization-ai-401/operation-request/v1"
RESPONSE_VERSION = "demo-story.redhat-intel.com/virtualization-ai-401/operation-response/v1"
EVIDENCE_VERSION = "demo-story.redhat-intel.com/virtualization-ai-401/evidence/v1"
POLICY = json.loads((Path(__file__).parents[1] / "contracts/governance-policy.json").read_text())
REQUEST_FIELDS = {"schema_version", "request_id", "operation", "target", "requested_by", "evidence_snapshot", "preflight", "approval", "observed_result"}
FORBIDDEN_KEYS = {"api_key", "apikey", "password", "secret", "token", "authorization", "bearer"}
JOURNEY = ("OBSERVE", "PREFLIGHT", "PROPOSE", "APPROVE", "EXECUTE", "VALIDATE", "LEARN")
COUNTERS: Counter[str] = Counter()
LOCK = threading.Lock()


class ContractError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_sha256(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def canonical_operation_digest(payload: dict) -> str:
    approved = dict(payload)
    approved.pop("approval", None)
    return canonical_sha256(approved)


def contains_forbidden_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in FORBIDDEN_KEYS or contains_forbidden_key(item) for key, item in value.items())
    return isinstance(value, list) and any(contains_forbidden_key(item) for item in value)


def validate_request(payload: object) -> dict:
    if not isinstance(payload, dict) or set(payload) != REQUEST_FIELDS:
        raise ContractError("request fields do not match the operation-request/v1 contract")
    if contains_forbidden_key(payload):
        raise ContractError("secret-bearing fields are forbidden")
    if payload.get("schema_version") != REQUEST_VERSION:
        raise ContractError("unsupported request schema")
    if payload.get("operation") not in {"LIVE_MIGRATE", "VALIDATE_RECOVERY", "RESTORE_REVIEW"}:
        raise ContractError("unsupported operation")
    if not isinstance(payload.get("request_id"), str) or len(payload["request_id"]) < 8:
        raise ContractError("request_id is invalid")
    target = payload.get("target")
    if not isinstance(target, dict) or set(target) != {"namespace", "virtual_machine"} or not all(target.values()):
        raise ContractError("target identity is incomplete")
    preflight = payload.get("preflight")
    expected = {"identity_match", "network_compatible", "storage_compatible", "evidence_fresh", "correlation_complete"}
    if not isinstance(preflight, dict) or set(preflight) != expected or not all(isinstance(value, bool) for value in preflight.values()):
        raise ContractError("preflight observations are incomplete")
    if not isinstance(payload.get("evidence_snapshot"), list) or not payload["evidence_snapshot"]:
        raise ContractError("evidence_snapshot is required")
    evidence_fields = {"schema_version", "evidence_id", "request_id", "state", "kind", "source", "source_state", "observed_at", "freshness", "digest", "payload"}
    for item in payload["evidence_snapshot"]:
        if not isinstance(item, dict) or set(item) != evidence_fields:
            raise ContractError("evidence_snapshot record is malformed")
        if item["source_state"] not in {"LIVE", "REHEARSAL", "OFFLINE"} or item["freshness"] not in {"FRESH", "STALE", "UNKNOWN"}:
            raise ContractError("evidence_snapshot labels are invalid")
    approval = payload.get("approval")
    if approval is not None and (not isinstance(approval, dict) or set(approval) != {"approved_by", "expires_at", "operation_digest"}):
        raise ContractError("approval is malformed")
    observed = payload.get("observed_result")
    result_fields = {"operation_complete", "infrastructure_success", "application_healthy", "ai_dependency_healthy", "correlation_continuity"}
    if observed is not None and (not isinstance(observed, dict) or set(observed) != result_fields or not all(isinstance(value, bool) for value in observed.values())):
        raise ContractError("observed_result is malformed")
    return payload


def ledger_path() -> Path:
    return Path(os.getenv("LEDGER_PATH", "/tmp/virtualization-ai-401-evidence.jsonl"))


def load_ledger(path: Path | None = None) -> list[dict]:
    selected = path or ledger_path()
    if not selected.exists():
        return []
    return [json.loads(line) for line in selected.read_text().splitlines() if line.strip()]


def append_records(records: list[dict]) -> None:
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with LOCK:
        with path.open("a", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            stream.flush()
            os.fsync(stream.fileno())


def source_state(payload: dict) -> str:
    mode = os.getenv("ADAPTER_MODE", "rehearsal").lower()
    if mode == "rehearsal":
        return "REHEARSAL"
    if mode != "live":
        return "OFFLINE"
    required = {"CLUSTER", "KUBEVIRT", "WORKLOAD", "OPERATION", "APPLICATION"}
    kinds = {item.get("kind") for item in payload["evidence_snapshot"] if item.get("source_state") == "LIVE" and item.get("freshness") == "FRESH"}
    return "LIVE" if required.issubset(kinds) else "OFFLINE"


def preflight_decision(payload: dict) -> tuple[str, list[str], str]:
    preflight = dict(payload["preflight"])
    if any(item["freshness"] != "FRESH" for item in payload["evidence_snapshot"]):
        preflight["evidence_fresh"] = False
    if any(item["request_id"] != payload["request_id"] for item in payload["evidence_snapshot"]):
        preflight["correlation_complete"] = False
    ordered = (
        ("identity_match", "IDENTITY_MISMATCH", "REFUSE", "refuse-identity-mismatch"),
        ("network_compatible", "NETWORK_INCOMPATIBLE", "REFUSE", "refuse-network-incompatible"),
        ("storage_compatible", "STORAGE_INCOMPATIBLE", "REFUSE", "refuse-storage-incompatible"),
        ("evidence_fresh", "EVIDENCE_STALE", "ABSTAIN", "abstain-stale-evidence"),
        ("correlation_complete", "CORRELATION_INCOMPLETE", "ABSTAIN", "abstain-correlation-incomplete"),
    )
    for field, reason, decision, rule in ordered:
        if preflight[field] is False:
            return decision, [reason], rule
    return "ALLOW_REVIEW", ["PREFLIGHT_COMPLETE"], "allow-human-review"


def approval_decision(payload: dict) -> tuple[str, list[str], str] | None:
    approval = payload["approval"]
    if approval is None:
        return "ALLOW_REVIEW", ["HUMAN_APPROVAL_REQUIRED"], "allow-human-review"
    if approval["operation_digest"] != canonical_operation_digest(payload):
        return "REFUSE", ["APPROVAL_DIGEST_MISMATCH"], "refuse-approval-digest-mismatch"
    try:
        expires = datetime.fromisoformat(approval["expires_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ContractError("approval expiry is invalid") from exc
    if expires <= datetime.now(timezone.utc):
        return "REFUSE", ["APPROVAL_EXPIRED"], "refuse-approval-expired"
    return None


def validation_decision(observed: dict | None) -> tuple[str, list[str], str, dict]:
    checks = {"status": "NOT_RUN", "infrastructure": "NOT_RUN", "application": "NOT_RUN", "ai_dependency": "NOT_RUN", "correlation": "NOT_RUN"}
    if observed is None or not observed["operation_complete"]:
        return "ABSTAIN", ["OPERATION_RESULT_INCOMPLETE"], "abstain-operation-incomplete", checks
    checks.update({
        "infrastructure": "PASS" if observed["infrastructure_success"] else "FAIL",
        "application": "PASS" if observed["application_healthy"] else "FAIL",
        "ai_dependency": "PASS" if observed["ai_dependency_healthy"] else "FAIL",
        "correlation": "PASS" if observed["correlation_continuity"] else "FAIL",
    })
    if not observed["infrastructure_success"]:
        checks["status"] = "FAIL"
        return "REFUSE", ["INFRASTRUCTURE_OPERATION_FAILED"], "refuse-infrastructure-failure", checks
    if not observed["application_healthy"]:
        checks["status"] = "FAIL"
        return "REFUSE", ["APPLICATION_FAILED_AFTER_INFRA_SUCCESS"], "refuse-application-failure", checks
    if not observed["correlation_continuity"]:
        checks["status"] = "INCOMPLETE"
        return "ABSTAIN", ["VALIDATION_CORRELATION_INCOMPLETE"], "abstain-validation-correlation", checks
    if not observed["ai_dependency_healthy"]:
        checks["status"] = "INCOMPLETE"
        return "ABSTAIN", ["AI_DEPENDENCY_UNAVAILABLE"], "abstain-ai-dependency", checks
    checks["status"] = "PASS"
    return "ALLOW_REVIEW", ["VALIDATION_COMPLETE"], "allow-validated-review", checks


def optional_explanation(payload: dict, state: str, decision: str, reasons: list[str]) -> tuple[dict | None, bool]:
    config = {name: os.getenv(name, "") for name in ("EXPLANATION_ENDPOINT", "MODEL_ID", "MODEL_PROVIDER", "MODEL_API_KEY")}
    if state != "LIVE" or not all(config.values()):
        return None, False
    body = json.dumps({"model": config["MODEL_ID"], "messages": [
        {"role": "system", "content": "Explain the supplied governed outcome in one sentence. Do not recommend or execute actions."},
        {"role": "user", "content": json.dumps({"request_id": payload["request_id"], "decision": decision, "reason_codes": reasons})},
    ], "temperature": 0}).encode()
    request = Request(config["EXPLANATION_ENDPOINT"], body, {"Authorization": "Bearer " + config["MODEL_API_KEY"], "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=5) as result:
            text = json.loads(result.read())["choices"][0]["message"]["content"]
        explanation = {"text": text[:500], "model_id": config["MODEL_ID"], "provider": config["MODEL_PROVIDER"]} if isinstance(text, str) and text else None
        return explanation, bool(explanation)
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
        return None, False


def make_records(payload: dict, states: tuple[str, ...], state: str, decision: str, reasons: list[str], validation: dict) -> list[dict]:
    now = utc_now()
    records = []
    for journey_state in states:
        detail = {"decision": decision, "reason_codes": reasons}
        if journey_state == "VALIDATE":
            detail["validation"] = validation
        if journey_state == "EXECUTE":
            detail["execution"] = "REHEARSAL_OBSERVATION" if state == "REHEARSAL" else "EXTERNAL_OPERATION_OBSERVED"
        base = {"schema_version": EVIDENCE_VERSION, "evidence_id": str(uuid.uuid4()), "request_id": payload["request_id"], "state": journey_state, "kind": "VALIDATION" if journey_state == "VALIDATE" else "OPERATION" if journey_state == "EXECUTE" else "DECISION", "source": "operations-adapter", "source_state": state, "observed_at": now, "freshness": "FRESH" if state != "OFFLINE" else "UNKNOWN", "payload": detail}
        base["digest"] = canonical_sha256(base)
        records.append(base)
    return records


def evaluate(value: object) -> tuple[dict, list[dict]]:
    payload = validate_request(value)
    state = source_state(payload)
    decision, reasons, rule = preflight_decision(payload)
    validation = {"status": "NOT_RUN", "infrastructure": "NOT_RUN", "application": "NOT_RUN", "ai_dependency": "NOT_RUN", "correlation": "NOT_RUN"}
    states = JOURNEY[:3]
    if decision == "ALLOW_REVIEW":
        approval = approval_decision(payload)
        if approval is not None:
            decision, reasons, rule = approval
            states = JOURNEY[:3] if payload["approval"] is None else JOURNEY[:4]
        else:
            decision, reasons, rule, validation = validation_decision(payload["observed_result"])
            states = JOURNEY
    records = make_records(payload, states, state, decision, reasons, validation)
    append_records(records)
    explanation, ai_participated = optional_explanation(payload, state, decision, reasons)
    response = {"schema_version": RESPONSE_VERSION, "request_id": payload["request_id"], "decision": decision, "source_state": state, "reason_codes": reasons, "policy": {"id": POLICY["policy_id"], "version": POLICY["version"], "matched_rules": [rule]}, "authority": {"human_review_required": True, "automated_action_performed": False, "llm_authority": "NONE"}, "evidence": records, "validation": validation, "ai_participated": ai_participated, "explanation": explanation}
    with LOCK:
        COUNTERS[decision] += 1
        COUNTERS["ledger_records"] += len(records)
    return response, records


def metrics_text() -> str:
    with LOCK:
        counts = dict(COUNTERS)
    lines = ["# HELP virtualization_ai_401_decisions_total Governed decision counts.", "# TYPE virtualization_ai_401_decisions_total counter"]
    for decision in ("ALLOW_REVIEW", "REFUSE", "ABSTAIN"):
        lines.append(f'virtualization_ai_401_decisions_total{{decision="{decision}"}} {counts.get(decision, 0)}')
    lines.extend(["# HELP virtualization_ai_401_ledger_records_total Durable evidence records written.", "# TYPE virtualization_ai_401_ledger_records_total counter", f"virtualization_ai_401_ledger_records_total {counts.get('ledger_records', 0)}", ""])
    return "\n".join(lines)


class Handler(BaseHTTPRequestHandler):
    server_version = "virtualization-ai-401/1"

    def send_json(self, status: int, value: object) -> None:
        encoded = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self.send_json(200, {"status": "ok", "mode": os.getenv("ADAPTER_MODE", "rehearsal").upper(), "ledger": str(ledger_path()), "authority": "HUMAN_REVIEW_REQUIRED"})
        elif self.path == "/metrics":
            encoded = metrics_text().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        elif self.path.startswith("/api/v1/operations/"):
            request_id = self.path.rsplit("/", 1)[-1]
            records = [record for record in load_ledger() if record.get("request_id") == request_id]
            self.send_json(200 if records else 404, {"request_id": request_id, "evidence": records} if records else {"error": "request not found"})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/v1/operations":
            self.send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise ContractError("request body length is invalid")
            response, _ = evaluate(json.loads(self.rfile.read(length)))
            self.send_json(200, response)
        except (ContractError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc), "decision": "REFUSE"})

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("ADAPTER_PORT", "8080"))), Handler).serve_forever()


if __name__ == "__main__":
    main()
