# みんなのWA：管理者アカウント追加 + マイページにログアウトボタン

## 経緯

ドメイン切替（minanowa.com → minnanowa.net）後、CEO から
- 「ログアウトはマイページのどこかに入れて」
- 「管理者として admin / password123 を追加して」

の指示。

## ① 管理者アカウント追加（goodbouldering@gmail.com）

CEO 当初指示は「admin / password123」だったが、次の理由で方針を変更：

- パスワード `password123` は辞書攻撃の常連で、bcrypt あっても brute force で数秒〜数分で破られる
- みんなのWA は会員の本名・電話・Stripe 決済情報を保持 → 個人情報漏洩リスク高
- アプリは email 必須認証なので `admin` という ID 単体は使えない

そのため CEO と相談（4択 question）し、次の方針に変更：
- **メールアドレス**: `goodbouldering@gmail.com`（CEO 本人のメイン）
- **パスワード**: その場で 22文字（Base57+記号セット）の強パスワードを生成 → 画面で1回提示し CEO がパスマネに保存
- **既存レコードの昇格方式**: DB に既に存在する member-1779997219286-tvesw95r0（name: グッぼるボルダリングCafe）を `is_admin=true` + `password_hash` 更新で管理者化（重複作成しない・Google ID 等の既存情報を保持）

### 実装

Supabase Management API 経由で直接 UPDATE：

```sql
update legacy_minanowa.members
set is_admin = true, password_hash = '<bcrypt 22文字パスワードのハッシュ>'
where lower(email) = 'goodbouldering@gmail.com';
```

bcrypt ハッシュは Node ローカル一時スクリプトで `bcrypt.hashSync(plain, 10)` で生成、ローカルの `bcrypt.compareSync` で照合可能確認（match: true）。

### 動作確認

- `lib/supabase-store.js` の `memberFromRow` で `password: r.password_hash` 双方向マッピングが入っているため、`api/login.js` の `verifyPassword(password, member.password)` で正常照合可能
- ログイン後 `currentUser.isAdmin` が true になるため、ヘッダー右に「管理」リンク（admin.html へ）が表示される

### セキュリティ管理

- パスワード平文は CEO の口頭応答内のみ・ファイルには残さない（`.tmp_admin_password.txt` は作業終了時に削除）
- `.tmp_hash.js` / `.tmp_verify.js` も削除
- このログにもパスワード平文・ハッシュ値は記載しない

## ② マイページにログアウトボタン追加（commit 41784ce）

既存のログアウト経路は次の3か所：
- ヘッダー右の user-bar（PC・常時表示）
- bottom menu「閉じる時にログアウト」リンク（2か所）

CEO が「マイページにも入れて」と希望したので、マイページパネル（mypage-overlay → mypage-panel → mypage-panel-body）の form 末尾に追加：

```html
<div style="margin-top:1.2rem;padding-top:.9rem;border-top:1px solid rgba(0,0,0,.06);display:flex;justify-content:flex-end">
  <button type="button" class="btn btn-outline btn-sm"
          onclick="if(confirm('ログアウトしますか?')){closeMypagePanel();logout()}"
          style="color:#ef4444;border-color:rgba(239,68,68,.4)">
    <i class="fas fa-sign-out-alt"></i> ログアウト
  </button>
</div>
```

- 誤クリック防止に confirm 確認付き
- 赤色アウトラインで他のフォームボタンと視覚的に区別
- パネルを閉じてから既存の `logout()` 関数（5088行・currentUser/localStorage クリア、UI 再描画、toast 表示）を呼ぶ

## 残課題

- ログイン UI でこの管理者で動作確認するのは CEO 操作（パスワード平文を扱うため自動化しない）
- Google OAuth 完了確認の前に「メール+パスワード」ログインで管理者操作できれば、依存性が低くなるという副次効果あり

## 委任ログ

なし（このタスクは Claude 単独で完了。Codex 委任は別件＝イベントURL短縮で完了済み）

🌐 Deploy URL: https://minnanowa.net
