import unittest
import tempfile
from pathlib import Path

from scripts.jira_executor import (
    JiraExecutor,
    JiraExecutorError,
    checklist_complete,
    create_operation_plan,
    update_managed_checklist,
)


class FakeTransport:
    def __init__(self):
        self.calls = []

    def __call__(self, method, url, headers, payload):
        self.calls.append((method, url, payload))
        if method == "POST" and url.endswith("/rest/api/3/version"):
            return {"id": "9001", "name": payload["name"]}
        return {"ok": True}


class JiraChecklistTests(unittest.TestCase):
    def test_preserves_original_text_description(self):
        original = "Descricao original importante."

        updated = update_managed_checklist(original, ["Validar login", "Validar logout"])

        self.assertIn(original, updated)
        self.assertIn("- [ ] Validar login", updated)
        self.assertFalse(checklist_complete(updated))
        self.assertTrue(checklist_complete(updated.replace("[ ]", "[x]")))

    def test_preserves_original_adf_nodes_and_completed_states(self):
        original = {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Original"}]},
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "[[VERVIT-CHECKLIST-START]]"}],
                },
                {
                    "type": "taskList",
                    "attrs": {"localId": "old"},
                    "content": [
                        {
                            "type": "taskItem",
                            "attrs": {"localId": "item", "state": "DONE"},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Validar login"}],
                                }
                            ],
                        }
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "[[VERVIT-CHECKLIST-END]]"}],
                },
            ],
        }

        updated = update_managed_checklist(original, ["Validar login", "Validar logout"])

        self.assertEqual(updated["content"][0], original["content"][0])
        task_items = next(
            node["content"] for node in updated["content"] if node["type"] == "taskList"
        )
        self.assertEqual(task_items[0]["attrs"]["state"], "DONE")
        self.assertEqual(task_items[1]["attrs"]["state"], "TODO")


class JiraExecutorTests(unittest.TestCase):
    def test_from_env_loads_project_local_vervit_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.vervit.local").write_text(
                "JIRA_BASE_URL=https://example.atlassian.net\n"
                "JIRA_EMAIL=user@example.com\n"
                "JIRA_API_TOKEN=secret\n",
                encoding="utf-8",
            )

            executor = JiraExecutor.from_env(root=root, env={})

            self.assertEqual(executor.base_url, "https://example.atlassian.net")
    def setUp(self):
        self.transport = FakeTransport()
        self.executor = JiraExecutor(
            "https://example.atlassian.net",
            "dev@example.com",
            "secret-token",
            transport=self.transport,
        )

    def test_sensitive_operation_requires_matching_confirmation_hash(self):
        plan = self.executor.create_plan(
            "create_version", {"project": 10000, "name": "1.5.0"}
        )

        with self.assertRaises(JiraExecutorError):
            self.executor.execute_plan(plan)

        result = self.executor.execute_plan(plan, confirmation_hash=plan["hash"])
        self.assertEqual(result["name"], "1.5.0")

    def test_can_create_sensitive_plan_without_jira_credentials(self):
        plan = create_operation_plan(
            "create_version", {"project": 10000, "name": "1.5.0"}
        )

        self.assertTrue(plan["sensitive"])
        self.assertEqual(len(plan["hash"]), 64)

    def test_create_apply_and_release_version_use_rest_v3(self):
        create = self.executor.create_plan(
            "create_version", {"project": 10000, "name": "1.5.0"}
        )
        apply = self.executor.create_plan(
            "apply_fix_version", {"issueKey": "ABC-1", "versionId": "9001"}
        )
        release = self.executor.create_plan(
            "release_version", {"versionId": "9001", "releaseDate": "2026-06-09"}
        )

        for plan in (create, apply, release):
            self.executor.execute_plan(plan, confirmation_hash=plan["hash"])

        self.assertEqual(
            [(method, url.rsplit("/", 1)[-1]) for method, url, _ in self.transport.calls],
            [("POST", "version"), ("PUT", "ABC-1"), ("PUT", "9001")],
        )
        self.assertEqual(
            self.transport.calls[1][2]["update"]["fixVersions"], [{"add": {"id": "9001"}}]
        )
        self.assertTrue(self.transport.calls[2][2]["released"])


if __name__ == "__main__":
    unittest.main()
