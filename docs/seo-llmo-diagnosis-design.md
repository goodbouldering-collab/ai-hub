# SEO・LLMO診断 — 設計メモ

作成日: 2026-08-20

## 目的

地域事業者、学校・福祉施設、個人事業主が「サイトはあるが検索やAI検索に伝わっているか分からない」という悩みを、URL入力から約1分で整理できる公開ページをAI相談に追加する。

- 誰に向けるか: 告知、集客、問い合わせ導線に不安がある小規模事業者・施設運営者
- 解決する悩み: SEOやLLMOの専門用語ではなく、見つけてもらう土台、信頼、次の行動の不足を知る
- 次の行動: 優先度の高い改善3項目を直す。必要ならAI相談へ持ち込む
- 媒体: AI相談の公開ページ `/seo-llmo-diagnosis/`
- 24時間後に残す一言: **検索順位の裏技ではなく、相手とAIに正しく伝わる土台から整える。**

## 公開体験

1. トップの「AI実践力診断」の直後に「SEO・LLMO診断」カードを置く。
2. 別ページで対象URL、主な相手、相手の悩み、ページで促したい行動、地域性を入力する。任意入力した3項目は公開本文との一致度として採点へ反映する。
3. Vercel Functionが公開HTML、`robots.txt`、`sitemap.xml`を一時取得し、既存SEO収益ループと同じ観点で点検する。
4. 100点の準備度、4領域、確認できた証拠、優先改善、限界を表示する。
5. 結果をコピー・印刷でき、AI相談の講習・相談へ進める。

点数は検索順位やAI回答への掲載確率ではない。公開ページから機械的に確認できる「準備度」と明記する。

## 診断の4領域

1. 発見・クロール: 到達、noindex、robots、sitemap、canonical、OAI-SearchBot
2. 内容の明確さ: title、description、H1、見出し、本文量、言語、画像alt
3. 信頼・主体: JSON-LD、Organization/Person/LocalBusiness、運営者・著者、所在地・連絡先、実績
4. 行動・計測: CTA、問い合わせ、料金、viewport、OGP、アクセス解析

`llms.txt` やAI専用Schemaを必須点にしない。Googleの通常SEOの基礎と、OpenAI検索用クローラを不必要に遮断していないかを分けて扱う。

## 安全・プライバシー

- 無料の公開診断では、入力URLと事業文脈を今回の応答だけに使い、DBへ継続保存しない。
- 管理者がCodex深掘りを実行した場合だけ、診断レポートを既存の保護relayへ一時保存する。画面上でもこの境界を明示する。
- `http` / `https` の標準ポートだけを許可する。
- localhost、プライベートIP、リンクローカル、予約IP、認証情報付きURLを拒否する。
- DNS確認を行い、リダイレクト先も毎回再検証する。
- DNSを3秒、診断全体を24秒の絶対期限で制限し、robots.txtとsitemap.xmlは並列取得する。
- 取得サイズ、時間、リダイレクト回数を制限し、本文そのものは応答へ返さない。
- Content-Type、HTML meta、XML宣言からUTF-8、EUC-JP、Shift_JIS等を判定してから解析する。
- Function内の回数制限は補助的な防御であり、複数インスタンスを横断する恒久制限ではない。本番で負荷が増えた場合はVercel Firewall等の外側の制限を追加する。
- 個人情報や管理画面URLを入力しない注意をフォームに表示する。

## Codex App Server

公開診断はApp Serverが停止中でも完結する。Codexによる深掘りは、同じ本番ページを開いた管理者だけが利用できる追加機能とする。

```text
公開ページ
  -> 管理者セッション確認
  -> 既存のVercel保護relay
  -> このPCのloopback bridge
  -> codex app-server
  -> 固定 seo-llmo-diagnosis Skill + 固定JSON Schema
```

- App ServerをVercelや公開インターネットへ配置しない。
- 管理者ログイン、PC bridgeのペアリング、既存HMAC relayを必須にする。
- ブラウザから任意のcwd、Skill path、CLI引数、コマンド、自由プロンプトを渡さない。
- 公開診断レポートと短い事業文脈だけを固定プロンプトへ変換する。
- Codex実行はread-only診断とし、修正・公開は別の明示依頼に分ける。

## 一次情報

- Google Search Essentials: https://developers.google.com/search/docs/essentials
- Google AI features and your website: https://developers.google.com/search/docs/appearance/ai-features
- Google AI optimization guide: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- OpenAI Publishers and Developers FAQ: https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
