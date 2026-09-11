# zenn-content

Claude Code で note 記事量産を自動化した検証ログを Zenn に公開し、Threads で告知するためのリポジトリ。
クラウドの Claude Code ルーチンがこのリポジトリに記事を push し、`scripts/` で Threads に投稿する。

## 構成

```
articles/   Zenn 記事（Markdown）。push すると Zenn に反映される
books/      Zenn 本（有料本を出す場合）
scripts/    Threads 投稿・反応取得・トークン更新（Python 標準ライブラリのみ）
```

## 公開ルール（Zenn の AI コンテンツガイドライン対応）

Zenn はボットによる自動投稿・著者検証なしの大量投稿を禁止している（違反はアカウント凍結対象）。
そのため **ルーチンは `published: false` の下書きを push するだけ**にし、公開は必ず人が行う。

1. ルーチンが `articles/*.md` を `published: false` で push する（週 1 本）
2. 本人が内容を読み、事実と数字を確認する
3. `published: true` に変えて push すると公開される

Threads の告知投稿は Zenn の規約対象外なので、そちらは全自動でよい。

## Zenn 記事のフロントマター

```markdown
---
title: "記事タイトル"
emoji: "🛠"
type: "tech"          # tech | idea
topics: ["claudecode", "note", "自動化"]
published: false      # true にした push で公開
published_at: "2026-09-13 07:00"   # 任意。未来日時なら予約公開
---
```

- ファイル名（slug）は英小文字・数字・ハイフンで 12〜50 文字。
- 画像は `/images/` 配下に置き `/images/xxx.png` で参照する。

## Threads 投稿

```
THREADS_ACCESS_TOKEN=xxx python scripts/threads_post.py --text "本文" --link https://zenn.dev/...
THREADS_ACCESS_TOKEN=xxx python scripts/threads_post.py --thread post.txt   # "---" 区切りでツリー投稿
python scripts/threads_post.py --text "本文" --dry-run                       # 送信せず内容確認
```

- 1 投稿 500 字まで。1 日 250 投稿が上限。
- 反応取得: `python scripts/threads_insights.py > insights.json`
- トークン更新（60 日で失効、週 1 回）: `python scripts/threads_token.py refresh`

## 必要な環境変数（クラウド環境に設定）

| 変数 | 内容 |
|---|---|
| THREADS_ACCESS_TOKEN | 長期トークン（threads_basic, threads_content_publish, threads_manage_insights） |
| THREADS_USER_ID | 任意。未設定なら /me から自動取得 |
