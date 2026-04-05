# tests/test_wechat_parser.py
"""Tests for wechat_parser.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from wechat_parser import parse_wechat_txt, classify_message


class TestParseWechatTxt(unittest.TestCase):
    def setUp(self):
        self.fixture_path = os.path.join(
            os.path.dirname(__file__), 'fixtures', 'wechat_sample.txt'
        )

    def test_parses_all_messages(self):
        messages = parse_wechat_txt(self.fixture_path)
        self.assertEqual(len(messages), 7)

    def test_extracts_sender(self):
        messages = parse_wechat_txt(self.fixture_path)
        self.assertEqual(messages[0]['sender'], '姚老师')

    def test_extracts_content(self):
        messages = parse_wechat_txt(self.fixture_path)
        self.assertIn('作业', messages[0]['content'])

    def test_filters_by_teacher(self):
        messages = parse_wechat_txt(self.fixture_path, teacher_name='姚老师')
        self.assertEqual(len(messages), 4)
        for m in messages:
            self.assertEqual(m['sender'], '姚老师')


class TestClassifyMessage(unittest.TestCase):
    def test_classify_notice(self):
        self.assertEqual(classify_message("今天的作业：课本P52"), "通知")

    def test_classify_answer(self):
        self.assertEqual(classify_message("先把等式两边同时减去3，再移项。你试试看。"), "答疑")

    def test_classify_chat(self):
        self.assertEqual(classify_message("哈哈今天中午吃什么"), "闲聊")

    def test_classify_knowledge(self):
        self.assertEqual(classify_message("记住：移项要变号，这个公式的推导过程是这样的……首先我们把两边同时除以a"), "知识讲解")


if __name__ == "__main__":
    unittest.main()
