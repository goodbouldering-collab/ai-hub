# 今日のAIニュース5のCodex導入を短くする

`/ai-news/` のCodex冒頭を「Codex新機能と活用例」と更新日だけにする。
導入文、公式情報の確認期間、今回の要点と3項目を削除する。
ニュース5件、機能別の活用例4件、リンク、レイアウト、CSS、管理/APIは保持する。

公開記事の既存 `dateModified`（2026-09-14）を更新日に表示する。
今回の表示修正をニュース内容の再確認・更新として扱わない。
自動記事更新は `render_header` を共用し、実際の記事更新日を渡す。

## 公開元と再現

中央台帳の登録公開元は `work/genspark-profile-edit/cloudflare-runtime`。
元の通常作業フォルダには別作業の変更があるため編集しない。

配信中のsource `1a28cf5e4f67f9257f655a8790ba987a3f0dbb3a`、
Cloudflare version `16685c01-2f38-41a3-9d2c-7da45fc495a9` の保存済み配信データを使う。
`deployment/codex-header/baseline.json` に固定したmanifestハッシュ、
全公開資産とruntimeのハッシュを確認してから新しい出力先へコピーする。

```powershell
python scripts/build_codex_header_release.py --output .editorial-release-codex-header-20260918
```

ビルドは `ai-news/index.html` の導入部分だけを変更し、それ以外の資産と
runtimeがバイト単位で同じでなければ停止する。コミット・PR統合後の確定SHAで再生成し、
登録cwdで中央ガードを通して既存のWrangler設定からCloudflareへ公開する。

## 検証

- 記事更新の既存unittest 30件が成功。
- ビルドの変更資産は `ai-news/index.html` 1件。
- ニュース5件とCodex活用例4件のHTMLが変更前と同一。
- 見出しと更新日以外の導入文・箇条書きがないことをDOMで確認。
- 本番の変更前HTTP検証17項目が保存済み配信データと一致。
- 公開後は `scripts/verify_editorial_live.py` で同じ17項目と配信ハッシュを照合し、
  新しい見出し・更新日・ニュース5件を本番HTMLで確認する。

ブラウザは「AI相談 - Chrome.lnk」がProfile 1を指すことまで確認。
今回のツールから同プロフィールへの接続は確認できていないため、
PC/iPhoneの目視確認はHTTP・DOM確認とは別の未確認項目として残す。
公開SHA、PR、Cloudflare version、HTTP結果はリリース出力内の
`production-summary.json` に記録する。
