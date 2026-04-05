#!/usr/bin/env python3
"""
wechat_parser.py — Parse WeChat exported chat logs.

Supports txt format exported via WeChat backup or third-party tools.

Usage:
    python3 wechat_parser.py --input chat.txt --teacher-name "姚老师"
"""
import argparse
import json
import re
import sys


# Pattern: "2026-03-15 09:23:45 姚老师"
MSG_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+)$')

# Keywords for classification
NOTICE_KEYWORDS = ['作业', '通知', '明天', '带好', '考试', '放假', '提醒', '要求', '今天的']
ANSWER_KEYWORDS = ['试试', '你看', '先把', '再', '移项', '因为', '所以', '这样做', '思路', '方法', '解法']
KNOWLEDGE_KEYWORDS = ['公式', '定理', '推导', '证明', '规律', '口诀', '记住', '知识点', '概念', '定义']


def parse_wechat_txt(filepath: str, teacher_name: str | None = None) -> list[dict]:
    """Parse a WeChat txt export file into structured messages.

    Args:
        filepath: Path to the exported txt file.
        teacher_name: If provided, only return messages from this sender.

    Returns:
        List of message dicts with keys: timestamp, sender, content, category.
    """
    messages = []
    current_msg = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip():
                if current_msg is not None:
                    messages.append(current_msg)
                    current_msg = None
                continue

            match = MSG_PATTERN.match(line)
            if match:
                if current_msg is not None:
                    messages.append(current_msg)
                current_msg = {
                    'timestamp': match.group(1),
                    'sender': match.group(2),
                    'content': '',
                }
            elif current_msg is not None:
                if current_msg['content']:
                    current_msg['content'] += '\n' + line
                else:
                    current_msg['content'] = line

        if current_msg is not None:
            messages.append(current_msg)

    # Classify messages
    for msg in messages:
        msg['category'] = classify_message(msg['content'])

    # Filter by teacher
    if teacher_name:
        messages = [m for m in messages if m['sender'] == teacher_name]

    return messages


def classify_message(content: str) -> str:
    """Classify a message into categories by content analysis.

    Categories (in priority order):
    - 知识讲解: Contains knowledge teaching content (highest weight)
    - 答疑: Contains problem-solving guidance
    - 通知: Contains homework/schedule notices
    - 闲聊: Everything else (lowest weight)
    """
    content_lower = content.lower()

    # Check knowledge keywords first (highest priority)
    knowledge_score = sum(1 for kw in KNOWLEDGE_KEYWORDS if kw in content_lower)
    if knowledge_score >= 2 or (knowledge_score >= 1 and len(content) > 50):
        return "知识讲解"

    # Check answer keywords
    answer_score = sum(1 for kw in ANSWER_KEYWORDS if kw in content_lower)
    if answer_score >= 2 or (answer_score >= 1 and len(content) > 30):
        return "答疑"

    # Check notice keywords
    notice_score = sum(1 for kw in NOTICE_KEYWORDS if kw in content_lower)
    if notice_score >= 1:
        return "通知"

    return "闲聊"


def main():
    parser = argparse.ArgumentParser(description="Parse WeChat chat logs")
    parser.add_argument("--input", required=True, help="Path to exported txt file")
    parser.add_argument("--teacher-name", help="Filter by teacher name")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")

    args = parser.parse_args()
    messages = parse_wechat_txt(args.input, teacher_name=args.teacher_name)

    result = {
        "source": "wechat",
        "file": args.input,
        "teacher_filter": args.teacher_name,
        "total_messages": len(messages),
        "by_category": {},
        "messages": messages,
    }

    for msg in messages:
        cat = msg['category']
        result['by_category'][cat] = result['by_category'].get(cat, 0) + 1

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved {len(messages)} messages to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
