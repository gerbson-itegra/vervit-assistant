import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DISPLAY_NAMES = {
    "vervit-assistant-main": "Vervit: Assistente Principal",
    "vervit-init-project": "Vervit: Inicializar Projeto",
    "vervit-map-codebase": "Vervit: Mapear Codebase",
    "vervit-especificar-tarefa": "Vervit: Especificar Tarefa",
    "vervit-implementar-tarefa": "Vervit: Implementar Tarefa",
}


def read_interface_value(metadata_path: Path, key: str) -> str:
    content = metadata_path.read_text(encoding="utf-8")
    match = re.search(rf'^\s{{2}}{re.escape(key)}:\s*"([^"]+)"\s*$', content, re.MULTILINE)
    if match is None:
        raise AssertionError(f"{metadata_path} does not define interface.{key}")
    return match.group(1)


class SkillDiscoveryTests(unittest.TestCase):
    def test_vervit_skills_have_distinct_searchable_display_names(self):
        display_names = []

        for skill_name, expected_display_name in SKILL_DISPLAY_NAMES.items():
            metadata_path = ROOT / "skills" / skill_name / "agents" / "openai.yaml"
            self.assertTrue(metadata_path.is_file(), metadata_path)
            display_name = read_interface_value(metadata_path, "display_name")
            short_description = read_interface_value(metadata_path, "short_description")

            self.assertEqual(display_name, expected_display_name)
            self.assertTrue(display_name.startswith("Vervit:"))
            self.assertTrue(short_description)
            display_names.append(display_name)

        self.assertEqual(len(display_names), len(set(display_names)))

    def test_marketplace_package_contains_skill_ui_metadata(self):
        for skill_name in SKILL_DISPLAY_NAMES:
            source = ROOT / "skills" / skill_name / "agents" / "openai.yaml"
            packaged = (
                ROOT
                / "plugins"
                / "vervit-assistant"
                / "skills"
                / skill_name
                / "agents"
                / "openai.yaml"
            )

            self.assertTrue(packaged.is_file(), packaged)
            self.assertEqual(packaged.read_bytes(), source.read_bytes())


if __name__ == "__main__":
    unittest.main()
