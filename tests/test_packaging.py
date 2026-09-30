import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts/virtualization-ai-401"


class PackagingTests(unittest.TestCase):
    def test_chart_expresses_governance_without_secret_values(self):
        rendered = "\n".join(path.read_text() for path in (CHART / "templates").glob("*"))
        for term in ("NetworkPolicy", "nodeSelector", "serviceAccountName", "ServiceMonitor", "/metrics", "secretKeyRef", "PersistentVolumeClaim", "LEDGER_PATH"):
            self.assertIn(term, rendered)
        self.assertNotIn("kind: Secret", rendered)
        self.assertIn("automountServiceAccountToken: false", rendered)
        self.assertIn("podSelector: {}", rendered)

    def test_published_values_are_absent_or_exact_release_receipts(self):
        path = CHART / "values.published.yaml"
        if path.exists():
            import re, yaml
            values = yaml.safe_load(path.read_text())
            for component in ("operationsAdapter", "presentation"):
                self.assertRegex(values[component]["image"]["digest"], r"^sha256:[0-9a-f]{64}$")
            self.assertNotIn("TO_BE_FILLED", path.read_text())

    def test_openshift_security_and_route_contracts_are_portable(self):
        adapter = (CHART / "templates" / "adapter.yaml").read_text()
        presentation = (CHART / "templates" / "presentation.yaml").read_text()
        values = (CHART / "values.yaml").read_text()

        # OpenShift assigns a namespace-specific supplemental group. A fixed
        # fsGroup is rejected by the restricted SCC on destination clusters.
        self.assertNotIn("fsGroup: 65532", adapter)
        # Per-seat namespaces are long. Keep the first DNS label bounded and
        # provide the destination ingress domain as an explicit deployment value.
        self.assertIn("virtualization-ai-401.routeHost", presentation)
        self.assertIn("ingressDomain", values)


if __name__ == "__main__":
    unittest.main()
