# tests/test_skill_writer.py
"""Tests for skill_writer.py"""
import json
import os
import shutil
import tempfile
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from skill_writer import (
    generate_slug,
    create_meta,
    write_teaching,
    write_persona,
    write_knowledge,
    write_skill,
    write_standalone_skills,
    list_teachers,
    delete_teacher,
)


class TestGenerateSlug(unittest.TestCase):
    def test_chinese_name(self):
        self.assertEqual(generate_slug("姚雪梅"), "yao-xuemei")

    def test_chinese_surname_laoshi(self):
        self.assertEqual(generate_slug("姚老师"), "yao-laoshi")

    def test_english_name(self):
        self.assertEqual(generate_slug("John Smith"), "john-smith")

    def test_single_character_surname(self):
        self.assertEqual(generate_slug("王老师"), "wang-laoshi")


class TestCreateMeta(unittest.TestCase):
    def test_creates_valid_meta(self):
        meta = create_meta(
            name="姚老师",
            slug="yao-laoshi",
            subject="数学",
            grade="初二",
            gender="female",
            teaching_years=20,
        )
        self.assertEqual(meta["name"], "姚老师")
        self.assertEqual(meta["slug"], "yao-laoshi")
        self.assertEqual(meta["version"], 1)
        self.assertEqual(meta["profile"]["subject"], "数学")
        self.assertEqual(meta["profile"]["teaching_years"], 20)
        self.assertIn("created_at", meta)

    def test_optional_fields(self):
        meta = create_meta(
            name="周老师",
            slug="zhou-laoshi",
            subject="英语",
            grade="初二",
            gender="female",
            teaching_years=20,
            school="北京一中",
            role="班主任",
            mbti="ENFJ",
        )
        self.assertEqual(meta["profile"]["school"], "北京一中")
        self.assertEqual(meta["profile"]["mbti"], "ENFJ")


class TestWriteTeaching(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(self.teacher_dir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_writes_teaching_file(self):
        content = "# 姚老师的教学能力\n\n## 一、教学范围\n..."
        write_teaching(self.teacher_dir, content)
        path = os.path.join(self.teacher_dir, "teaching.md")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)


class TestWritePersona(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(self.teacher_dir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_writes_persona_file(self):
        content = "# 姚老师的人格特征\n\n## Layer 0\n..."
        write_persona(self.teacher_dir, content)
        path = os.path.join(self.teacher_dir, "persona.md")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)


class TestWriteKnowledge(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(self.teacher_dir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_writes_knowledge_file(self):
        content = "# 姚老师的学科知识\n\n## 一、知识讲解路径\n..."
        write_knowledge(self.teacher_dir, content)
        path = os.path.join(self.teacher_dir, "knowledge.md")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)


class TestWriteSkill(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(self.teacher_dir)
        self.teaching = "# Teaching\ncontent"
        self.persona = "# Persona\ncontent"
        self.knowledge = "# Knowledge\ncontent"
        write_teaching(self.teacher_dir, self.teaching)
        write_persona(self.teacher_dir, self.persona)
        write_knowledge(self.teacher_dir, self.knowledge)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_merges_three_files(self):
        write_skill(self.teacher_dir, "姚老师")
        path = os.path.join(self.teacher_dir, "SKILL.md")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("# Teaching", content)
        self.assertIn("# Persona", content)
        self.assertIn("# Knowledge", content)
        self.assertIn("Layer 0 人格规则优先级最高", content)

    def test_includes_runtime_rules(self):
        write_skill(self.teacher_dir, "姚老师")
        path = os.path.join(self.teacher_dir, "SKILL.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Part B（persona）先判断", content)
        self.assertIn("Part A（teaching）决定方法", content)
        self.assertIn("Part C（knowledge）提供内容", content)


class TestWriteStandaloneSkills(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(self.teacher_dir)
        write_teaching(self.teacher_dir, "# Teaching\ncontent")
        write_persona(self.teacher_dir, "# Persona\ncontent")
        write_knowledge(self.teacher_dir, "# Knowledge\ncontent")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_three_standalone_files(self):
        write_standalone_skills(self.teacher_dir, "姚老师")
        for name in ("teaching_skill.md", "persona_skill.md", "knowledge_skill.md"):
            path = os.path.join(self.teacher_dir, name)
            self.assertTrue(os.path.exists(path), f"{name} should exist")


class TestListTeachers(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        for slug in ("yao-laoshi", "zhou-laoshi"):
            d = os.path.join(self.tmpdir, slug)
            os.makedirs(d)
            meta = create_meta(name=f"{slug}", slug=slug, subject="test", grade="初二", gender="female", teaching_years=1)
            with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_lists_all_teachers(self):
        teachers = list_teachers(self.tmpdir)
        slugs = [t["slug"] for t in teachers]
        self.assertIn("yao-laoshi", slugs)
        self.assertIn("zhou-laoshi", slugs)


class TestDeleteTeacher(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.teacher_dir = os.path.join(self.tmpdir, "yao-laoshi")
        os.makedirs(self.teacher_dir)
        with open(os.path.join(self.teacher_dir, "meta.json"), "w") as f:
            json.dump({"name": "test"}, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_deletes_teacher_directory(self):
        delete_teacher(self.tmpdir, "yao-laoshi")
        self.assertFalse(os.path.exists(self.teacher_dir))

    def test_raises_on_missing_teacher(self):
        with self.assertRaises(FileNotFoundError):
            delete_teacher(self.tmpdir, "nonexistent")


if __name__ == "__main__":
    unittest.main()
