import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    ROOT / "skills" / "vervit-assistant-main" / "SKILL.md",
    ROOT / "skills" / "vervit-especificar-tarefa" / "SKILL.md",
    ROOT / "skills" / "vervit-implementar-tarefa" / "SKILL.md",
    ROOT / "skills" / "vervit-init-project" / "SKILL.md",
    ROOT / "skills" / "vervit-update" / "SKILL.md",
]
WORD_LIMITS = {
    ROOT / "skills" / "vervit-assistant-main" / "SKILL.md": 145,
    ROOT / "skills" / "vervit-especificar-tarefa" / "SKILL.md": 105,
    ROOT / "skills" / "vervit-implementar-tarefa" / "SKILL.md": 110,
    ROOT / "skills" / "vervit-init-project" / "SKILL.md": 180,
    ROOT / "skills" / "vervit-map-codebase" / "SKILL.md": 80,
    ROOT / "skills" / "vervit-update" / "SKILL.md": 90,
    ROOT / "assets" / "templates" / "AGENTS.md": 90,
    ROOT / "assets" / "templates" / "agent-profile.md": 80,
    ROOT / "skills" / "vervit-assistant-main" / "references" / "task-workflow.md": 50,
    ROOT / "skills" / "vervit-assistant-main" / "references" / "jira-operations.md": 50,
    ROOT / "skills" / "vervit-assistant-main" / "references" / "provider-routing.md": 50,
    ROOT / "skills" / "vervit-assistant-main" / "references" / "releases.md": 50,
}


class SkillInteractionContractTests(unittest.TestCase):
    def test_user_questions_prefer_structured_interaction_with_text_fallback(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                content = skill.read_text(encoding="utf-8").lower()
                self.assertIn("request_user_input", content)
                self.assertIn("pergunta textual", content)

    def test_skills_do_not_store_open_questions_in_markdown(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                content = skill.read_text(encoding="utf-8").lower()
                self.assertNotIn("perguntas abertas", content)

    def test_frequent_skills_stay_within_token_budgets(self):
        for skill, limit in WORD_LIMITS.items():
            with self.subTest(skill=skill.name):
                words = len(skill.read_text(encoding="utf-8").split())
                self.assertLessEqual(words, limit)

    def test_main_routes_reads_on_demand_instead_of_loading_everything(self):
        content = SKILLS[0].read_text(encoding="utf-8").lower()

        self.assertIn("state.json", content)
        self.assertIn("sob demanda", content)
        self.assertNotIn("leia `agents.md`, `vervit-assistant/agent-profile.md`", content)
        self.assertNotIn("abra `docs/<key>/prd.md`, `trace.md` e `state.json`", content)

    def test_security_gates_survive_compaction(self):
        content = "\n".join(
            skill.read_text(encoding="utf-8").lower() for skill in SKILLS[:3]
        )

        for required in [
            "prd aprovado",
            "checklist manual",
            "testes",
            "confirmação explícita",
            "credenciais",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, content)

    def test_init_skill_guides_first_run_without_requesting_secret_in_chat(self):
        content = (
            ROOT / "skills" / "vervit-init-project" / "SKILL.md"
        ).read_text(encoding="utf-8").lower()

        self.assertIn(".env.vervit.local", content)
        self.assertIn("primeira execução", content)
        self.assertIn("ações", content)
        self.assertIn("nunca peça", content)


if __name__ == "__main__":
    unittest.main()
