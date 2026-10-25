# 音声メモアプリ講座とコンパクトなブログ一覧

2026-10-25本人依頼。旧AIコーディング講習を最新ブログ「10時の会話が、10時のお客様の記録になる」を題材にした120分・8,800円の個別講座へ変更。

## 内容と判断

録音や文字起こしを、予約時間・顧客リストと結びつける小さなアプリをCodexで試作する。実際の受講者の声は作らず、メリット・当日の流れ・到達目標を具体的に示す。受講者はAIエージェント講習1回以上またはCodex基本操作ができる方。講習では匿名サンプルを使う。

## Square

既存サービスID S7GERYVDIPRV76DKXCC3WJWH、variation R4ZXWZBO2YHS3IVRK3JVK6SQ、location LWJNMP7EAN4GS。店舗表示名はNotエステ彦根だが、AI相談が従来からリンクする同じAI講習IDを取得・照合し、そのサービスだけ更新した。価格11000→8800 JPY、所要時間7200000msを維持。担当者、移行時間、公開範囲、予約可否、カテゴリ、税設定、画像は保持。

公式Catalog APIの完全置換仕様に従い全オブジェクトとversionを保持し、取得直後のversion一致を確認して更新。APIは説明の空行を正規化するため、再取得は空白正規化後の全文一致と公開予約画面の表示で確認。API資格情報は既存ローカル設定から内部でのみ利用し、原稿・ログ・Gitへ保存していない。

## サイトと再生成

core/voice_memo_course.pyをcore/square_menu.pyから呼び、日次生成時の巻き戻りを防ぐ。core/home_blog_layout.pyをニュース・ブログの再配置処理にも接続。ブログ記事・ニュースの件数／順序／公開日・配置は維持する。

直前の正常公開版10b9b0f3（SNS上部メニュー、管理Worker PR217を含む）の781資産をdeployment/voice-course/baseline.jsonで固定し、公開3HTMLとのハッシュ一致を確認。scripts/build_voice_course_release.pyはindex.htmlだけを変更し、他780資産とWorkerバイト列を保持する。公開前に統合SHAから同じ処理を再現する。

## 検証と記録

52 Python tests、verify_ai_news_feature --assets。IABで834pxブログ、1440px講座、390px講座と詳細開閉を確認。横はみ出しなし。公開予約画面で新しいタイトル・説明・8800円・2時間を確認。

作業証拠は事業ルートoutputs/voice-course-20261025。ローカルプレビュー http://127.0.0.1:4191/、親PID40232、2026-10-29 14:30:20 JSTまで（PC再起動・サーバー異常終了を除く）。公開・Git統合・Cloudflareガード・配信ハッシュ・APIの最終実績はdelivery記録とrelease-result.jsonを参照。
