#!/usr/bin/env bash
# AIハブ管理画面 (/admin) 用の Vercel 環境変数を一括登録するスクリプト。
#
# 使い方:
#   1. ~/.claude/.env に必要なキーを書く（例 .env.example 参照）
#   2. bash scripts/setup_admin_env.sh
#
# - 既存の同名 env は一旦削除してから登録し直す（上書き）
# - production / preview / development の3環境すべてに登録する
# - VERCEL_TOKEN は ~/.claude/.env から自動で読む

set -euo pipefail

ENV_FILE="${HOME}/.claude/.env"
PROJECT_ID="prj_e7vh73eF0KZpm8C49esnILvHO98o"  # ai-hub-jp
TEAM_HINT=""  # 必要なら ?teamId=team_xxx を入れる

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE が見つかりません" >&2
  exit 1
fi

# .env を読み込み (シェル変数化)
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

VT="${VERCEL_TOKEN:-}"
if [ -z "$VT" ]; then
  echo "ERROR: VERCEL_TOKEN が ~/.claude/.env にありません" >&2
  exit 1
fi

# 登録対象の env キー
KEYS=(
  ADMIN_USER
  ADMIN_PASS
  COLORME_ACCESS_TOKEN
  COLORME_PREVIEW_TEMPLATE_ID
  COLORME_LIVE_TEMPLATE_ID
  ANTHROPIC_API_KEY
  OPENAI_API_KEY
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
  SUPABASE_BUCKET
)

# 既存 env を取得
echo "[*] 既存 env を取得中..."
EXISTING=$(curl -s -H "Authorization: Bearer $VT" \
  "https://api.vercel.com/v9/projects/${PROJECT_ID}/env${TEAM_HINT}")

delete_env() {
  local key="$1"
  local ids
  ids=$(echo "$EXISTING" | python -c "
import sys, json
key = '$key'
d = json.load(sys.stdin)
for e in d.get('envs', []):
    if e.get('key') == key:
        print(e.get('id', ''))
")
  for id in $ids; do
    [ -z "$id" ] && continue
    echo "  - 既存 $key ($id) を削除"
    curl -s -X DELETE -H "Authorization: Bearer $VT" \
      "https://api.vercel.com/v9/projects/${PROJECT_ID}/env/${id}${TEAM_HINT}" >/dev/null
  done
}

create_env() {
  local key="$1"
  local value="$2"
  local payload
  payload=$(python -c "
import json, sys
print(json.dumps({
  'key': sys.argv[1],
  'value': sys.argv[2],
  'type': 'encrypted',
  'target': ['production', 'preview', 'development']
}))
" "$key" "$value")
  local res
  res=$(curl -s -H "Authorization: Bearer $VT" -H "Content-Type: application/json" \
    -d "$payload" \
    "https://api.vercel.com/v10/projects/${PROJECT_ID}/env${TEAM_HINT}")
  local err
  err=$(echo "$res" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('error',{}).get('message','') if isinstance(d,dict) else '')" 2>/dev/null || true)
  if [ -n "$err" ]; then
    echo "  ✗ $key 失敗: $err"
  else
    echo "  ✓ $key 登録"
  fi
}

set_env_if_present() {
  local key="$1"
  local val="${!key:-}"
  if [ -z "$val" ]; then
    echo "[ ] $key スキップ（~/.claude/.env に未設定）"
    return
  fi
  echo "[+] $key"
  delete_env "$key"
  create_env "$key" "$val"
}

for k in "${KEYS[@]}"; do
  set_env_if_present "$k"
done

echo
echo "[*] 完了。Vercel で再デプロイすると新しい env が反映されます:"
echo "    curl -X POST -H 'Authorization: Bearer \$VERCEL_TOKEN' \\"
echo "      'https://api.vercel.com/v13/deployments?forceNew=1' \\"
echo "      -d '{\"name\":\"ai-hub-jp\",\"project\":\"${PROJECT_ID}\",\"target\":\"production\",\"gitSource\":{\"type\":\"github\",\"ref\":\"main\",\"repo\":\"goodbouldering-collab/ai-hub\"}}'"
