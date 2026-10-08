#!/usr/bin/env python3
"""Cross-platform installer for Orchestra plugin in Antigravity."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import sys
from typing import Any

MANIFEST_FILENAME = ".orchestra-installed-manifest.json"


def resolve_global_paths(plugin_name: str = "orchestra") -> dict[str, pathlib.Path]:
  """Resolves standard global Antigravity / Jetski paths."""
  home = pathlib.Path.home()
  gemini_config = home / ".gemini" / "config"
  plugins_dir = gemini_config / "plugins" / plugin_name
  agents_dir = gemini_config / "agents"

  return {
      "plugins_dir": plugins_dir,
      "agents_dir": agents_dir,
      "config_root": gemini_config,
  }


def resolve_workspace_paths(workspace_dir: str, plugin_name: str = "orchestra") -> dict[str, pathlib.Path]:
  """Resolves workspace-local Antigravity paths."""
  ws = pathlib.Path(workspace_dir).resolve()
  plugins_dir = ws / ".gemini" / "plugins" / plugin_name
  agents_dir = ws / ".agents" / "agents"

  return {
      "plugins_dir": plugins_dir,
      "agents_dir": agents_dir,
      "config_root": ws,
  }


def get_source_root() -> pathlib.Path:
  """Gets the root directory of this repository."""
  return pathlib.Path(__file__).resolve().parent.parent


def install_plugin(
    scope: str = "global",
    project_dir: str | None = None,
    plugin_name: str = "orchestra",
    use_symlink: bool = True,
    dry_run: bool = False,
    force: bool = False,
) -> int:
  """Installs the Orchestra plugin and registers custom agents."""
  src_root = get_source_root()
  print(f"[Orchestra] Installing from: {src_root}")

  if scope == "global":
    paths = resolve_global_paths(plugin_name=plugin_name)
  elif scope == "workspace":
    if not project_dir:
      project_dir = os.getcwd()
    paths = resolve_workspace_paths(project_dir, plugin_name=plugin_name)
  else:
    print(f"Error: Unknown scope '{scope}'. Use 'global' or 'workspace'.", file=sys.stderr)
    return 1

  target_plugin_dir = paths["plugins_dir"]
  target_agents_dir = paths["agents_dir"]

  print(f"[Orchestra] Target plugin location: {target_plugin_dir}")
  print(f"[Orchestra] Target agents location: {target_agents_dir}")

  manifest: dict[str, Any] = {
      "scope": scope,
      "source_root": str(src_root),
      "installed_at": str(pathlib.Path.home()),
      "created_links": [],
      "copied_files": [],
  }

  if dry_run:
    print("[DRY RUN] Would create target directories and link plugin + agents.")
    return 0

  # 1. Create plugin directory / link
  target_plugin_dir.parent.mkdir(parents=True, exist_ok=True)
  if target_plugin_dir.exists() or target_plugin_dir.is_symlink():
    if target_plugin_dir.is_symlink():
      target_plugin_dir.unlink()
    else:
      shutil.rmtree(target_plugin_dir)

  if use_symlink:
    try:
      target_plugin_dir.symlink_to(src_root, target_is_directory=True)
      manifest["created_links"].append(str(target_plugin_dir))
      print(f"  + Symlinked plugin directory: {target_plugin_dir} -> {src_root}")
    except OSError as e:
      print(f"  ! Symlink failed ({e}), falling back to copy...", file=sys.stderr)
      shutil.copytree(src_root, target_plugin_dir, dirs_exist_ok=True)
      manifest["copied_files"].append(str(target_plugin_dir))
  else:
    shutil.copytree(src_root, target_plugin_dir, dirs_exist_ok=True)
    manifest["copied_files"].append(str(target_plugin_dir))
    print(f"  + Copied plugin directory: {target_plugin_dir}")

  # 2. Expose markdown agents directly in agents directory
  target_agents_dir.mkdir(parents=True, exist_ok=True)
  agents_src = src_root / "agents"
  if agents_src.is_dir():
    for agent_file in agents_src.glob("*.md"):
      dest = target_agents_dir / agent_file.name
      if dest.exists() or dest.is_symlink():
        dest.unlink()
      if use_symlink:
        try:
          dest.symlink_to(agent_file)
          manifest["created_links"].append(str(dest))
          print(f"  + Registered agent: {dest.name} -> {agent_file}")
        except OSError:
          shutil.copy2(agent_file, dest)
          manifest["copied_files"].append(str(dest))
          print(f"  + Copied agent: {dest.name}")
      else:
        shutil.copy2(agent_file, dest)
        manifest["copied_files"].append(str(dest))
        print(f"  + Copied agent: {dest.name}")

  # 3. Save install manifest
  manifest_file = target_plugin_dir.parent / MANIFEST_FILENAME
  with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

  print("\n[SUCCESS] Orchestra successfully installed for Antigravity!")
  print("You can now:")
  print("  1. Select 'orchestra' from the Agent dropdown in Antigravity.")
  print("  2. Use slash commands: /orchestra, /orchestra-plan, /orchestra-verify.")
  return 0


def uninstall_plugin(
    scope: str = "global",
    project_dir: str | None = None,
    plugin_name: str = "orchestra",
) -> int:
  """Uninstalls previously installed Orchestra plugin and agents."""
  if scope == "global":
    paths = resolve_global_paths(plugin_name=plugin_name)
  else:
    if not project_dir:
      project_dir = os.getcwd()
    paths = resolve_workspace_paths(project_dir, plugin_name=plugin_name)

  manifest_file = paths["plugins_dir"].parent / MANIFEST_FILENAME
  if not manifest_file.exists():
    print(f"No installation manifest found at {manifest_file}. Cleaning default paths...")
    if paths["plugins_dir"].is_symlink():
      paths["plugins_dir"].unlink()
      print(f"  - Removed {paths['plugins_dir']}")
    elif paths["plugins_dir"].is_dir():
      shutil.rmtree(paths["plugins_dir"])
      print(f"  - Removed {paths['plugins_dir']}")
    return 0

  with open(manifest_file, "r", encoding="utf-8") as f:
    manifest = json.load(f)

  for link in manifest.get("created_links", []):
    p = pathlib.Path(link)
    if p.exists() or p.is_symlink():
      p.unlink()
      print(f"  - Removed link: {link}")

  for copied in manifest.get("copied_files", []):
    p = pathlib.Path(copied)
    if p.is_file():
      p.unlink()
      print(f"  - Removed file: {copied}")
    elif p.is_dir():
      shutil.rmtree(p)
      print(f"  - Removed directory: {copied}")

  manifest_file.unlink(missing_ok=True)
  print("\n[SUCCESS] Orchestra uninstalled cleanly.")
  return 0


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(description="Installer for Orchestra in Antigravity.")
  parser.add_argument(
      "--scope",
      choices=["global", "workspace"],
      default="global",
      help="Installation scope: 'global' (~/.gemini/config) or 'workspace' (.gemini).",
  )
  parser.add_argument(
      "--plugin-name",
      default="orchestra",
      help="Target plugin directory name (default: 'orchestra').",
  )
  parser.add_argument(
      "--project-dir",
      default=None,
      help="Target project directory for workspace scope (defaults to CWD).",
  )
  parser.add_argument(
      "--copy",
      action="store_true",
      help="Copy files instead of symlinking.",
  )
  parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Simulate installation without making changes.",
  )
  parser.add_argument(
      "--force",
      action="store_true",
      help="Force overwrite existing installation or symlinks.",
  )
  parser.add_argument(
      "--uninstall",
      action="store_true",
      help="Uninstall Orchestra plugin and agents.",
  )

  args = parser.parse_args(argv)

  if args.uninstall:
    return uninstall_plugin(
        scope=args.scope,
        project_dir=args.project_dir,
        plugin_name=args.plugin_name,
    )

  return install_plugin(
      scope=args.scope,
      project_dir=args.project_dir,
      plugin_name=args.plugin_name,
      use_symlink=not args.copy,
      dry_run=args.dry_run,
      force=args.force,
  )


if __name__ == "__main__":
  sys.exit(main())
