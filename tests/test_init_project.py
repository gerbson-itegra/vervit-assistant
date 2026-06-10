import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.init_project import (
    detect_atlassian,
    detect_superpowers,
    detect_tlc_spec_driven,
    initialize_project,
    load_vervit_env,
    sanitize_source,
    sync_skill_sources,
)


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def create_skill(root: Path, name: str) -> None:
    skill = root / "skills" / name / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text(f"---\nname: {name}\n---\n", encoding="utf-8")


class InitProjectTests(unittest.TestCase):
    def test_loads_local_vervit_env_without_overwriting_existing_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.vervit.local").write_text(
                "JIRA_BASE_URL=https://example.atlassian.net\n"
                "JIRA_EMAIL=local@example.com\n"
                "JIRA_API_TOKEN=local-secret\n",
                encoding="utf-8",
            )

            loaded = load_vervit_env(root, {"JIRA_EMAIL": "existing@example.com"})

            self.assertEqual(loaded["JIRA_BASE_URL"], "https://example.atlassian.net")
            self.assertEqual(loaded["JIRA_EMAIL"], "existing@example.com")
            self.assertEqual(loaded["JIRA_API_TOKEN"], "local-secret")

    def test_skill_source_credentials_are_not_recorded(self):
        sanitized = sanitize_source("https://token:secret@example.com/org/repo.git")

        self.assertEqual(sanitized, "https://example.com/org/repo.git")
        self.assertNotIn("token", sanitized)
        self.assertNotIn("secret", sanitized)

    def test_superpowers_is_ready_only_when_all_required_skills_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            required = [
                "brainstorming",
                "writing-plans",
                "systematic-debugging",
                "test-driven-development",
                "verification-before-completion",
            ]
            for name in required[:-1]:
                create_skill(root, name)

            incomplete = detect_superpowers(search_roots=[root])

            self.assertEqual(incomplete["status"], "incomplete")
            self.assertEqual(
                incomplete["missingSkills"], ["verification-before-completion"]
            )

            create_skill(root, required[-1])
            ready = detect_superpowers(search_roots=[root])

            self.assertEqual(ready["status"], "ready")
            self.assertEqual(ready["missingSkills"], [])
            self.assertEqual(set(ready["skills"]), set(required))

    def test_atlassian_status_reflects_only_environment_markers_and_rest_credentials(self):
        pending = detect_atlassian(env={})
        exposed = detect_atlassian(
            env={
                "ATLASSIAN_CLOUD_ID": "not-recorded",
                "JIRA_BASE_URL": "not-recorded",
                "JIRA_EMAIL": "not-recorded",
                "JIRA_API_TOKEN": "not-recorded",
            }
        )

        self.assertEqual(pending["connector"]["status"], "not_exposed")
        self.assertEqual(pending["rest"]["status"], "pending")
        self.assertEqual(exposed["connector"]["status"], "exposed")
        self.assertEqual(exposed["connector"]["environmentMarkers"], ["ATLASSIAN_CLOUD_ID"])
        self.assertEqual(exposed["rest"]["status"], "configured")
        self.assertNotIn("not-recorded", json.dumps(exposed))

    def test_tlc_detection_remains_optional(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pending = detect_tlc_spec_driven(search_roots=[root])
            create_skill(root, "tlc-spec-driven")
            available = detect_tlc_spec_driven(search_roots=[root])

            self.assertEqual(pending["status"], "pending")
            self.assertEqual(pending["mode"], "optional")
            self.assertEqual(available["status"], "available")
            self.assertEqual(available["mode"], "optional")

    def test_sync_skill_sources_clones_then_updates_from_original_git_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            git("init", "-b", "main", cwd=source)
            git("config", "user.email", "tests@example.com", cwd=source)
            git("config", "user.name", "Tests", cwd=source)
            create_skill(source, "brainstorming")
            git("add", ".", cwd=source)
            git("commit", "-m", "initial", cwd=source)
            codex_home = root / "codex"

            cloned = sync_skill_sources(
                {"superpowers": str(source)}, codex_home=codex_home
            )

            checkout = codex_home / "skills" / "sources" / "superpowers"
            self.assertEqual(cloned["superpowers"]["action"], "cloned")
            self.assertEqual(cloned["superpowers"]["source"], str(source))
            self.assertTrue((checkout / "skills" / "brainstorming" / "SKILL.md").exists())
            self.assertTrue(
                (codex_home / "skills" / "brainstorming" / "SKILL.md").exists()
            )

            create_skill(source, "writing-plans")
            git("add", ".", cwd=source)
            git("commit", "-m", "update", cwd=source)
            updated = sync_skill_sources(
                {"superpowers": str(source)}, codex_home=codex_home
            )

            self.assertEqual(updated["superpowers"]["action"], "updated")
            self.assertTrue((checkout / "skills" / "writing-plans" / "SKILL.md").exists())
            self.assertTrue(
                (codex_home / "skills" / "writing-plans" / "SKILL.md").exists()
            )
            self.assertEqual(
                set(updated["superpowers"]["installedSkills"]),
                {"brainstorming", "writing-plans"},
            )

    def test_sync_skill_sources_does_not_overwrite_unmanaged_installed_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            git("init", "-b", "main", cwd=source)
            git("config", "user.email", "tests@example.com", cwd=source)
            git("config", "user.name", "Tests", cwd=source)
            create_skill(source, "brainstorming")
            git("add", ".", cwd=source)
            git("commit", "-m", "initial", cwd=source)
            codex_home = root / "codex"
            unmanaged = codex_home / "skills" / "brainstorming"
            unmanaged.mkdir(parents=True)
            (unmanaged / "SKILL.md").write_text("local", encoding="utf-8")

            result = sync_skill_sources(
                {"superpowers": str(source)}, codex_home=codex_home
            )

            self.assertEqual(
                result["superpowers"]["blockedSkills"], ["brainstorming"]
            )
            self.assertEqual(
                (unmanaged / "SKILL.md").read_text(encoding="utf-8"), "local"
            )

    def test_sync_skill_sources_preserves_dirty_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            git("init", "-b", "main", cwd=source)
            git("config", "user.email", "tests@example.com", cwd=source)
            git("config", "user.name", "Tests", cwd=source)
            create_skill(source, "brainstorming")
            git("add", ".", cwd=source)
            git("commit", "-m", "initial", cwd=source)
            codex_home = root / "codex"
            sync_skill_sources({"superpowers": str(source)}, codex_home=codex_home)
            checkout = codex_home / "skills" / "sources" / "superpowers"
            (checkout / "local.txt").write_text("preserve me", encoding="utf-8")

            result = sync_skill_sources(
                {"superpowers": str(source)}, codex_home=codex_home
            )

            self.assertEqual(result["superpowers"]["status"], "blocked")
            self.assertEqual(result["superpowers"]["reason"], "dirty_checkout")
            self.assertTrue((checkout / "local.txt").exists())

    def test_creates_vervit_workflow_configuration_and_codebase(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            skills = root / "available"
            for name in [
                "brainstorming",
                "writing-plans",
                "systematic-debugging",
                "test-driven-development",
                "verification-before-completion",
            ]:
                create_skill(skills, name)

            results = initialize_project(
                root,
                env={"ATLASSIAN_CLOUD_ID": "not-recorded"},
                skill_search_roots=[skills],
            )

            config_path = root / "vervit-assistant" / "config.json"
            onboarding_path = root / "vervit-assistant" / "state.json"
            env_example_path = root / ".env.vervit.example"
            gitignore_path = root / ".gitignore"
            integrations_path = root / "docs" / "_codebase" / "INTEGRATIONS.md"
            self.assertEqual(results["vervit-assistant/config.json"], "written")
            self.assertTrue(config_path.exists())
            self.assertTrue(env_example_path.exists())
            self.assertFalse((root / ".env.vervit.local").exists())
            env_example = env_example_path.read_text(encoding="utf-8")
            self.assertIn("JIRA_BASE_URL=", env_example)
            self.assertIn("JIRA_EMAIL=", env_example)
            self.assertIn("JIRA_API_TOKEN=", env_example)
            gitignore = gitignore_path.read_text(encoding="utf-8")
            self.assertIn(".env.vervit.local", gitignore)
            self.assertIn("!.env.vervit.example", gitignore)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            serialized = json.dumps(config)
            self.assertNotIn("secret-token", serialized)
            self.assertEqual(config["git"]["mainBranch"], "main")
            self.assertEqual(config["git"]["releaseBranch"], "release")
            self.assertEqual(config["jira"]["apiTokenEnv"], "JIRA_API_TOKEN")
            onboarding = json.loads(onboarding_path.read_text(encoding="utf-8"))
            self.assertEqual(onboarding["dependencies"]["superpowers"]["status"], "ready")
            self.assertEqual(
                onboarding["dependencies"]["atlassian"]["connector"]["status"], "exposed"
            )
            self.assertTrue(onboarding["firstRun"]["required"])
            self.assertIn("configureJira", onboarding["firstRun"]["pending"])
            self.assertIn("listJiraIssues", onboarding["firstRun"]["availableActions"])
            integrations = integrations_path.read_text(encoding="utf-8")
            self.assertIn("Superpowers: ready", integrations)
            self.assertIn("Atlassian connector: exposed", integrations)

    def test_local_vervit_env_marks_jira_as_configured_without_recording_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            secret = "must-never-be-recorded"
            (root / ".env.vervit.local").write_text(
                "JIRA_BASE_URL=https://example.atlassian.net\n"
                "JIRA_EMAIL=user@example.com\n"
                f"JIRA_API_TOKEN={secret}\n",
                encoding="utf-8",
            )

            initialize_project(root, env={})

            onboarding_text = (root / "vervit-assistant" / "state.json").read_text(
                encoding="utf-8"
            )
            onboarding = json.loads(onboarding_text)
            self.assertEqual(onboarding["jira"]["rest"]["status"], "configured")
            self.assertNotIn(secret, onboarding_text)
            self.assertNotIn("configureJira", onboarding["firstRun"]["pending"])

    def test_initialize_project_records_installed_skill_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            git("init", "-b", "main", cwd=source)
            git("config", "user.email", "tests@example.com", cwd=source)
            git("config", "user.name", "Tests", cwd=source)
            for name in [
                "brainstorming",
                "writing-plans",
                "systematic-debugging",
                "test-driven-development",
                "verification-before-completion",
            ]:
                create_skill(source, name)
            git("add", ".", cwd=source)
            git("commit", "-m", "initial", cwd=source)
            target = root / "project"
            target.mkdir()
            codex_home = root / "codex"

            initialize_project(
                target,
                install_skills=True,
                skill_sources={"superpowers": str(source)},
                codex_home=codex_home,
                env={},
            )

            onboarding = json.loads(
                (target / "vervit-assistant" / "state.json").read_text(
                    encoding="utf-8"
                )
            )
            source_state = onboarding["dependencies"]["skillSources"]["superpowers"]
            self.assertEqual(source_state["action"], "cloned")
            self.assertEqual(
                onboarding["dependencies"]["superpowers"]["status"], "ready"
            )


if __name__ == "__main__":
    unittest.main()
