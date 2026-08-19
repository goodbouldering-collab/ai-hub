# SEO・LLMO診断 — 実装計画

作成日: 2026-08-20

1. 失敗するテストを追加する。
   - 公開URL正規化とlocalhost・私設IP・危険なポートの拒否
   - HTML、robots、sitemapの診断と透明な点数・優先度
   - 公開ページ、フォーム、トップ導線、サイトマップ
   - 管理者だけが固定SEO診断SkillをApp Serverへ渡せる境界
2. 依存なしの診断コアとVercel API Routeを実装する。
3. 独立ページのHTML、CSS、JS、結果表示、コピー・印刷を実装する。
4. トップのAI実践力診断直後へSEO・LLMO診断カードを追加する。
5. `seo-llmo-diagnosis` Skill、出力Schema、App Server manager、relay許可パスを実装する。
6. Skill検証、Node/Pythonテスト、静的ビルドを通す。
7. ローカルHTTPでPC・390px、キーボード、横あふれ、コンソール、APIエラー表示を確認する。
8. commit、push、Vercel本番反映、公開ページ・API・トップ導線を実URLで確認する。
