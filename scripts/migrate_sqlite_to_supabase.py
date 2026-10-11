"""Retired one-time importer. Historical implementation remains in Git.

This entry point never loads .env, credentials, data/history.db, or a network SDK.
"""
import sys


def main() -> int:
    print('廃止済み: Supabaseへの履歴移送は実行しません。'
          'docs/2026-10-12-auxiliary-d1.md のD1移行手順を確認してください。', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())