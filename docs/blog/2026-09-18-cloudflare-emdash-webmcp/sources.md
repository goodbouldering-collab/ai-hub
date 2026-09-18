# 公式情報と事実確認

確認日：2026-09-18（JST）。検索結果だけでなく、以下の公式発表・公式ドキュメント本文で確認。本文は原文の転載ではなく、複数資料から必要な論点を整理したオリジナル原稿。

| 出典 | 発表日・扱い | 支える事実 |
|---|---|---|
| [Cloudflare WebMCP](https://blog.cloudflare.com/webmcp/) | 2026-08-06の発表 | 開発者プレビュー。ページへブリッジを注入。発表時はContent CredentialsとSite MCP Serverの2パック。後者は既存のMCPサーバーに接続する。対応ブラウザが必要。元サイトのコード変更は不要という設計。 |
| [EmDashの発表](https://blog.cloudflare.com/emdash-wordpress/) | 2026-04-01の発表 | WordPressの精神的後継という開発元の位置づけ。独立したコード、オープンソース。Cloudflare以外でも動作可能。発表時のv0.1.0を現行版とは記載しない。 |
| [EmDash MCP仕様](https://docs.emdashcms.com/reference/mcp-server/) | 現行ドキュメントを確認、更新日断定なし | 管理用エンドポイント `/_emdash/api/mcp`、認証必須、トークンスコープとユーザー権限、記事取得・編集・公開・予約。セッションCookieだけでは認証不可。 |
| [EmDash AI Tools](https://docs.emdashcms.com/guides/ai-tools/) | 現行ドキュメントを確認 | 対応AIクライアントとEmDashを接続するための案内。 |
| [Cloudflare自社ブログのEmDash移行](https://blog.cloudflare.com/cloudflare-blog-uses-emdash/) | 発表2026-08-24、移行2026-08-12 | 記事検索・取得等を提供する読者向けMCPと、著者が利用するEmDashの管理MCPを区別。 |
| [Cloudflare OS](https://blog.cloudflare.com/cloudflare-os/) | 2026-08-05の発表 | 組織向けAIワークスペース、アプリ、アクセス統制、オープンソース。既存MCPはMCP Server Portals経由でも接続。PC用OSの置き換えではない。 |
| [EmDashのCloudflare導入](https://docs.emdashcms.com/deployment/cloudflare/) | 現行ドキュメントを確認 | AI Searchにはプラグイン登録、接続設定、対象コレクション指定、初回同期が必要。単なるホスティングで全機能が有効にはならない。 |

## 書き分けた点

- 発表時点と調査時点：WebMCPは「8月6日に開発者プレビューを発表」と記載。すべてのアカウント・プラン・ドメイン（workers.devを含む）で利用できるとは主張しない。
- 公開閲覧と管理操作：読者向け記事検索MCPとEmDash管理MCPは別。管理用エンドポイントを匿名で公開する提案はしない。
- WebMCPのブリッジとEmDashの直結：認証仕様を調整せず両者がそのままつながるとは記載しない。
- Cloudflare OSとEmDashの組み合わせ：公式の一括自動連携としては未確認。可能性を示す設計・活用案と明示。
- 認知・集客：MCPやWebMCPは検索順位、AIへの掲載、AI学習、予約、問い合わせ削減の成果を保証するものではない。
- 架空例：夜9時半の運営者、講座の問い合わせ文、作業例は説明用。実際の顧客発言や導入実績ではない。
- WordPress：移行の選択肢として説明。既存プラグインやテーマの無変更互換、全面的な置き換えを断言しない。
- 課金：料金の数値、完全無料、費用削減率を記事に入れていない。

## 調査の限界

各製品の公式説明に基づく解説であり、このAI相談サイトでMCP、EmDash、Cloudflare OSを稼働させた実証ではない。Cloudflare管理画面や外部サービスの設定は変更していない。
