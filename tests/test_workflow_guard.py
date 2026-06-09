import unittest

from scripts.workflow_guard import (
    WorkflowGateError,
    can_close_task,
    release_ready,
    superpowers_flow,
)


class WorkflowGuardTests(unittest.TestCase):
    def test_selects_superpowers_flow_for_each_task_type(self):
        bug = superpowers_flow("bug")
        feature = superpowers_flow("feature")
        improvement = superpowers_flow("improvement", behavioral_change=False)

        self.assertEqual(bug[0], "superpowers:systematic-debugging")
        self.assertIn("superpowers:test-driven-development", feature)
        self.assertNotIn("superpowers:test-driven-development", improvement)
        self.assertEqual(
            bug[-1], "superpowers:verification-before-completion"
        )

    def test_hotfix_and_planned_tasks_require_correct_merge_target(self):
        common = {
            "prdApproved": True,
            "manualChecklistComplete": True,
            "automatedTestsPassed": True,
        }

        self.assertTrue(can_close_task({**common, "track": "hotfix", "mergedTo": "main"}))
        self.assertTrue(
            can_close_task({**common, "track": "planned", "mergedTo": "release"})
        )
        with self.assertRaises(WorkflowGateError):
            can_close_task({**common, "track": "planned", "mergedTo": "main"})

    def test_release_is_blocked_until_general_regression_and_sync_complete(self):
        with self.assertRaises(WorkflowGateError):
            release_ready(
                {
                    "scopeFrozen": True,
                    "fixVersionCreated": True,
                    "generalRegressionComplete": False,
                    "automatedTestsPassed": True,
                    "releaseNotesComplete": True,
                    "mainReleaseSynchronized": True,
                }
            )

        self.assertTrue(
            release_ready(
                {
                    "scopeFrozen": True,
                    "fixVersionCreated": True,
                    "generalRegressionComplete": True,
                    "automatedTestsPassed": True,
                    "releaseNotesComplete": True,
                    "mainReleaseSynchronized": True,
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
