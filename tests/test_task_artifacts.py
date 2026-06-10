import json
import tempfile
import unittest
from pathlib import Path

from scripts.task_artifacts import create_task_artifacts


class TaskArtifactsTests(unittest.TestCase):
    def test_creates_traceable_task_files_without_overwriting_existing_prd(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results = create_task_artifacts(
                root,
                issue_key="ABC-123",
                summary="Adicionar login social",
                task_type="feature",
                track="planned",
                branch="feature/ABC-123-adicionar-login-social",
            )
            prd = root / "docs" / "ABC-123_PRD.md"
            state = json.loads(
                (root / "docs" / "ABC-123_state.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(results["ABC-123_PRD.md"], "written")
            self.assertIn("Cenarios De Validacao Manual", prd.read_text(encoding="utf-8"))
            prd_content = prd.read_text(encoding="utf-8")
            self.assertLessEqual(len(prd_content.split()), 100)
            self.assertNotIn("Perguntas Abertas", prd_content)
            self.assertEqual(state["track"], "planned")
            prd.write_text("conteudo aprovado\n", encoding="utf-8")
            second = create_task_artifacts(
                root,
                issue_key="ABC-123",
                summary="Adicionar login social",
                task_type="feature",
                track="planned",
                branch="feature/ABC-123-adicionar-login-social",
            )
            self.assertEqual(second["ABC-123_PRD.md"], "unchanged")
            self.assertEqual(prd.read_text(encoding="utf-8"), "conteudo aprovado\n")


if __name__ == "__main__":
    unittest.main()
