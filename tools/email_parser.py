#!/usr/bin/env python3
"""
email_parser.py — Parse email files (plain text, EML, MBOX).

Usage:
    python3 email_parser.py --input email.txt
    python3 email_parser.py --input mailbox.mbox
"""
import argparse
import email
import json
import mailbox
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wechat_parser import classify_message


def parse_email_file(filepath: str) -> list[dict]:
    """Parse an email file and extract messages.

    Detects format by extension: .eml, .mbox, .txt
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.mbox':
        return _parse_mbox(filepath)
    elif ext == '.eml':
        return _parse_eml(filepath)
    else:
        return _parse_txt(filepath)


def _parse_eml(filepath: str) -> list[dict]:
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        msg = email.message_from_file(f)
    return [_email_to_dict(msg)]


def _parse_mbox(filepath: str) -> list[dict]:
    mbox = mailbox.mbox(filepath)
    return [_email_to_dict(msg) for msg in mbox]


def _parse_txt(filepath: str) -> list[dict]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return [{
        'sender': '',
        'subject': '',
        'content': content,
        'category': classify_message(content),
    }]


def _email_to_dict(msg) -> dict:
    sender = str(msg.get('From', ''))
    subject = str(msg.get('Subject', ''))
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='replace')
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='replace')

    return {
        'sender': sender,
        'subject': subject,
        'content': body,
        'category': classify_message(body),
    }


def main():
    parser = argparse.ArgumentParser(description="Parse email files")
    parser.add_argument("--input", required=True, help="Path to email file")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()
    messages = parse_email_file(args.input)

    result = {
        'source': 'email',
        'file': args.input,
        'total_messages': len(messages),
        'messages': messages,
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
