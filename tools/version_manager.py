#!/usr/bin/env python3
"""
version_manager.py — Archive, rollback, and cleanup teacher profile versions.

Usage:
    python3 version_manager.py --action archive --teacher-dir ./teachers/yao-laoshi
    python3 version_manager.py --action rollback --slug yao-laoshi --version 1 --base-dir ./teachers
    python3 version_manager.py --action cleanup --teacher-dir ./teachers/yao-laoshi
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime


MAX_VERSIONS = 10
ARCHIVABLE_FILES = ["meta.json", "teaching.md", "persona.md", "knowledge.md", "SKILL.md",
                     "teaching_skill.md", "persona_skill.md", "knowledge_skill.md"]


def archive_version(teacher_dir: str) -> str:
    """Archive current files to versions/ directory.

    Returns the path to the created archive directory.
    """
    meta_path = os.path.join(teacher_dir, "meta.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    version = meta.get("version", 1)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_name = f"v{version}_{timestamp}"
    archive_dir = os.path.join(teacher_dir, "versions", archive_name)
    os.makedirs(archive_dir, exist_ok=True)

    for filename in ARCHIVABLE_FILES:
        src = os.path.join(teacher_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(archive_dir, filename))

    return archive_dir


def rollback_version(teacher_dir: str, target_version: int) -> None:
    """Rollback to a specific version. Creates a safety backup first."""
    versions_dir = os.path.join(teacher_dir, "versions")

    # Find the target version archive
    target_dir = None
    for entry in sorted(os.listdir(versions_dir)):
        if entry.startswith(f"v{target_version}_"):
            target_dir = os.path.join(versions_dir, entry)
            break

    if target_dir is None:
        raise FileNotFoundError(f"Version {target_version} not found")

    # Safety backup of current state
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(versions_dir, f"v_before_rollback_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    for filename in ARCHIVABLE_FILES:
        src = os.path.join(teacher_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(backup_dir, filename))

    # Restore files from target version
    for filename in ARCHIVABLE_FILES:
        src = os.path.join(target_dir, filename)
        dst = os.path.join(teacher_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)


def cleanup_versions(teacher_dir: str, max_versions: int = MAX_VERSIONS) -> int:
    """Remove oldest versions if count exceeds max. Returns number removed."""
    versions_dir = os.path.join(teacher_dir, "versions")
    if not os.path.isdir(versions_dir):
        return 0

    def _version_sort_key(name: str) -> tuple:
        """Sort by numeric version number, then lexicographically for ties."""
        parts = name.lstrip("v").split("_", 1)
        try:
            return (int(parts[0]), parts[1] if len(parts) > 1 else "")
        except ValueError:
            return (0, name)

    entries = sorted(os.listdir(versions_dir), key=_version_sort_key)
    removed = 0

    while len(entries) > max_versions:
        oldest = entries.pop(0)
        shutil.rmtree(os.path.join(versions_dir, oldest))
        removed += 1

    return removed


def main():
    parser = argparse.ArgumentParser(description="Teacher version manager")
    parser.add_argument("--action", required=True, choices=["archive", "rollback", "cleanup"])
    parser.add_argument("--teacher-dir", help="Teacher directory path")
    parser.add_argument("--slug", help="Teacher slug (for rollback)")
    parser.add_argument("--version", type=int, help="Target version (for rollback)")
    parser.add_argument("--base-dir", default="./teachers", help="Base directory")

    args = parser.parse_args()

    if args.action == "archive":
        path = archive_version(args.teacher_dir)
        print(f"Archived to: {path}")

    elif args.action == "rollback":
        teacher_dir = args.teacher_dir or os.path.join(args.base_dir, args.slug)
        rollback_version(teacher_dir, args.version)
        print(f"Rolled back to version {args.version}")

    elif args.action == "cleanup":
        removed = cleanup_versions(args.teacher_dir)
        print(f"Cleaned up {removed} old versions")


if __name__ == "__main__":
    main()
