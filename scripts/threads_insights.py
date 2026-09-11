#!/usr/bin/env python3
"""直近の Threads 投稿とその反応（views / likes / replies / reposts / quotes）を JSON で出す。

環境変数: THREADS_ACCESS_TOKEN（threads_manage_insights 権限付き）, THREADS_USER_ID（任意）
使い方:  python scripts/threads_insights.py [--limit 25] > insights.json
"""
import argparse
import json
import os
import urllib.parse
import urllib.request

API = "https://graph.threads.net/v1.0"
METRICS = "views,likes,replies,reposts,quotes"


def get(url, params):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params))
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=25)
    a = ap.parse_args()
    token = os.environ["THREADS_ACCESS_TOKEN"]
    user_id = os.environ.get("THREADS_USER_ID") or get(f"{API}/me", {"fields": "id", "access_token": token})["id"]

    posts = get(f"{API}/{user_id}/threads", {
        "fields": "id,text,permalink,timestamp,is_reply_owned_by_me",
        "limit": a.limit, "access_token": token})["data"]

    out = []
    for p in posts:
        try:
            ins = get(f"{API}/{p['id']}/insights", {"metric": METRICS, "access_token": token})["data"]
            metrics = {m["name"]: (m.get("values", [{}])[0].get("value") if "values" in m else m.get("total_value", {}).get("value")) for m in ins}
        except Exception as e:  # 権限なし等
            metrics = {"error": str(e)}
        out.append({**p, "metrics": metrics})
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
