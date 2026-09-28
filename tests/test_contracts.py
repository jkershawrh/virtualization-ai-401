import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def load_json(relative: str):
    return json.loads((CONTRACTS / relative).read_text())


class GovernanceContractTests(unittest.TestCase):
    def validate(self, schema: str, example: str):
        validator = Draft202012Validator(load_json(schema), format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(load_json(example)), key=lambda error: list(error.path))
        self.assertEqual(errors, [], "\n".join(error.message for error in errors))

    def test_examples_satisfy_versioned_schemas(self):
        self.validate("modernization-request.schema.json", "examples/allowed-request.json")
        for name in ("allowed-response.json", "identity-refused-response.json", "placement-unknown-response.json", "model-unavailable-response.json"):
            self.validate("modernization-response.schema.json", f"examples/{name}")
        self.validate("evidence-record.schema.json", "examples/allowed-evidence.json")

    def test_failure_precedence_is_explicit(self):
        policy = load_json("governance-policy.json")
        self.assertEqual(policy["precedence"], ["IDENTITY", "NETWORK", "OBSERVABILITY", "PLACEMENT", "MODEL"])
        self.assertEqual(policy["outcomes"]["IDENTITY_MISMATCH"], "REFUSE")
        self.assertEqual(policy["outcomes"]["NETWORK_MISMATCH"], "REFUSE")
        self.assertEqual(policy["outcomes"]["PLACEMENT_UNKNOWN"], "ABSTAIN")
        self.assertEqual(policy["outcomes"]["MODEL_UNAVAILABLE"], "ABSTAIN")

    def test_refused_and_abstained_examples_have_no_advisory_or_ai_claim(self):
        for name in ("identity-refused-response.json", "placement-unknown-response.json", "model-unavailable-response.json"):
            response = load_json(f"examples/{name}")
            self.assertNotIn("advisory", response)
            self.assertFalse(response["ai_participated"])
            self.assertEqual(response["authority"], "HUMAN_REVIEW_REQUIRED")

    def test_request_has_no_secret_values(self):
        request = load_json("examples/allowed-request.json")
        lowered = json.dumps(request).lower()
        for forbidden in ("api_key", "password", "bearer", "secret_value"):
            self.assertNotIn(forbidden, lowered)

    def test_openapi_exposes_only_bounded_paths(self):
        spec = yaml.safe_load((CONTRACTS / "openapi.yaml").read_text())
        self.assertEqual(spec["openapi"], "3.1.0")
        self.assertEqual(set(spec["paths"]), {"/api/v1/modernize", "/api/v1/evidence/{evidence_id}", "/metrics", "/healthz"})


if __name__ == "__main__":
    unittest.main()
