# Codexのプロンプト提案：制作・公開記録

最終更新：2026-10-17。本人から原稿の平易な整理とブログ投稿を依頼。

## 編集

対象はAIへの頼み方に迷う人。主題は「AIは、答えだけでなく頼み方も手伝ってくれる」。本人提供の実体験を主軸に、ブログ短縮の場面は説明用の例として明記。スマホ対応を推測させる記述は削除。体験を損なわず重複を削り、3章・約3分へ整理した。

タイトル候補：①次に頼みたいことが、もう出ている。Codexの「プロンプト提案」に驚いた（採用：本人の実感を維持）／②AIにどう頼むかで止まらない。Codexの次の一文が便利だった（負担軽減）／③Codexのプロンプト提案とは？「そう、それ」で進める新しい使い心地（入門・操作）。最終比較でも①が本文の体験に最も合う。

H2構成候補：A「次の言葉を提案→頼み方の負担軽減→自分で判断」（採用）、B「入力欄で驚いた→ブログ短縮の例→毎日の小さな停止が減る」、C「プロンプトとは→提案の取り込み方→使わない選択」。簡単な操作と提供条件を最終章へまとめ、別FAQの重複は設けない。

AI整文注記は `※内容は運営者が考え、AIで整えています。`。CTAは「次の作業で候補を読み、意図に合えば使ってみる」。ユーザー提供の体験以外の実績・効果数値は追加していない。

## 事実確認

- 2026-10-17確認：[OpenAI Composer predictions](https://help.openai.com/en/articles/20001601-composer-predictions-in-codex)。回答後に現在の会話から候補を提案、任意採用、Tabで取り込み、編集後に本人が送信。毎回表示されるとは限らない。個人Pro・18歳以上・対応モデルと会話のベータ機能。記事では変わり得る細かなモデル一覧を転載せず公式へ案内。
- ユーザーの原稿を本人提供の実体験として使用。ブログ短縮の例は実際の候補文として扱わない。
- ローカル既存資料には当機能の説明が見つからず、公式ヘルプで確認した。

## 画像

built-in image_genで4枚を生成。保存先 `site/static/img/blog-codex-prompt-{hero,section1,section2,section3}-20261017.png`。各H2直下にfigure・alt・説明を配置。実画面ではないことを明記。

共通プロンプト：Landscape 3:2 editorial illustration, refined layered paper cut art in ivory, muted teal and warm peach, soft natural shadows, minimal uncluttered composition for a Japanese beginner blog. No text, no letters, no numbers, no logos, no product screenshot.

- hero：A simple laptop with a blank rounded suggestion card appearing above its keyboard, and an abstract thought bubble gently aligning with the card. Communicate the words I was about to ask are already there.
- section1：A thought bubble and a matching suggestion card emerging from a laptop, representing that is what I wanted to ask next.
- section2：A tangled paper ribbon transforming into one neatly folded message card, representing making a vague wish into a clear instruction.
- section3：A hand choosing a single blank suggestion card beside a laptop, a small pencil next to it, representing reviewing and editing before sending.

## 検証・公開

- 登録公開元の直前リリース `.news-summary-course-note-release-20261017-final/public` を全ハッシュで固定。限定ビルドで記事・画像4枚を追加、トップ・ブログ一覧・sitemapだけを更新。その他759資産と管理Workerを保持。
- 既存編集・AIニュース本文を変更しない。ソースは独立worktree `work/codex-prompt-suggestions-20261017`。
- 関連25テスト（editorial_feed/authorship_note）とCloudflare公開経路検査成功。画像追跡検査は画像をstageした後に成功。
- 追加で実行した旧 `test_blog_freshness` は既定ブランチでも1失敗・2エラー。廃止済み `content/blog/codex-update-log.md` と旧一覧形式を前提にしており、登録公開元でも同じ結果を再現。今回触れない日次機能の既存課題として残す。今回の限定ビルドでは一覧順・注記・画像・canonical・追加資産・非対象資産保持を別途検証。
- プレビュー：127.0.0.1:4417、親PID54588、保持期限2026-10-19 12:24:32 JST。公開結果は今回のdelivery記録へ保存する。

## GBP 最新情報

対象は独立事業「AI相談」、既存記録のプロフィールID `8474055285715858305`。クライミングコンサルへ代替しない。10月11日記録は動画によるオーナー確認待ち。

今回、起動中のChrome接続を確認し、実在のAI相談デスクトップショートカットを起動したが、AI相談専用プロフィールの操作接続は得られなかった。現在のオーナー確認状態・投稿可否は未確認。存在なしとは扱わない。

告知案：『AIに何と頼めばいいか、考えて手が止まることはありませんか。Codexを使っていて、次に頼もうとした指示がもう入力欄に出ている体験に驚きました。便利なのは、文字数より「頼み方」を考える手間が減ること。使い方と気づきを、約3分の記事にまとめました。』

画像は本記事hero。記事公開後の正規URLを詳細ボタンに使用。接続・管理対象・投稿権限と重複を確認してから投稿する。現時点は未投稿。
