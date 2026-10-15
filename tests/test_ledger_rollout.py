import subprocess
import unittest
from pathlib import Path

import yaml


class LedgerRolloutTests(unittest.TestCase):
    def test_single_writer_ledger_uses_non_overlapping_rollout(self):
        chart = Path(__file__).resolve().parents[1] / "charts/virtualization-ai-401"
        result = subprocess.run(["helm", "template", "cert", str(chart),
                                 "--set-string", "presentation.ingressDomain=apps.example.invalid"],
                                capture_output=True, text=True, check=True)
        resources = list(yaml.safe_load_all(result.stdout))
        adapter = next(item for item in resources if item and item.get("kind") == "Deployment"
                       and item["metadata"]["name"] == "virtualization-ai-401-operations-adapter")
        self.assertEqual(adapter["spec"]["replicas"], 1)
        self.assertEqual(adapter["spec"].get("strategy"), {"type": "Recreate"})
        ledger = next(item for item in resources if item and item.get("kind") == "PersistentVolumeClaim")
        self.assertEqual(ledger["spec"]["accessModes"], ["ReadWriteOnce"])
