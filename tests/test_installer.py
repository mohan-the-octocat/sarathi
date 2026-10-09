"""Unit tests for the Sarathi Antigravity installer."""

import os
import pathlib
import tempfile
import unittest

from scripts.install import (
    MANIFEST_FILENAME,
    install_plugin,
    resolve_global_paths,
    resolve_workspace_paths,
    uninstall_plugin,
)


class TestInstaller(unittest.TestCase):

  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.ws_dir = self.temp_dir.name

  def tearDown(self):
    self.temp_dir.cleanup()

  def test_resolve_workspace_paths(self):
    paths = resolve_workspace_paths(self.ws_dir)
    self.assertEqual(paths["plugins_dir"], pathlib.Path(self.ws_dir) / ".gemini" / "plugins" / "sarathi")
    self.assertEqual(paths["agents_dir"], pathlib.Path(self.ws_dir) / ".agents" / "agents")

  def test_dry_run_install(self):
    ret = install_plugin(
        scope="workspace",
        project_dir=self.ws_dir,
        dry_run=True,
    )
    self.assertEqual(ret, 0)
    # In dry run, files should not exist
    self.assertFalse((pathlib.Path(self.ws_dir) / ".gemini" / "plugins" / "sarathi").exists())

  def test_real_workspace_install_and_uninstall(self):
    # 1. Install
    ret = install_plugin(
        scope="workspace",
        project_dir=self.ws_dir,
        use_symlink=True,
    )
    self.assertEqual(ret, 0)

    # Verify plugin directory was created
    plugin_target = pathlib.Path(self.ws_dir) / ".gemini" / "plugins" / "sarathi"
    self.assertTrue(plugin_target.exists(), "Plugin target must exist")

    # Verify agents were installed
    agents_target = pathlib.Path(self.ws_dir) / ".agents" / "agents"
    self.assertTrue((agents_target / "sarathi.md").exists(), "sarathi.md agent must exist in agents dir")
    self.assertTrue((agents_target / "sarathi_worker.md").exists())
    self.assertTrue((agents_target / "sarathi_scout.md").exists())
    self.assertTrue((agents_target / "sarathi_redteam.md").exists())

    # Verify manifest
    manifest_file = plugin_target.parent / MANIFEST_FILENAME
    self.assertTrue(manifest_file.is_file(), "Manifest must be written")

    # 2. Uninstall
    uninst_ret = uninstall_plugin(scope="workspace", project_dir=self.ws_dir)
    self.assertEqual(uninst_ret, 0)

    # Verify cleanup
    self.assertFalse(plugin_target.exists(), "Plugin target should be removed")
    self.assertFalse((agents_target / "sarathi.md").exists(), "Agent link should be removed")
    self.assertFalse(manifest_file.exists(), "Manifest should be removed")


if __name__ == "__main__":
  unittest.main()
