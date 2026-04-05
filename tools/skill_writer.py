#!/usr/bin/env python3
"""
skill_writer.py — Write and manage teacher skill files.

Usage:
    python3 skill_writer.py --action slug --name "姚老师"
    python3 skill_writer.py --action create --slug yao-laoshi --meta '{"name":"姚老师",...}' --base-dir ./teachers
    python3 skill_writer.py --action list --base-dir ./teachers
    python3 skill_writer.py --action delete --slug yao-laoshi --base-dir ./teachers
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone

try:
    from pypinyin import pinyin, Style
except ImportError:
    pinyin = None
    Style = None


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a teacher's name.

    Chinese names are converted to pinyin. '老师' suffix is preserved as 'laoshi'.
    English names are lowercased with spaces replaced by hyphens.
    """
    name = name.strip()

    # Handle Chinese names
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in name)
    if not has_chinese:
        return name.lower().replace(" ", "-")

    # Handle "X老师" pattern
    if name.endswith("老师"):
        surname = name[:-2]
        if pinyin is not None:
            surname_py = "".join(p[0] for p in pinyin(surname, style=Style.NORMAL))
        else:
            surname_py = surname
        return f"{surname_py}-laoshi"

    # Full Chinese name: treat first character as surname, rest as given name
    if pinyin is not None:
        chars = list(name)
        py_parts = [p[0] for p in pinyin(name, style=Style.NORMAL)]
        if len(py_parts) > 1:
            surname_py = py_parts[0]
            given_py = "".join(py_parts[1:])
            return f"{surname_py}-{given_py}"
        return py_parts[0]
    else:
        return name


def create_meta(
    name: str,
    slug: str,
    subject: str,
    grade: str,
    gender: str,
    teaching_years: int,
    school: str = "",
    role: str = "",
    mbti: str = "",
    is_class_teacher: bool = False,
    personality_tags: list = None,
    teaching_tags: list = None,
    impression: str = "",
) -> dict:
    """Create a meta.json structure for a teacher."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "name": name,
        "slug": slug,
        "version": 1,
        "created_at": now,
        "updated_at": now,
        "profile": {
            "school": school,
            "subject": subject,
            "grade": grade,
            "role": role or f"{subject}老师",
            "gender": gender,
            "teaching_years": teaching_years,
            "mbti": mbti,
            "is_class_teacher": is_class_teacher,
        },
        "tags": {
            "personality": personality_tags or [],
            "teaching": teaching_tags or [],
        },
        "impression": impression,
        "knowledge_sources": [],
        "corrections_count": 0,
    }


def _write_file(directory: str, filename: str, content: str) -> str:
    """Write content to a file in the given directory."""
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def write_teaching(teacher_dir: str, content: str) -> str:
    """Write teaching.md to the teacher directory."""
    return _write_file(teacher_dir, "teaching.md", content)


def write_persona(teacher_dir: str, content: str) -> str:
    """Write persona.md to the teacher directory."""
    return _write_file(teacher_dir, "persona.md", content)


def write_knowledge(teacher_dir: str, content: str) -> str:
    """Write knowledge.md to the teacher directory."""
    return _write_file(teacher_dir, "knowledge.md", content)


def write_skill(teacher_dir: str, name: str) -> str:
    """Merge teaching.md + persona.md + knowledge.md into SKILL.md with runtime rules."""
    teaching_path = os.path.join(teacher_dir, "teaching.md")
    persona_path = os.path.join(teacher_dir, "persona.md")
    knowledge_path = os.path.join(teacher_dir, "knowledge.md")

    parts = []
    parts.append(f"# {name} — AI 老师技能\n")
    parts.append("> 本文件由 teacher-skill 自动生成。请勿手动编辑。\n")
    parts.append("## 三维度运行时协调规则\n")
    parts.append("1. **Part B（persona）先判断**：这个老师会接受这个问题吗？以什么态度回应？")
    parts.append("2. **Part A（teaching）决定方法**：用什么教学方式来讲？按什么流程引导？")
    parts.append("3. **Part C（knowledge）提供内容**：调用老师的知识讲解路径、口诀、类比")
    parts.append("4. **输出时保持 Part B 的表达风格**：用老师的口头禅和语气输出\n")
    parts.append("> **Layer 0 人格规则优先级最高，不可违反。**\n")
    parts.append("---\n")

    for label, path in [
        ("PART A：教学能力", teaching_path),
        ("PART B：人格特征", persona_path),
        ("PART C：学科知识", knowledge_path),
    ]:
        parts.append(f"# {label}\n")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f.read())
        else:
            parts.append("(尚未生成)\n")
        parts.append("\n---\n")

    content = "\n".join(parts)
    return _write_file(teacher_dir, "SKILL.md", content)


def write_standalone_skills(teacher_dir: str, name: str) -> list:
    """Generate standalone skill files for each dimension."""
    files_written = []

    for dimension, filename, src_file, desc in [
        ("教学能力", "teaching_skill.md", "teaching.md", "只包含教学能力维度，适合让 AI 用这个老师的方式出题和讲课。"),
        ("人格特征", "persona_skill.md", "persona.md", "只包含人格特征维度，适合让 AI 用这个老师的语气和风格互动。"),
        ("学科知识", "knowledge_skill.md", "knowledge.md", "只包含学科知识维度，适合用老师的方式复习知识点。"),
    ]:
        src_path = os.path.join(teacher_dir, src_file)
        if not os.path.exists(src_path):
            continue

        with open(src_path, "r", encoding="utf-8") as f:
            src_content = f.read()

        content = f"# {name} — {dimension}（独立技能）\n\n"
        content += f"> {desc}\n\n"
        content += "---\n\n"
        content += src_content

        path = _write_file(teacher_dir, filename, content)
        files_written.append(path)

    return files_written


def write_meta(teacher_dir: str, meta: dict) -> str:
    """Write meta.json to the teacher directory."""
    path = os.path.join(teacher_dir, "meta.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return path


def list_teachers(base_dir: str) -> list:
    """List all teachers in the base directory."""
    teachers = []
    if not os.path.isdir(base_dir):
        return teachers

    for entry in sorted(os.listdir(base_dir)):
        meta_path = os.path.join(base_dir, entry, "meta.json")
        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            teachers.append(meta)
    return teachers


def delete_teacher(base_dir: str, slug: str) -> None:
    """Delete a teacher directory by slug."""
    teacher_dir = os.path.join(base_dir, slug)
    if not os.path.isdir(teacher_dir):
        raise FileNotFoundError(f"Teacher '{slug}' not found in {base_dir}")
    shutil.rmtree(teacher_dir)


def main():
    parser = argparse.ArgumentParser(description="Teacher skill file writer")
    parser.add_argument("--action", required=True, choices=["slug", "create", "list", "delete"])
    parser.add_argument("--name", help="Teacher name (for slug action)")
    parser.add_argument("--slug", help="Teacher slug")
    parser.add_argument("--meta", help="Meta JSON string (for create action)")
    parser.add_argument("--base-dir", default="./teachers", help="Base directory for teacher profiles")

    args = parser.parse_args()

    if args.action == "slug":
        if not args.name:
            print("Error: --name required for slug action", file=sys.stderr)
            sys.exit(1)
        print(generate_slug(args.name))

    elif args.action == "list":
        teachers = list_teachers(args.base_dir)
        if not teachers:
            print("No teachers found.")
        else:
            for t in teachers:
                subj = t.get("profile", {}).get("subject", "?")
                print(f"  {t['slug']}  —  {t['name']}（{subj}）v{t.get('version', '?')}")

    elif args.action == "delete":
        if not args.slug:
            print("Error: --slug required for delete action", file=sys.stderr)
            sys.exit(1)
        delete_teacher(args.base_dir, args.slug)
        print(f"Deleted: {args.slug}")

    elif args.action == "create":
        if not args.slug or not args.meta:
            print("Error: --slug and --meta required for create action", file=sys.stderr)
            sys.exit(1)
        meta = json.loads(args.meta)
        teacher_dir = os.path.join(args.base_dir, args.slug)
        os.makedirs(teacher_dir, exist_ok=True)
        os.makedirs(os.path.join(teacher_dir, "versions"), exist_ok=True)
        os.makedirs(os.path.join(teacher_dir, "sources"), exist_ok=True)
        write_meta(teacher_dir, meta)
        print(f"Created: {teacher_dir}")


if __name__ == "__main__":
    main()
