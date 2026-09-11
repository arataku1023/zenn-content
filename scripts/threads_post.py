#!/usr/bin/env python3
"""Threads API で投稿する（標準ライブラリのみ、pip不要）。

環境変数:
  THREADS_ACCESS_TOKEN  長期トークン（必須）
  THREADS_USER_ID       Threads ユーザーID（省略時は /me から取得）

使い方:
  python scripts/threads_post.py --text "本文" [--link URL] [--reply-to MEDIA_ID] [--dry-run]
  python scripts/threads_post.py --file post.txt        # 1投稿=ファイル1つ
  python scripts/threads_post.py --thread thread.txt    # "---" 区切りで連投（ツリー）

出力: 投稿した media_id を JSON で標準出力に出す。
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://graph.threads.net/v1.0"
MAX_LEN = 500


def _call(method, url, params):
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"Threads API error {e.code}: {body}")


def get_user_id(token):
    me = _call("GET", f"{API}/me", {"fields": "id,username", "access_token": token})
    return me["id"], me.get("username")


def post_text(token, user_id, text, link=None, reply_to=None, dry_run=False):
    if len(text) > MAX_LEN:
        raise SystemExit(f"本文が {len(text)} 字で上限 {MAX_LEN} 字を超えています")
    params = {"media_type": "TEXT", "text": text, "access_token": token}
    if link:
        params["link_attachment"] = link
    if reply_to:
        params["reply_to_id"] = reply_to
    if dry_run:
        print(json.dumps({"dry_run": True, "text": text, "link": link, "reply_to": reply_to}, ensure_ascii=False))
        return None
    container = _call("POST", f"{API}/{user_id}/threads", params)
    time.sleep(3)  # コンテナ生成後は数秒待つのが公式推奨
    published = _call("POST", f"{API}/{user_id}/threads_publish",
                      {"creation_id": container["id"], "access_token": token})
    return published["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--thread", help="'---' 区切りで複数投稿をツリーにする")
    ap.add_argument("--link")
    ap.add_argument("--reply-to")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    token = os.environ.get("THREADS_ACCESS_TOKEN")
    if not token and not a.dry_run:
        raise SystemExit("THREADS_ACCESS_TOKEN が未設定です")

    if a.thread:
        parts = [p.strip() for p in open(a.thread, encoding="utf-8").read().split("\n---\n") if p.strip()]
    elif a.file:
        parts = [open(a.file, encoding="utf-8").read().strip()]
    elif a.text:
        parts = [a.text]
    else:
        raise SystemExit("--text / --file / --thread のいずれかを指定してください")

    user_id = os.environ.get("THREADS_USER_ID")
    if not user_id and not a.dry_run:
        user_id, _ = get_user_id(token)

    ids = []
    reply_to = a.reply_to
    for i, text in enumerate(parts):
        link = a.link if i == 0 else None
        mid = post_text(token, user_id, text, link=link, reply_to=reply_to, dry_run=a.dry_run)
        ids.append(mid)
        reply_to = mid
        if mid and i < len(parts) - 1:
            time.sleep(5)
    print(json.dumps({"media_ids": ids}, ensure_ascii=False))


if __name__ == "__main__":
    main()
