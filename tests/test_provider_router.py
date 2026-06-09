import unittest

from scripts.provider_router import (
    ProviderPayloadError,
    ProviderRouter,
    ProviderRouterError,
    sanitize_payload,
)


class ProviderRouterTests(unittest.TestCase):
    def test_uses_priority_and_falls_back_after_provider_failure(self):
        calls = []

        def adapter(provider, task, payload):
            calls.append(provider["id"])
            if provider["id"] == "first":
                raise ProviderRouterError("indisponivel")
            return {"text": "checkpoint formatado"}

        router = ProviderRouter(
            [
                {"id": "second", "adapter": "fake", "priority": 20, "enabled": True},
                {"id": "first", "adapter": "fake", "priority": 10, "enabled": True},
            ],
            adapters={"fake": adapter},
        )

        result = router.route("checkpoint-draft", {"facts": ["teste passou"]})

        self.assertEqual(calls, ["first", "second"])
        self.assertEqual(result["provider"], "second")

    def test_requires_consent_before_sending_jira_content(self):
        router = ProviderRouter(
            [{"id": "external", "adapter": "fake", "priority": 1, "enabled": True}],
            adapters={"fake": lambda provider, task, payload: {"text": "ok"}},
        )

        result = router.route(
            "issue-summary",
            {"issue": {"description": "privado"}},
            contains_jira_content=True,
        )

        self.assertEqual(result["status"], "fallback-required")

    def test_rejects_secret_bearing_payload(self):
        router = ProviderRouter([], adapters={})

        with self.assertRaises(ProviderPayloadError):
            router.route(
                "issue-summary",
                {"comments": ["Authorization: Bearer abcdefghijklmnopqrstuvwxyz"]},
            )

    def test_removes_secret_fields_case_insensitively(self):
        sanitized = sanitize_payload(
            {
                "description": "texto seguro",
                "APIToken": "nao-deve-sair",
                "attachments": [{"name": "contrato.pdf"}],
            }
        )

        self.assertEqual(sanitized, {"description": "texto seguro"})

    def test_disallows_analysis_or_implementation_tasks(self):
        router = ProviderRouter([], adapters={})

        with self.assertRaises(ProviderRouterError):
            router.route("implement-code", {"request": "corrija"})

    def test_suspends_provider_after_three_failures(self):
        now = [1000.0]
        attempts = []

        def failing(provider, task, payload):
            attempts.append(provider["id"])
            raise ProviderRouterError("falhou")

        router = ProviderRouter(
            [{"id": "unstable", "adapter": "fake", "priority": 1, "enabled": True}],
            adapters={"fake": failing},
            clock=lambda: now[0],
        )

        for _ in range(4):
            router.route("checkpoint-draft", {"facts": ["ok"]})

        self.assertEqual(attempts, ["unstable", "unstable", "unstable"])
        now[0] += 901
        router.route("checkpoint-draft", {"facts": ["ok"]})
        self.assertEqual(attempts[-1], "unstable")


if __name__ == "__main__":
    unittest.main()
