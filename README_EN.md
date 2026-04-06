English | [中文](./README.md)

# Teacher Skill — Distill Your Teacher

**Turn your favorite teacher into an AI that teaches just like them.**

Ever had a teacher who explained things in a way that just *clicked*? What happens when you switch classes, graduate, or move on — and that teacher is gone?

Teacher Skill captures a teacher's **teaching methods**, **personality**, and **subject knowledge** into a structured AI skill file. Once loaded, the AI interacts like your teacher — using their catchphrases, following their teaching style, and even reciting their mnemonics.

> Inspired by [colleague-skill](https://github.com/titanwings/colleague-skill) (distill your colleagues). We brought the same idea to education.

## What Does It Do?

### Three-Dimensional Distillation

| Dimension | What It Captures | Example |
|-----------|-----------------|---------|
| **Teaching Ability** | Lesson flow, question style, grading habits, problem-solving approach | "Before each new concept, Ms. Yao writes a real-life scenario on the board" |
| **Personality** | Catchphrases, tone, attitude toward different students, boundaries | "When a student says 'I can't do it', she asks 'Where did you get stuck?'" |
| **Subject Knowledge** | Teaching paths, mnemonics, key points, knowledge connections | "Equations are like a family — linear is the little brother, quadratic is the big brother" |

### What You Get

A structured teacher profile:

```
teachers/yao-laoshi/
├── teaching.md        # How they teach
├── persona.md         # Who they are (5-layer personality model)
├── knowledge.md       # How they explain things
├── SKILL.md           # All-in-one skill file (load this)
├── teaching_skill.md  # Teaching dimension only
├── persona_skill.md   # Personality dimension only
└── knowledge_skill.md # Knowledge dimension only
```

## Quick Start

### Install

```bash
git clone https://github.com/AdeleZhu/teacher-skill ~/.claude/skills/create-teacher
```

### Use

In Claude Code:

```
/create-teacher
```

The AI guides you through three rounds of questions about your teacher. Done — your AI teacher is ready.

### Import Chat Logs (Optional)

Got chat logs from your teacher? Import them for better accuracy:

| Source | Support |
|--------|---------|
| WeChat | Export as txt |
| QQ | Export as txt |
| DingTalk | Auto-collect via API |
| Feishu/Lark | Auto-collect / Browser / MCP |
| Email | .eml / .mbox / .txt |

## Examples

Two example teachers are included:

- **Ms. Yao** (Math, 20 years) — Strict, board-writing expert, never gives answers directly
- **Ms. Zhou** (English, 20 years) — Energetic, "Come on, try it!", encourages speaking

## How It Works

**9 prompt templates** drive the distillation pipeline:
- Student questionnaire with personality & teaching style tag libraries
- Subject-specific extraction templates for 7 subjects
- 5-layer personality model (Core → Identity → Expression → Decision → Interaction → Boundaries)
- Incremental merge and correction handlers

**10 Python tools** handle data and files:
- 4 chat parsers (WeChat, QQ, Feishu, Email)
- Auto-collectors for Feishu (3 methods) and DingTalk
- Skill file writer and version manager

## vs. colleague-skill

| | colleague-skill | teacher-skill |
|---|---|---|
| Target | Colleagues | Teachers |
| Dimensions | 2 (Work + Persona) | **3 (Teaching + Persona + Knowledge)** |
| Data Sources | Feishu, DingTalk, Slack | Feishu, DingTalk, **QQ, WeChat** |
| Users | Professionals | Students |
| Subject Templates | None | **7 subject-specific templates** |

## Contributing

Contributions welcome! You can add subject templates, improve prompts, add new data parsers, or submit example teachers.

## License

MIT License
