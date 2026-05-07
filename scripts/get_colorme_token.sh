#!/usr/bin/env bash
# カラーミー OAuth トークンを取得して ~/.claude/.env に保存するヘルパー。
#
# 事前準備（ユーザー手動・1分）:
#   1. https://api.shop-pro.jp/developers にログイン
#   2. 「アプリ追加」→ 名前=ai-hub-admin / リダイレクトURI=http://127.0.0.1:3000/callback
#      / スコープ=read_products, read_templates, write_templates
#   3. 表示された client_id と client_secret をコピーしておく
#
# 使い方:
#   bash scripts/get_colorme_token.sh
#
# このスクリプトがやること:
#   1. client_id / client_secret を対話的に受け取る
#   2. 認可URLを生成して標準のブラウザで開く
#   3. リダイレクト先 URL の code= をユーザーから貼り付けてもらう
#   4. /oauth/token に POST して access_token を取得
#   5. ~/.claude/.env に COLORME_ACCESS_TOKEN として保存
#   6. setup_admin_env.sh を呼んで Vercel に登録 + 再デプロイは別途

set -euo pipefail

ENV_FILE="${HOME}/.claude/.env"

read -p "client_id: " CID
read -p "client_secret: " CSEC

REDIRECT="http://127.0.0.1:3000/callback"
# スコープは認可URLで動的に要求する。write_products はグループ作成 (POST /v1/groups) に必須。
SCOPE="read_products%20write_products%20read_templates%20write_templates"
AUTH_URL="https://api.shop-pro.jp/oauth/authorize?client_id=${CID}&response_type=code&scope=${SCOPE}&redirect_uri=${REDIRECT}"

echo
echo "[*] 以下のURLをブラウザで開いて「許可」してください:"
echo "    $AUTH_URL"
echo
# 環境別に開く（Windows / mac / Linux）
if command -v start >/dev/null 2>&1; then start "$AUTH_URL"
elif command -v open >/dev/null 2>&1; then open "$AUTH_URL"
elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$AUTH_URL"
fi

echo "[!] 許可後、ブラウザは http://127.0.0.1:3000/callback?code=XXX に飛びます"
echo "    (ページは「ページが見つかりません」と表示されますが正常です)"
echo "    URLバーから code= の値だけをコピーしてください"
echo
read -p "code: " CODE

echo
echo "[*] access_token を取得中..."
RESP=$(curl -s -X POST https://api.shop-pro.jp/oauth/token \
  -d "client_id=$CID" -d "client_secret=$CSEC" \
  -d "code=$CODE" -d "grant_type=authorization_code" \
  -d "redirect_uri=$REDIRECT")

TOKEN=$(echo "$RESP" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('access_token',''))")

if [ -z "$TOKEN" ]; then
  echo "ERROR: token 取得失敗"
  echo "応答: $RESP"
  exit 1
fi

echo "[+] 取得成功 (token len=${#TOKEN})"

if grep -q "^COLORME_ACCESS_TOKEN=" "$ENV_FILE"; then
  sed -i "s|^COLORME_ACCESS_TOKEN=.*|COLORME_ACCESS_TOKEN=${TOKEN}|" "$ENV_FILE"
  echo "[+] 既存の COLORME_ACCESS_TOKEN を更新しました ($ENV_FILE)"
else
  printf "\nCOLORME_ACCESS_TOKEN=%s\n" "$TOKEN" >> "$ENV_FILE"
  echo "[+] $ENV_FILE に追記しました"
fi

echo
echo "[*] 次のステップ:"
echo "    bash scripts/setup_admin_env.sh"
echo "    で Vercel に登録され、再デプロイ後に管理画面のカラーミー連携が有効化されます"
