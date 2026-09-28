import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, RefResolver
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def load_json(relative: str):
    return json.loads((CONTRACTS / relative).read_text())


class GovernanceContractTests(unittest.TestCase):
    def validate(self, schema: str, example: str):
        evidence = load_json("evidence-record.schema.json")
        resolver = RefResolver((CONTRACTS / schema).as_uri(), load_json(schema), store={evidence["$id"]: evidence, "evidence-record.schema.json": evidence})
        validator = Draft202012Validator(load_json(schema), format_checker=FormatChecker(), resolver=resolver)
        errors = sorted(validator.iter_errors(load_json(example)), key=lambda error: list(error.path))
        self.assertEqual(errors, [], "\n".join(error.message for error in errors))

    def test_examples_satisfy_401_schemas(self):
        for name in ("approved-migration-request.json", "dependency-outage-request.json", "application-failure-request.json"):
            self.validate("operation-request.schema.json", f"examples/{name}")
        for name in ("approved-migration-response.json", "dependency-outage-response.json", "application-failure-response.json"):
            self.validate("operation-response.schema.json", f"examples/{name}")
        self.validate("evidence-record.schema.json", "examples/approved-evidence.json")

    def test_policy_is_deterministic_and_nonremediating(self):
        policy = load_json("governance-policy.json")
        self.assertEqual([rule["priority"] for rule in policy["rules"]], sorted(rule["priority"] for rule in policy["rules"]))
        self.assertEqual({rule["decision"] for rule in policy["rules"]}, {"ALLOW_REVIEW", "REFUSE", "ABSTAIN"})
        self.assertFalse(policy["execution"]["automated_remediation"])
        self.assertFalse(policy["execution"]["llm_may_execute"])

    def test_examples_never_grant_automation_authority(self):
        for path in (CONTRACTS / "examples").glob("*-response.json"):
            response = json.loads(path.read_text())
            self.assertFalse(response["authority"]["automated_action_performed"])
            self.assertEqual(response["authority"]["llm_authority"], "NONE")

    def test_openapi_exposes_bounded_operations_only(self):
        spec = yaml.safe_load((CONTRACTS / "openapi.yaml").read_text())
        self.assertEqual(spec["openapi"], "3.1.0")
        self.assertEqual(set(spec["paths"]), {"/api/v1/operations", "/api/v1/operations/{request_id}", "/metrics", "/healthz"})


if __name__ == "__main__":
    unittest.main()
