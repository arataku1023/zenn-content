# zenn-content

Claude Code のクラウドルーチンでアフィリエイトブログ [kominka log](https://kominka-in.jp)（古民家・空き家・美容家電）の運用を自動化し、収益が出るかを検証するログを Zenn に公開し、Threads で告知するためのリポジトリ。
クラウドの Claude Code ルーチンがこのリポジトリに記事を push し、`scripts/` で Threads に投稿する。

題材の変遷: 2026-09-05〜11 は「note 有料記事の量産」を検証（10本で売上0、`articles/claude-code-note-factory-log-*.md` に記録）。2026-09-12 に題材をブログ運用に切り替え、新シリーズは `articles/claude-code-affiliate-log-NN.md`。
ブログ運用の仕組み・ルール・状況はすべて別リポジトリ [arataku1023/kominka-ops](https://github.com/arataku1023/kominka-ops)（private）にあり、両ルーチンはそれを読み取り専用の source として持つ。Zenn 記事にはブログ本体へのリンクを入れ、アフィリエイトリンク（楽天・A8・もしも）は貼らない。

## 構成

```
articles/   Zenn 記事（Markdown）。push すると Zenn に反映される（https://zenn.dev/banpeiyu）
books/      Zenn 本（有料本を出す場合）
scripts/    Threads 投稿・反応取得・トークン更新（Python 標準ライブラリのみ）
logs/       ルーチンが書く投稿ログ（threads_posts.jsonl）と反応データ（threads_metrics.json）
queue/      週次ルーチンが書く告知文（announce_NN.txt）。毎日ルーチンが公開検知後に使う
config/     threads_token_issued_at.txt = Threads トークンの発行日（再発行したら書き換える）
```

## ルーチン（claude.ai/code/routines）

| ルーチン | 時刻 (JST) | やること |
|---|---|---|
| Zenn検証ログ｜Threads日次投稿 | 毎日 08:00 | kominka-ops の docs と Threads の反応から実数を集め、Threads に1本投稿（型 A〜F。F はブログ新記事の紹介、週2回まで）し、logs/ を更新して push |
| Zenn検証ログ｜週次記事下書き | 月曜 07:00 | 週の数字（記事数・インデックス・GA4・楽天/A8 の実績）で検証ログ記事を `published: false` で書き、queue/ に告知文を置いて push |

数字の出どころ: kominka-ops の `docs/status.md` `docs/ga_latest.md` `docs/decisions.md`、運用台帳 Artifact の `revenue`（楽天の週次実績、人が入力）、`logs/threads_metrics.json`。取れない数字は「未計測」と書く。

Threads アカウント: @takuyamaaaaaan / Meta アプリ: zenn-threads-poster（App ID 1088936270287604）。
トークンは60日で失効。ルーチンが残日数を報告するので、警告が出たら Meta のトークン生成ツールで再生成し、環境変数と config/threads_token_issued_at.txt を更新する。

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
title: "記事タイトル（実数を1つ含む、40字以内）"
emoji: "🏠"
type: "idea"          # tech | idea
topics: ["claudecode", "アフィリエイト", "自動化", "wordpress"]
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
