# tests/test_email_parser.py
"""Tests for email_parser.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from email_parser import parse_email_file


class TestParseEmailFile(unittest.TestCase):
    def setUp(self):
        self.fixture_path = os.path.join(
            os.path.dirname(__file__), 'fixtures', 'email_sample.txt'
        )

    def test_parses_txt_file(self):
        messages = parse_email_file(self.fixture_path)
        self.assertEqual(len(messages), 1)

    def test_extracts_content(self):
        messages = parse_email_file(self.fixture_path)
        self.assertIn('明天', messages[0]['content'])

    def test_classifies_notice(self):
        messages = parse_email_file(self.fixture_path)
        self.assertEqual(messages[0]['category'], '通知')

    def test_message_has_required_fields(self):
        messages = parse_email_file(self.fixture_path)
        msg = messages[0]
        self.assertIn('sender', msg)
        self.assertIn('subject', msg)
        self.assertIn('content', msg)
        self.assertIn('category', msg)


if __name__ == "__main__":
    unittest.main()
