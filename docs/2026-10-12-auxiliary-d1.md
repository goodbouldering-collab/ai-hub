# 指令室・収集履歴のD1移行候補

2026-10-12。保存API、非上書き移送、暗号化バックアップと復元を合成データで検証した。本番D1の作成、元データ本文の取得、移送、切替は未実施。公開ニュース・612公開資産・既存ログインを変更していない。

## 移す対象と承認範囲

| 対象 | 確認済み範囲 | 今回の扱い |
|---|---|---|
| Supabase `zrawhzwtppmlxyhngnju` の `command_center` | projects 15、tasks 8、directives 5、directive_executions 2、trades / trade_plans / relay_state / relay_requests / relay_nonces 各0、計30行 | 非公開の業務指示・実行記録。件数のみ確認済み。本文は未取得。列を欠落させずJSONで保全する |
| 同projectの `ai_watch.articles` | 3行 | 既存の収集履歴。新規・重複の判定を維持する |
| `portal.sns_posts` | 監査した2projectで表未検出 | 実在する表の0行とは扱わない。移送元SELECT対象に含めず、D1の履歴読取だけ準備する |
| Auth・顧客業務DB・Storage | 今回の対象外 | auth、storage、B21のpublic業務表を取得しない。既存ログインの秘密・Cookie仕様・利用者権限を変更しない |

承認対象は、上記33行の暗号化取得・保全・D1移送、新規専用D1 `aiclimb-auxiliary`、`aiclimb` Workerの `AUX_DB` bindingと切替。Cloudflare accountは中央台帳の `2cc53dc7f0cadb5f36fa48d256e10cc7`。D1 IDは未作成・未確定で、仮IDを設定に入れていない。新しい認証Secret、R2 bucket、DNS、SNS送信、Supabaseへの変更・削除・解約は含まない。

公開元は中央台帳どおり `C:/Project/AI相談/work/genspark-profile-edit/cloudflare-runtime`、設定は `wrangler-profile-release.jsonc`、Workerは `aiclimb`、TargetKeyは `default`。候補worktreeからの本番操作は拒否する。新D1の実IDと所有関係を台帳でverifiedにした後、既存Wranglerログインと中央 `-ForDeploy` ガードを使う。

## 実装した経路

- `deployment/admin-workspace/worker.mjs` は既存 `/api/admin/ping` の認証後にD1 APIへ渡す。`AUXILIARY_BACKEND=d1` と実bindingがそろわない場合は503。旧Supabaseへのfallbackはない。
- `/api/admin/command-center/data` は旧11操作を実装。所有者をサーバー設定から固定し、Origin、実body64KiB上限、入力形式、CAS更新を検査する。承認済み取引計画からの実行はD1 batchで一度だけ保存する。取引の外部発注APIは呼ばない。
- `/api/admin/sns-history` は認証済みGET/HEADのみ。SNS投稿・PC relay・AIチャットの未接続APIは引き続き503。データ移行と、これらの外部実行機能の受入は別工程。
- `core/differ.py` は通常のSQLiteを保持。`ARTICLE_STORE=d1` の明示時だけ、標準入力でNode経由のD1履歴へ接続する。旧Supabase環境変数がある場合は通信前に停止して切替手順を案内する。日次処理の設定は変更していない。
- `scripts/migrate_sqlite_to_supabase.py` は既存呼出0件を確認し、実行時に通信・環境設定・SQLite読取の前で廃止エラーにした。履歴はGitから参照できる。

保存表は `cloudflare-runtime/migrations/0001_auxiliary_data.sql` の `auxiliary_records`。許可した11 namespace、元のID、所有者、元行JSON、更新revisionを保持する。画面へは許可した項目だけcamelCaseへ変換する。未知の列も移送原本とD1のJSON内には保持する。

## 実行前に具体化した移送・復元手順

Node 24が必要。以下は承認後に統合済みの正本で実行する手順であり、実施済みではない。

1. 既存の手動Supabase書込経路が停止していることを確認する。新D1を専用で作成し、実IDを中央台帳と設定に登録。初期設定は `AUXILIARY_BACKEND=disabled`、`AUXILIARY_WRITES=frozen` とし、認証付きAPIはまだ開かない。
2. 実際の本人承認を参照する `tmp/auxiliary-transfer-approval.json` と、元書込停止・D1凍結の証拠 `tmp/auxiliary-transfer-freeze.json` を用意する。自己生成した設定ファイルだけを本人承認の代用にしない。freeze証拠は正本内の実ファイルと30分以内の確認日時を必須にする。
3. `node scripts/auxiliary-transfer-cli.mjs init` で事業専用のローカルvaultを作る。保存先は `C:/Project/AI相談/tmp/auxiliary-transfer-v1`。B21やNotエステの鍵・保存先を再利用しない。
4. `node scripts/auxiliary-transfer-cli.mjs query <snapshot-id>` で公開鍵入りの単一SELECTを生成。公式Supabaseコネクターから上記projectで実行する。応答は `encrypted_snapshot` の暗号文だけとし、端末内でbase64を復号して同vaultの `<snapshot-id>.pgp` に非上書き保存する。実SQLは固定10表の件数とportal表不存在を先に検査し、変化時は行本文を選択せず失敗を返す。
5. `node scripts/auxiliary-transfer-cli.mjs prepare <snapshot-id>`。端末内でPGPを復号し、33行・ID重複・所有者・payload上限を検査。各行の元JSON表記を暗号文内に保持し、大きな整数・高精度小数・入れ子JSONの数値をJavaScriptで丸めず保持できるか検査する。不一致なら移送前に停止し、値や型を推測で変換しない。AES-GCMで原本を非上書き保存し、再読込と同バックアップからの隔離SQLite復元を確認する。秘密・元行は標準出力やGitへ出さない。
6. `node scripts/auxiliary-transfer-cli.mjs import <snapshot-id>`。承認、freeze、中央台帳、canonical cwd、HEAD=origin/main、移送入力のcommit、中央ガードを確認。専用DB以外の表があれば停止する。全既存行の一致・未使用revision=1を確認してから不足行のみ追加し、全列の再取得digestを照合する。途中失敗後は同じ暗号化原本から再開できる。異なる行や使用済み行を上書きしない。
7. 移送後に新しいsnapshot-idで手順4～5をもう一度行う。`node scripts/auxiliary-transfer-cli.mjs finalize <fresh-id> <original-id>` でD1 readbackより新しい元の観測と全内容が一致することを確認する。単に同じ保存済み元データを再比較した結果では切り替えない。
8. 33行の保存と元再照合、既存ログインでの所有者一致、画面表示、変更・再読込を確認できた後、別の統合差分で `AUXILIARY_BACKEND=d1` / `AUXILIARY_WRITES=enabled` を配備する。実認証後のテスト書込は事前に対象・復元方法を定める。未確認のownerを推測で差し替えない。

vaultのAES鍵とPGP passphraseはWindows CurrentUser DPAPIで保護し、PGP秘密鍵もpassphrase付きで保存する。`public.asc` 以外の鍵・暗号化原本・承認記録はGit対象外。合成データでこのPCのGPG/DPAPI/AES readbackを確認したが、別端末からの復旧や外部媒体へのバックアップは未実施。本人が選ぶ保管先と復旧方法を本番受入に含める。

APIとCLIは失敗閉止。切替前の復旧は旧Supabaseを変更せずD1凍結を維持する。切替後に新しいD1書込が発生した場合、古い原本へ巻き戻さない。書込を凍結し、D1最新データの保全・差分照合をしてから復旧する。

## 検証と残件

- `npm run verify:auxiliary` 成功: Node20件、Python5件、Cloudflare7件、公開経路検査。認証・所有者・CSRF・body上限・凍結、11保存操作、同時実行/CAS、全33合成行の復元・再開・改ざん拒否、旧移行ツールの通信前停止を検証した。
- 実配備形式の `published-worker.mjs` でも既存Cookieによる認証、D1 GET/POST/HEADを合成bindingで実行。公開資産・ニュースJSONは差分0。`npm run build:auxiliary` でWorkerだけ再生成する。esbuild 0.25.4、Node24.15.0、Python3.12を使用。
- 独立読取レビューで数値精度の指摘を受け、上記の移送前拒否を追加。再レビューで修正必須の指摘なし。PGliteの隔離PostgreSQLでも生成SQLを実行し、合成33行、精度不適合の拒否、件数変化時に行本文を返さないことを確認した。このSQL検査だけはPGP関数をstubにし、暗号の実往復は別のGPG試験で確認した。
- Git共有の結果は工程記録 `tmp/delivery/20261012-auxiliary-d1.json`、ローカル証拠は同名ディレクトリ。GPG/DPAPI合成検証は `tmp/auxiliary-os-probe.json`、PostgreSQL合成検証は `tmp/auxiliary-postgres-probe.json`。証拠・vaultはリポジトリへ送らない。
- 残件: 本人による非公開33行と新D1の具体承認、元行の実型/owner確認、移送とfresh比較、本番認証付き画面・保存受入、日次D1選択、別端末復旧。旧画像Storage補助モジュールはruntime import外。`ai-hub-public` の6画像はグッぼる所有で、この移送へ含めない。事業全体のSupabase解約条件は未達。

元の件数監査は [2026-10-11監査](supabase-aux-audit-20261011.md)。D1 batchの取引境界は [Cloudflare公式](https://developers.cloudflare.com/d1/worker-api/d1-database/)、CLI remote proxyは [Wrangler API](https://developers.cloudflare.com/workers/wrangler/api/) を参照。
