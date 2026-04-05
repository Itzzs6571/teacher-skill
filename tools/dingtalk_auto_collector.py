#!/usr/bin/env python3
"""
dingtalk_auto_collector.py — Collect teacher data from DingTalk via API.

Attempts to collect group messages and documents via the DingTalk Open API.
When API access is denied or rate-limited, automatically falls back to
Playwright browser scraping using the existing DingTalk login session.

Requires:
    pip install requests
    # For browser fallback:
    pip install playwright && playwright install chromium

Usage:
    python3 dingtalk_auto_collector.py \\
        --app-key <key> \\
        --app-secret <secret> \\
        --output output.json
"""
import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Collect teacher data from DingTalk (API with browser fallback).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '--app-key',
        required=True,
        help='DingTalk app key (from DingTalk Open Platform developer console)',
    )
    parser.add_argument(
        '--app-secret',
        required=True,
        help='DingTalk app secret (from DingTalk Open Platform developer console)',
    )
    parser.add_argument(
        '--output',
        default='dingtalk_output.json',
        help='Output JSON file path (default: dingtalk_output.json)',
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print('Not yet implemented. Coming soon.')
    print(f'Would collect from DingTalk with app-key={args.app_key}')
    print(f'  Will try API first, fall back to browser scraping if API fails')
    print(f'  output: {args.output}')
    sys.exit(0)


if __name__ == '__main__':
    main()
