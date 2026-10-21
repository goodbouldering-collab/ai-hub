# AI動画制作・投稿自動化講座

2026-10-21。旧reel自動投稿講座を改名し、動画の生成から投稿までを自動化する実践編へ説明・カリキュラムを更新。現在は準備中。予約ボタンは無効、販売Offerは非表示。Squareの商品ID・予約URL・外部設定、8,800円・120分は保持。

生成元は config/reel-course.json と core/reel_course.py。登録公開元の .ai-kids-toolkit-release-20261021-final/public を基準に、scripts/build_ai_video_course_release.py で対象カードと構造化データのみを更新。既存画像・770資産・Workerを保持。

検証：変更範囲・再適用一致・準備中の予約停止・Square設定一致を検査、Cloudflare7テスト成功。IABのPCと390pxでタイトル・本文・準備中表示と横はみ出しなしを確認。

本番結果は登録公開元 tmp/delivery/20261021-ai-video-course.json に保存。Present.mdは既存の別作業更新と混ぜず、登録公開元の現在地に今回の結果を追記する。受付開始は別途指示後に変更する。
