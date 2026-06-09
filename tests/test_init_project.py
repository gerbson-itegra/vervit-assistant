import json
import tempfile
import unittest
from pathlib import Path

from scripts.init_project import initialize_project


class InitProjectTests(unittest.TestCase):
    def test_creates_vervit_workflow_configuration_and_release_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            results = initialize_project(root)

            config_path = root / ".agents" / "vervit-assistant.json"
            release_path = root / ".specs" / "releases" / "NEXT" / "RELEASE.md"
            self.assertEqual(results[".agents/vervit-assistant.json"], "written")
            self.assertTrue(config_path.exists())
            self.assertTrue(release_path.exists())
            config = json.loads(config_path.read_text(encoding="utf-8"))
            serialized = json.dumps(config)
            self.assertNotIn("secret-token", serialized)
            self.assertEqual(config["git"]["mainBranch"], "main")
            self.assertEqual(config["git"]["releaseBranch"], "release")
            self.assertEqual(config["jira"]["apiTokenEnv"], "JIRA_API_TOKEN")


if __name__ == "__main__":
    unittest.main()
