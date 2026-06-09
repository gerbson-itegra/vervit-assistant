import unittest

from scripts.release_guard import (
    ReleasePolicyError,
    branch_name,
    build_release_publication_actions,
    calculate_next_version,
    ensure_single_active_release,
    integration_gate,
    latest_version_from_tags,
    validate_requested_version,
)


class ReleaseGuardTests(unittest.TestCase):
    def test_calculates_major_minor_patch_and_hotfix(self):
        self.assertEqual(calculate_next_version("1.4.2", ["improvement"]), "1.4.3")
        self.assertEqual(calculate_next_version("1.4.2", ["bug", "feature"]), "1.5.0")
        self.assertEqual(
            calculate_next_version("1.4.2", ["feature"], breaking=True), "2.0.0"
        )
        self.assertEqual(
            calculate_next_version("1.4.2", ["feature"], hotfix=True), "1.4.3"
        )

    def test_rejects_duplicate_or_incompatible_version(self):
        with self.assertRaises(ReleasePolicyError):
            validate_requested_version("1.4.2", "1.4.2", ["bug"], {"v1.4.2"})
        with self.assertRaises(ReleasePolicyError):
            validate_requested_version("1.4.2", "1.5.0", ["bug"], set())

    def test_builds_branch_names_for_delivery_track(self):
        self.assertEqual(
            branch_name("ABC-123", "Adicionar Login Social", "feature", "planned"),
            "feature/ABC-123-adicionar-login-social",
        )
        self.assertEqual(
            branch_name("ABC-123", "Corrigir Pagamento", "bug", "hotfix"),
            "hotfix/ABC-123-corrigir-pagamento",
        )

    def test_blocks_integration_when_any_gate_is_incomplete(self):
        with self.assertRaises(ReleasePolicyError):
            integration_gate(
                worktree_clean=True,
                automated_tests_passed=True,
                manual_checklist_complete=False,
                release_notes_complete=True,
                branch_synchronized=True,
            )

        self.assertTrue(
            integration_gate(
                worktree_clean=True,
                automated_tests_passed=True,
                manual_checklist_complete=True,
                release_notes_complete=True,
                branch_synchronized=True,
            )
        )

    def test_detects_latest_version_and_builds_publication_sequence(self):
        self.assertEqual(
            latest_version_from_tags(["draft", "v1.2.9", "v1.10.0", "v2.0.0-rc1"]),
            "1.10.0",
        )

    def test_allows_only_one_planned_release_at_a_time(self):
        self.assertTrue(ensure_single_active_release(["REL-10"]))
        with self.assertRaises(ReleasePolicyError):
            ensure_single_active_release(["REL-10", "REL-11"])
        self.assertEqual(
            build_release_publication_actions("1.10.0"),
            [
                {"action": "merge_no_ff", "source": "release", "target": "main"},
                {"action": "tag_release", "source": "main", "tag": "v1.10.0"},
                {"action": "merge_no_ff", "source": "main", "target": "release"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
