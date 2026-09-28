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

REQUEST_VERSION = "virtualization-ai.redhat-intel.com/modernization-request/v1"
RESPONSE_VERSION = "virtualization-ai.redhat-intel.com/modernization-response/v1"
EVIDENCE_VERSION = "virtualization-ai.redhat-intel.com/evidence-record/v1"
ALLOWED_CATEGORIES = {"identity", "connectivity", "placement", "operations", "unknown"}
FORBIDDEN_KEYS = {"api_key", "apikey", "password", "secret", "token", "authorization"}
POLICY = json.loads((Path(__file__).parents[1] / "contracts/governance-policy.json").read_text())
EVIDENCE: dict[str, dict] = {}
COUNTERS: Counter[str] = Counter()
LOCK = threading.Lock()


class ContractError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def contains_forbidden_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in FORBIDDEN_KEYS or contains_forbidden_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_forbidden_key(item) for item in value)
    return False


def validate_request(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ContractError("request must be a JSON object")
    expected = {"schema_version", "correlation_id", "task", "note", "allowed_categories", "declared", "observed"}
    if set(payload) != expected:
        raise ContractError("request fields do not match the v1 contract")
    if contains_forbidden_key(payload):
        raise ContractError("secret-bearing fields are forbidden")
    if payload["schema_version"] != REQUEST_VERSION or payload["task"] != "review-vm-modernization":
        raise ContractError("unsupported contract version or task")
    try:
        uuid.UUID(str(payload["correlation_id"]))
    except ValueError as exc:
        raise ContractError("correlation_id must be a UUID") from exc
    if not isinstance(payload["note"], str) or not 0 < len(payload["note"]) <= 1000:
        raise ContractError("note must contain 1 to 1000 characters")
    if set(payload["allowed_categories"]) != ALLOWED_CATEGORIES or len(payload["allowed_categories"]) != 5:
        raise ContractError("allowed_categories must contain the complete v1 enumeration")
    for section in ("declared", "observed"):
        if not isinstance(payload[section], dict):
            raise ContractError(f"{section} must be an object")
    return payload


def configuration() -> dict[str, str]:
    return {
        "mode": os.getenv("ADAPTER_MODE", "rehearsal").lower(),
        "endpoint": os.getenv("MODEL_ENDPOINT", ""),
        "model": os.getenv("MODEL_ID", ""),
        "provider": os.getenv("MODEL_PROVIDER", ""),
        "hardware": os.getenv("MODEL_HARDWARE", ""),
        "api_key": os.getenv("MODEL_API_KEY", ""),
    }


def compare_controls(payload: dict) -> tuple[str, list[str], dict[str, str]]:
    declared, observed = payload["declared"], payload["observed"]
    checks = {name.lower(): "NOT_RUN" for name in POLICY["precedence"]}
    identity_fields = ("namespace", "vm_name", "service_account")
    if any(declared["identity"].get(key) != observed["identity"].get(key) for key in identity_fields) or not observed["identity"].get("vmi_uid"):
        checks["identity"] = "FAIL"
        return "REFUSE", ["IDENTITY_MISMATCH"], checks
    checks["identity"] = "PASS"

    destination_match = all(declared["destination"].get(key) == observed["destination"].get(key) for key in ("service", "port"))
    if not destination_match or observed["destination"].get("network_policy") != "ENFORCED" or not observed["destination"].get("endpoints_ready"):
        checks["network"] = "FAIL"
        return "REFUSE", ["NETWORK_MISMATCH"], checks
    checks["network"] = "PASS"

    observation = observed.get("observability", {})
    if observation.get("correlation_id") != payload["correlation_id"] or not observation.get("collected_at") or not observation.get("events_available"):
        checks["observability"] = "UNKNOWN"
        return "ABSTAIN", ["OBSERVABILITY_INCOMPLETE"], checks
    checks["observability"] = "PASS"

    wanted, found = declared["placement"], observed.get("placement", {})
    if not found.get("node_name") or found.get("architecture") in (None, "unknown") or not isinstance(found.get("labels"), dict):
        checks["placement"] = "UNKNOWN"
        return "ABSTAIN", ["PLACEMENT_UNKNOWN"], checks
    labels_match = all(found["labels"].get(key) == value for key, value in wanted.get("required_labels", {}).items())
    if found.get("architecture") != wanted.get("architecture") or not labels_match:
        checks["placement"] = "FAIL"
        return "REFUSE", ["PLACEMENT_MISMATCH"], checks
    checks["placement"] = "PASS"
    return "ALLOW_REVIEW", ["CONTROLS_COMPLETE"], checks


def rehearsal_advisory() -> dict[str, str]:
    return {
        "category": "operations",
        "summary": "Deterministic rehearsal summary; no live model participated.",
        "rationale": "All supplied representative control observations matched the declared policy.",
    }


def call_live_model(payload: dict, config: dict[str, str]) -> dict[str, str]:
    missing = [key for key in ("endpoint", "model", "provider", "hardware", "api_key") if not config[key]]
    if missing:
        raise ContractError("live model identity is incomplete")
    body = json.dumps({
        "model": config["model"],
        "messages": [
            {"role": "system", "content": "Return one JSON object with category, summary, and rationale. Never propose or execute actions."},
            {"role": "user", "content": json.dumps({"note": payload["note"], "allowed_categories": payload["allowed_categories"]})},
        ],
        "temperature": 0,
    }).encode()
    request = Request(config["endpoint"], body, {"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=8) as result:
        content = json.loads(result.read())["choices"][0]["message"]["content"]
    advisory = json.loads(content)
    if set(advisory) != {"category", "summary", "rationale"} or advisory["category"] not in ALLOWED_CATEGORIES:
        raise ContractError("model output is outside the response contract")
    if not all(isinstance(advisory[key], str) and advisory[key] for key in advisory):
        raise ContractError("model output contains an empty or non-string value")
    return advisory


def evaluate(payload: object, condition: str = "healthy") -> tuple[dict, dict]:
    request_payload = validate_request(payload)
    outcome, reasons, checks = compare_controls(request_payload)
    config = configuration()
    source_state = "OFFLINE" if config["mode"] == "offline" else "REHEARSAL"
    ai_participated = False
    advisory = None
    model = None

    if condition == "model-unavailable" and outcome == "ALLOW_REVIEW":
        outcome, reasons, checks["model"] = "ABSTAIN", ["MODEL_UNAVAILABLE"], "FAIL"
        source_state = "OFFLINE"
    elif outcome == "ALLOW_REVIEW" and config["mode"] == "live":
        try:
            advisory = call_live_model(request_payload, config)
            model = {"id": config["model"], "provider": config["provider"], "hardware": config["hardware"]}
            checks["model"] = "PASS"
            source_state, ai_participated = "LIVE", True
        except (ContractError, HTTPError, URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
            outcome, reasons, checks["model"] = "ABSTAIN", ["MODEL_UNAVAILABLE"], "FAIL"
            source_state = "OFFLINE"
    elif outcome == "ALLOW_REVIEW" and config["mode"] == "offline":
        outcome, reasons, checks["model"] = "ABSTAIN", ["MODEL_UNAVAILABLE"], "FAIL"
    elif outcome == "ALLOW_REVIEW":
        advisory = rehearsal_advisory()
        model = {"id": "rehearsal-fixture", "provider": "fixture", "hardware": "not-observed"}
        checks["model"] = "NOT_RUN"

    evidence_id = str(uuid.uuid4())
    response = {
        "schema_version": RESPONSE_VERSION,
        "correlation_id": request_payload["correlation_id"],
        "outcome": outcome,
        "source_state": source_state,
        "ai_participated": ai_participated,
        "reason_codes": reasons,
        "checks": checks,
        "authority": "HUMAN_REVIEW_REQUIRED",
        "evidence_id": evidence_id,
    }
    if advisory is not None:
        response["advisory"], response["model"] = advisory, model
    evidence = {
        "schema_version": EVIDENCE_VERSION,
        "evidence_id": evidence_id,
        "correlation_id": request_payload["correlation_id"],
        "request_sha256": canonical_sha256(request_payload),
        "source_state": source_state,
        "outcome": outcome,
        "reason_codes": reasons,
        "checks": checks,
        "ai_participated": ai_participated,
        "authority": "HUMAN_REVIEW_REQUIRED",
        "created_at": utc_now(),
    }
    with LOCK:
        EVIDENCE[evidence_id] = evidence
        COUNTERS[outcome] += 1
    return response, evidence


def metrics_text() -> str:
    with LOCK:
        counts = dict(COUNTERS)
    lines = ["# HELP virtualization_ai_301_decisions_total In-process governed decision counts.", "# TYPE virtualization_ai_301_decisions_total counter"]
    for outcome in ("ALLOW_REVIEW", "REFUSE", "ABSTAIN"):
        lines.append(f'virtualization_ai_301_decisions_total{{outcome="{outcome}"}} {counts.get(outcome, 0)}')
    lines.append("")
    return "\n".join(lines)


class Handler(BaseHTTPRequestHandler):
    server_version = "virtualization-ai-301/1"

    def send_json(self, status: int, value: object) -> None:
        encoded = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            config = configuration()
            self.send_json(200, {"status": "ok", "mode": config["mode"].upper(), "live_identity_complete": all(config[key] for key in ("endpoint", "model", "provider", "hardware", "api_key")), "authority": "HUMAN_REVIEW_REQUIRED"})
        elif self.path == "/metrics":
            encoded = metrics_text().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        elif self.path.startswith("/api/v1/evidence/"):
            evidence_id = self.path.rsplit("/", 1)[-1]
            with LOCK:
                evidence = EVIDENCE.get(evidence_id)
            self.send_json(200 if evidence else 404, evidence or {"error": "evidence not found"})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/api/v1/modernize"):
            self.send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 32768:
                raise ContractError("request body length is invalid")
            payload = json.loads(self.rfile.read(length))
            condition = "model-unavailable" if "condition=model-unavailable" in self.path else "healthy"
            response, _ = evaluate(payload, condition)
            self.send_json(200, response)
        except (ContractError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc), "outcome": "REFUSE"})

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("ADAPTER_PORT", "8080"))), Handler).serve_forever()


if __name__ == "__main__":
    main()
