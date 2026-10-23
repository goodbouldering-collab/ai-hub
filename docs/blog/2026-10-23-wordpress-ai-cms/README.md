# WordPressからAIで育てるサイトへ — 制作・レビュー
最終更新：2026-10-23。AI相談の記事公開準備。2026-10-23に追加編集とデプロイを本人承認。公開実績は登録公開元の工程記録で確認する。

## 完成物
- content/blog/2026-10-23-wordpress-ai-cms.md：公開用編集ソース。
- site/static/img/wordpress-ai-cms-*.png：オリジナル図版4点。
- image-prompts.json：制作に使ったプロンプト。
- scripts/build_wordpress_ai_cms_release.py：現行資産を保持する公開用ビルダー。
- deployment/wordpress-ai-cms/baseline.json：公開基準の資産ハッシュとWorkerハッシュ。
- 初回レビュー用HTML、JSON、画像コピーは主作業フォルダ docs/blog/2026-10-23-wordpress-ai-cms/ に保管。公開正本は上記Markdownと画像。

## 編集方針
対象は、WordPressの保守で発信が止まる小規模事業者。1ページをAIと試作することが主CTA。
本人提供の主張「自分で移行し保守できるならCMSを必ず乗り換える必要はない」を軸にした。
「少し教えてないように」は、手順をすべて網羅せず全体像と依頼例を少し紹介する意図と解釈。
教室の話は明示した架空例。実在顧客、本人の移行実績、SEO効果、所要時間を創作しない。
EmDashにもMCP/CLIがありCodexから操作できる。「AIが使えない人向け」は修正。
安全・無料・検索順位上昇を保証せず、PHP更新と移行、静的配信と管理処理、ブログ公開とSNS投稿を分離した。

## タイトル案3つ
1. WordPressの更新が怖い人へ。AIと作る、身軽なホームページ（初期推奨）
   対象：小規模事業者。悩み：更新への不安。利益：保守対象を見直せる。CTA：1ページを試作。検索：WordPress 移行 PHP AI。地域の教室にも当てはまるが地名は詰め込まない。
2. お知らせを書きたいだけなのに。PHPの問題から考えるホームページの持ち方
   対象：非技術者。悩み：告知が進まない。利益：直す場所が分かる。CTA：PHP対応確認。実話未提供のため架空例であることを明示。
3. EmDashへ移る前に考えたい。Codexで育てる自分用CMSという選択
   対象：AIでサイトを作れる人。悩み：次のCMS選び。利益：AIとの併用も含め比較できる。CTA：必要機能を整理。検索：EmDash Codex CMS 比較。AI相談の実用的な判断支援として執筆。

## H2構成案3組
A（採用）：
1. PHPの問題は、WordPressの更新ボタンだけでは解決しない — 緊急対応と移行検討を分ける。
2. EmDashもAIで動かせる。選ぶ基準は「誰が、何を更新するか」 — 自作と既製CMS、無料範囲を比較する。
3. ブログもリールも一つの管理画面へ。まず1ページから移そう — 管理設計、指示例、移行とSEOを説明する。

B：①教室の告知が更新通知で止まったら ②PHPを直してからサイトの必要機能を絞る ③記事と動画を一つの管理画面で準備する ④元の記事とURLを保って引っ越す。
C：①WordPressを続けるか自作するか ②EmDashとCodexは併用できる ③無料の範囲と保守責任を確かめる ④移行前に確認したいSEOとSNS投稿。

最終タイトル候補は「WordPressの引っ越し先は、別のCMSとは限らない。AIと育てる自分のホームページへ」「ホームページの更新で止まらない。AIと作る自分用CMS入門」「PHPの問題を機に考える、WordPress移行とAI運用の始め方」の3つ。
最初を採用。恐怖だけで引きつけず、本人の主張と読者が選べる道を明示できるため。
最終H2はA、標準注記は「※内容は運営者が考え、AIで整えています。」。

## 根拠（2026-10-23閲覧）
- PHP Group、2026-10-21：二つのRCE、対象環境、修正版、提供元のバックポート。https://www.php.net/archive/2026.php#2026-10-21-5
- ENISAほか、2026-10-21：ホスティング提供者との連携と更新の呼びかけ。https://www.enisa.europa.eu/news/joint-statement-on-critical-php-vulnerabilities
- EmDash公式、更新日本文未確認：MCP、Codex接続、内容編集・公開など。https://docs.emdashcms.com/guides/ai-tools/
- Cloudflare、更新日本文未確認：静的アセットの無料リクエストとWorker処理の別料金。https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/
- Google、更新日本文未確認：検索対象と読者に分かりやすいサイト作り。https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=ja
- Google、更新日本文未確認：URL移行、転送、一時的順位変動。https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes?hl=ja
- Meta公式Postman資料：API投稿対象、リール投稿。検索索引の公式本文抜粋で確認。動的ページの全本文再取得はできず、詳細な権限名・数値・投稿上限は記事に書かない。https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-1ff01566-3509-48bd-a0f4-8571a91ccfdf
- Meta開発者ページはHTTP 429で取得不可。https://developers.facebook.com/docs/instagram-platform/content-publishing/
- Wordfence検証記事は取得不可のため本文根拠に不使用。
- 自作を推奨する条件と管理画面構成は編集提案。移行、Codex接続、CMS、Instagram実投稿を今回実行検証したものではない。

## デザインと検証範囲
紙の質感、紺・くすんだ青・黄土色で、保守の不安より「仕組みを理解できる」印象を優先。警告色・攻撃者イメージ中心の方向を見送った。
冒頭は所有感、各章はPHPの層、二つの操作入口、発信フロー。説明図として読めるラベルを優先。
既存ブラウザの接続先は別事業のタブが中心。C:\Users\yui\Desktop\AI相談 - Chrome.lnkは実在確認済みだがnative操作が無効なため起動・選択できず、ローカル閲覧はIABを利用した。
生成画像は1672×941。PHP図のサービス名称・記号は説明対象の識別であり、公式図や提携の表示ではない。

## 公開時の引渡し
2026-10-23の追加指示で直接公開を承認済み。再承認待ちは不要。
GBP：既存記事制作記録の候補プロフィールID 8474055285715858305は、今回の管理アクセス・対象一致を未確認。プロフィール不存在とは扱わない。未投稿。
GBP告知案：「ホームページを更新したいだけなのに、保守で手が止まる。PHPの問題への対応と、AIで自分のサイトを育てる方法を整理しました。EmDashとの比較、無料で始められる範囲、ブログとリールの管理、SEOを守る移行のポイントを紹介します。」
画像：hero。公開予定URL：https://aiclimb.aiclimb.workers.dev/blog/2026-10-23-wordpress-ai-cms.html 。到達検証後にGBP告知へ使用する。
既存差分を保全。記事・画像・一覧・サイトマップが今回の公開対象。管理機能のコードは保持。

初回レビュー検証：IAB 1440×1000／390×844。画像4点の読込、横はみ出しなし、正確な著者注記、目次クリックによる移動を確認。Python 3.12.14、Markdown 3.10.2。
プレビュー：http://127.0.0.1:4423/ 。親PID59880、2026-10-27 11:05:35 +09:00まで。PC再起動等で停止する場合がある。


## 2026-10-23 公開承認と追加編集

本人の「AIなら、思い通りの引っ越しができるみたいなニュアンスも追加して、そしてデプロイして」により公開承認。記事・写真・URL・教室らしさを保ち、配置と管理画面を希望に合わせる具体例を追加。完全自動移植の保証にはしない。正本記事は content/blog/2026-10-23-wordpress-ai-cms.md、画像は site/static/img/wordpress-ai-cms-*.png。

公開時は scripts/build_wordpress_ai_cms_release.py を使用。登録公開元の固定済み現行771資産を基準に記事・画像4点を追加し、トップ・ブログ一覧・サイトマップのみを変更。公開結果は登録公開元 tmp/delivery/20261023-wordpress-ai-cms-release.json に保存する。Present.mdは既存の別作業と混ぜず現在地を更新する。

公開候補の検証：本番テンプレートで1440px/390px表示、画像4点読込、横はみ出しなし、追加ニュアンスを確認。Cloudflareランタイム7テスト成功。現在の本番トップ・ブログ一覧・サイトマップのハッシュが基準と一致。
検証Pythonは別PCの旧.venvが起動不可のため、tmp/wordpress-ai-cms-pythonに分離環境を作成。Python3.12、beautifulsoup4 4.15.0、Pillow13.0.0、PyYAML6.0.3、Markdown3.11.2。
