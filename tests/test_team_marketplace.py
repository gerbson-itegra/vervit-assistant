import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TeamMarketplaceTests(unittest.TestCase):
    def test_marketplace_exposes_root_plugin(self):
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(marketplace["name"], "vervit")
        self.assertEqual(len(marketplace["plugins"]), 1)

        plugin = marketplace["plugins"][0]
        self.assertEqual(plugin["name"], "vervit-assistant")
        self.assertEqual(
            plugin["source"],
            {"source": "local", "path": "./plugins/vervit-assistant"},
        )
        self.assertEqual(plugin["policy"]["installation"], "AVAILABLE")
        self.assertEqual(plugin["policy"]["authentication"], "ON_INSTALL")

    def test_installer_defaults_to_repository_marketplace(self):
        installer = (ROOT / "scripts" / "install_plugin.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            'https://github.com/gerbson-itegra/vervit-assistant.git', installer
        )
        self.assertIn('$marketplaceName = "vervit"', installer)
        self.assertIn('$pluginName = "vervit-assistant"', installer)
        self.assertIn(
            'Invoke-Codex -Arguments @("plugin", "add", "$pluginName@$marketplaceName")',
            installer,
        )

    def test_npx_installer_is_private_and_points_to_private_repository(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        installer = (ROOT / "bin" / "install.mjs").read_text(encoding="utf-8")

        self.assertTrue(package["private"])
        self.assertEqual(
            package["bin"],
            {"vervit-assistant-install": "./bin/install.mjs"},
        )
        self.assertIn("gerbson-itegra/vervit-assistant", installer)
        self.assertIn('"plugin", "marketplace", "add"', installer)
        self.assertIn('"plugin", "add"', installer)

    def test_marketplace_package_is_current(self):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_marketplace_plugin.py")],
            check=True,
            capture_output=True,
            text=True,
        )

        packaged_manifest = (
            ROOT / "plugins" / "vervit-assistant" / ".codex-plugin" / "plugin.json"
        )
        self.assertEqual(
            packaged_manifest.read_bytes(),
            (ROOT / ".codex-plugin" / "plugin.json").read_bytes(),
        )
        packaged_scripts = ROOT / "plugins" / "vervit-assistant" / "scripts"
        self.assertFalse((packaged_scripts / "build_marketplace_plugin.py").exists())
        self.assertFalse((packaged_scripts / "install_plugin.ps1").exists())


if __name__ == "__main__":
    unittest.main()
