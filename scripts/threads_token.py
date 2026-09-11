#!/usr/bin/env python3
"""Threads の長期トークン（60日有効）の発行と更新。

短期→長期:  python scripts/threads_token.py exchange --short SHORT_TOKEN --secret APP_SECRET
更新:       THREADS_ACCESS_TOKEN=... python scripts/threads_token.py refresh
    ※ 更新は発行から24時間以上経過した、まだ有効なトークンにのみ可能。
      週次ルーチンで refresh を回し、出力された新トークンを環境変数に入れ直す。
"""
import argparse
import json
import os
import urllib.parse
import urllib.request

BASE = "https://graph.threads.net"


def get(path, params):
    req = urllib.request.Request(f"{BASE}{path}?" + urllib.parse.urlencode(params))
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("exchange")
    ex.add_argument("--short", required=True)
    ex.add_argument("--secret", required=True)
    sub.add_parser("refresh")
    a = ap.parse_args()

    if a.cmd == "exchange":
        res = get("/access_token", {"grant_type": "th_exchange_token",
                                    "client_secret": a.secret, "access_token": a.short})
    else:
        res = get("/refresh_access_token", {"grant_type": "th_refresh_token",
                                            "access_token": os.environ["THREADS_ACCESS_TOKEN"]})
    # res = {"access_token": "...", "token_type": "bearer", "expires_in": 5183944}
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
