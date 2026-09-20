# 講師写真の復元 — 2026-09-20

ユーザーが選択した「黒い服で、背後に照明が写る実写の講師写真」をトップと自己紹介ページへ復元。使用画像は既存の `site/static/img/speaker-portrait-v2.webp`（1024×1024）。画像ファイルは加工せず、既存のガラス調フレームにobject-fit:coverで収める。

変更は2ページの講師画像タグのみ。CSS・本文・リンク・Instagram・他の画像・Worker本体は変更しない。通常ビルドにも `core/art_direction.py` で同じ写真を適用する。

公開物は `scripts/build_speaker_photo_release.py --baseline <warm-line-release> --output <new-release>` で生成する。基準はmain `5c3b88c703fa9c0588c4492b879724039bb6e5cb`、Cloudflare版 `7984ba41-86f0-4b28-9b45-0facad4721fe`。基準マニフェスト、全配信ファイル、ランタイム、コンパイル済みWorker、写真のSHA-256を照合する。

ローカル検証: 既存6テスト成功、変更がindex.htmlとspeaker.htmlの画像タグだけであることを検査、他511ファイルとWorker同一。ユーザー指定のアプリ内ブラウザでPC1365px・モバイル390pxの講師画像と横はみ出しを確認。

main統合後に登録公開元で再生成し、Cloudflareガード通過後にデプロイ。公開後は `verify_warm_line_live.py` の37項目と画面を確認し、リリースフォルダにSHA・PR・本番検証を保存する。
