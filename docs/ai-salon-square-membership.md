# AIオンラインサロン Square決済・LINE参加管理

## 目的

公開ページからLINEオープンチャットへ直接入れないようにし、Square決済を確認できた人だけ参加案内へ進める。

## 公開導線

1. サイトの「Squareで決済して参加」
2. AI相談内の確認画面
3. Squareの決済画面
4. 決済完了をSquare Orders APIで照合
5. LINEオープンチャットの招待URLを表示
6. 管理者が決済名と参加申請を照合して承認

## 必要なVercel環境変数

- `SQUARE_ACCESS_TOKEN`
- `SQUARE_ENVIRONMENT=production`
- `SQUARE_VERSION=2026-05-20`
- `SQUARE_LOCATION_ID`
- `SQUARE_AI_SALON_PRICE_YEN`
- `SQUARE_AI_SALON_ITEM_NAME=AIオンラインサロン`
- `AI_SALON_OPENCHAT_URL`

金額は推測で設定しない。代表者が確定した税込金額を `SQUARE_AI_SALON_PRICE_YEN` に円の整数で登録する。

## LINEオープンチャットの設定

1. オープンチャットの公開設定を「参加の承認」にする。
2. 質問を「Square決済時に入力した名前を入力してください」にする。
3. Square注文の購入者名・カスタム項目と参加申請の回答を照合する。
4. 一致した人だけ承認する。
5. 返金・退会が発生した場合は、Square注文とLINEメンバーを確認して手動で調整する。

LINEオープンチャットには、外部決済と会員状態を自動同期する公開APIがないため、最終承認と退会処理は管理者が行う。

## 実装ファイル

- `api/square/ai-salon-checkout.ts`: Square決済リンクの作成
- `api/square/ai-salon-access.ts`: 決済済み注文の照合とLINE案内
- `api/_lib/square.ts`: Square API共通処理
- `site/build_portal.py`: 短いサロン説明と購入導線
