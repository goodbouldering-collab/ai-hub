# Codexのリモート共同開発ガイド

対象: 高校生・初めて友達と開発する人。悩み: 同じ「リモート」に見える3方式を選べず設定で迷う。
持ち帰る一言: 画面・AI・コマンド。つなぐものを選んで、変更は分けて合わせる。
行動: READMEを1行変更し、各自のアカウントでPRレビュー・統合まで練習する。

2026-10-03にOpenAI公式Remote connections / CLI / Auth / Pricing、Google Chrome Remote Desktop、Microsoft RDP / OpenSSH、Ubuntu OpenSSH、OpenBSD ssh、Tailscale、GitHub PR公式を確認。個々の主張に対応するリンクは記事内に配置した。
公式資料に基づく設定ガイド。全OSや実アカウントで接続を実測した報告ではない。学校や組織の制限・段階提供を明記。Remoteは同一アカウント・ワークスペース、SSHは別の実行環境、共同開発は各自の認証とGitHubレビューに分離する。第三者へ認証情報を渡す手順はない。

## 図解
imagegenで5枚作成。横長、白い紙調、濃紺の線画、青緑とコーラルのアクセント、日本語の見出し、文字を少なくする方針。
- hero: 画面・AI・コマンド／つなぐものが違う。3方式を横並びで比較。
- desktop: 友達に画面を見てもらう。本人の画面と一時的なサポートを描く。
- remote: スマホから、家のCodexへ／同じアカウントで接続。スマホと起動中のPCを接続。
- ssh: 手元で指示、接続先で実行。キーボード側と実行PCを区別。
- team: 別々に作って、確認して合わせる。2人の変更をPRで合わせる。
元画像はsite/static/img/blog-remote-guide-*-20261003.png。別記事には流用していない。

## 再生成・検証
scripts/build_remote_guide_release.py --baseline <検証済み537資産のpublic> --output <新しい出力先>
baseline契約はdeployment/cloudflare-blog/remote-guide-20261003.json。534既存資産を不変で保持し、ホーム新着、ブログ一覧、sitemapだけ更新。記事と5画像を追加。immutable資産はハードリンクのため直接編集しない。
記事の見出し、図、代替文、canonical、OGP、JSON-LD、著者注記、ページ内リンク、画像読込、PC・390px表示を確認。
既存test_blog_freshnessのうちcodex-update-log.mdを要求する2件は、mainに当該ファイルが存在しない既存不整合。今回の変更と独立。残る12件と今回の生成アサーションを実施する。既存失敗を成功扱いしない。

ローカル確認: http://127.0.0.1:4027/ 、親PID 45652、2026-10-05 12:53:06 JSTまで。作業コピーはその期限まで保持。
外部SNS・GBPへの投稿なし。ユーザーPCの認証・SSH・RDP設定変更なし。
