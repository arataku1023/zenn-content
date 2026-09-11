# 初回セットアップ（本人作業）

4 つとも 1 回だけ。以降はルーチンが下書きを自動で出す（公開は人が行う。README の公開ルール参照）。

進捗（2026-09-12）: 1 GitHub ✅ / 2 Zenn 連携 ✅ / 3 Threads トークン ✅（Meta アプリ zenn-threads-poster、テスター @takuyamaaaaaan）/ 4 Claude Code: GitHub 連携 ✅・環境変数 ✅ / テスト投稿 ✅ / ルーチン2本作成 ✅（README 参照）

## 1. GitHub にリポジトリを作って中身を上げる

1. https://github.com/new で `zenn-content` を Public で作成（README は追加しない）。
2. このフォルダ（`C:\Users\arata\zenn-content`）を上げる。どちらか:
   - **A. git を入れて push**（Claude Code 側で以降の更新もできる）
     ```
     winget install --id Git.Git -e
     ```
     インストール後、ターミナルを開き直して Claude に「push して」と言えば残りは Claude がやる（初回 push 時にブラウザで GitHub ログインが 1 回出る）。
   - **B. Web からアップロード**: リポジトリページ → Add file → Upload files に `articles/ scripts/ README.md .gitignore` をドラッグ。

## 2. Zenn とリポジトリを連携する

1. https://zenn.dev/ に GitHub でログイン。
2. https://zenn.dev/dashboard/deploys → 「リポジトリを連携する」→ `zenn-content` を選択。
3. 連携後、`articles/*.md` の `published: true` を push すると公開される。

## 3. Threads API のトークンを作る

1. https://developers.facebook.com/ → My Apps → Create App。
   - ユースケース: **Threads API** を選ぶ（「Access the Threads API」）。
2. アプリのダッシュボード → Use cases → Threads API → Settings で権限を確認:
   `threads_basic` `threads_content_publish` `threads_manage_insights` にチェック。
3. App settings → Basic → **App Secret** を控える。
4. Threads アカウントをテスターに追加:
   - App roles → Roles → Add People → Threads Tester → 自分の Threads ユーザー名。
   - Threads アプリ側: 設定 → アカウント → Web サイトの権限 → 招待を承認。
5. Use cases → Threads API → Settings → **User Token Generator** → Generate Token → 短期トークンをコピー。
6. 長期トークン（60 日有効）に交換:
   ```
   python scripts/threads_token.py exchange --short 短期トークン --secret APP_SECRET
   ```
   出力の `access_token` を控える。
7. 動作確認（1 件テスト投稿される）:
   ```
   $env:THREADS_ACCESS_TOKEN="長期トークン"; python scripts/threads_post.py --text "テスト投稿"
   ```

## 4. Claude Code クラウド環境に設定する

1. https://claude.ai/code → 設定 → GitHub 連携で `zenn-content` を許可（ルーチンが push できるようにする）。
2. 環境（Environments）→ 使う環境の環境変数に追加:
   - `THREADS_ACCESS_TOKEN` = 長期トークン
3. ここまで終わったら Claude に「Threads と Zenn の設定終わった」と言う。ルーチンの組み込みは Claude がやる。

## トークンの寿命

長期トークンは 60 日で失効する。週次ルーチンに `threads_token.py refresh` を入れ、更新後の値を環境変数に入れ直す。
（環境変数の書き換えはルーチンからできないため、更新後の値は週次レポートに出す。月 1 回、貼り直しが要る。）
