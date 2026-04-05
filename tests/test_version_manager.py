# tests/test_version_manager.py
"""Tests for version_manager.py"""
import json
import os
import shutil
import tempfile
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from version_manager import archive_version, rollback_version, cleanup_versions


class TestArchiveVersion(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(os.path.join(self.teacher_dir, "versions"))
        # Create current files
        meta = {"name": "姚老师", "slug": "yao-laoshi", "version": 1}
        with open(os.path.join(self.teacher_dir, "meta.json"), "w") as f:
            json.dump(meta, f)
        with open(os.path.join(self.teacher_dir, "teaching.md"), "w") as f:
            f.write("# v1 teaching")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_version_archive(self):
        archive_version(self.teacher_dir)
        versions_dir = os.path.join(self.teacher_dir, "versions")
        entries = os.listdir(versions_dir)
        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0].startswith("v1_"))

    def test_archive_contains_files(self):
        archive_version(self.teacher_dir)
        versions_dir = os.path.join(self.teacher_dir, "versions")
        archive_dir = os.path.join(versions_dir, os.listdir(versions_dir)[0])
        self.assertTrue(os.path.exists(os.path.join(archive_dir, "meta.json")))
        self.assertTrue(os.path.exists(os.path.join(archive_dir, "teaching.md")))


class TestRollbackVersion(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(os.path.join(self.teacher_dir, "versions"))
        # v1
        meta = {"name": "姚老师", "slug": "yao-laoshi", "version": 1}
        with open(os.path.join(self.teacher_dir, "meta.json"), "w") as f:
            json.dump(meta, f)
        with open(os.path.join(self.teacher_dir, "teaching.md"), "w") as f:
            f.write("# v1 teaching")
        archive_version(self.teacher_dir)
        # v2
        with open(os.path.join(self.teacher_dir, "teaching.md"), "w") as f:
            f.write("# v2 teaching")
        meta["version"] = 2
        with open(os.path.join(self.teacher_dir, "meta.json"), "w") as f:
            json.dump(meta, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_rollback_restores_content(self):
        rollback_version(self.teacher_dir, 1)
        with open(os.path.join(self.teacher_dir, "teaching.md")) as f:
            self.assertEqual(f.read(), "# v1 teaching")

    def test_rollback_creates_safety_backup(self):
        rollback_version(self.teacher_dir, 1)
        versions_dir = os.path.join(self.teacher_dir, "versions")
        entries = os.listdir(versions_dir)
        backup_dirs = [e for e in entries if "before_rollback" in e]
        self.assertEqual(len(backup_dirs), 1)


class TestCleanupVersions(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(os.path.join(self.teacher_dir, "versions"))
        # Create 12 version archives
        for i in range(1, 13):
            archive_dir = os.path.join(self.teacher_dir, "versions", f"v{i}_20260405")
            os.makedirs(archive_dir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_keeps_max_versions(self):
        cleanup_versions(self.teacher_dir, max_versions=10)
        versions_dir = os.path.join(self.teacher_dir, "versions")
        self.assertEqual(len(os.listdir(versions_dir)), 10)

    def test_removes_oldest(self):
        cleanup_versions(self.teacher_dir, max_versions=10)
        versions_dir = os.path.join(self.teacher_dir, "versions")
        entries = os.listdir(versions_dir)
        self.assertNotIn("v1_20260405", entries)
        self.assertNotIn("v2_20260405", entries)


if __name__ == "__main__":
    unittest.main()
