---
title: "Codexで共同開発するには？リモートデスクトップ・Remote・SSHの違いと設定を図解"
date: 2026-10-03
updated: 2026-10-03
authorship_note: "※内容は運営者が考え、AIで整えています。"
role: ブログ / Codex・共同開発
gen_by: 由井辰美 / AI相談
summary: "画面を借りるリモートデスクトップ、別端末からAIに指示するCodex Remote、開発用PCへ接続するSSH。高校生にもわかる比較表と設定手順、Windowsの制約、GitHubで2人が安全に作る練習まで解説します。"
image: /img/blog-remote-guide-hero-20261003.png
status: published
---

友達と文化祭のホームページを作りたい。自宅のパソコンで動いているCodexを、外出先から確認したい。でも、調べると「リモートデスクトップ」「Remote」「SSH」が出てきて、何を選べばいいのかわからない。

まず、覚えることは一つです。**画面を動かすならリモートデスクトップ。AIに指示を届けるならCodex Remote。別のPCでコマンドを動かすならSSH。**

そして、友達と作品を作るなら、この接続方法に**GitHubで変更を持ち寄る仕組み**を組み合わせます。全員が一台のパソコンを触らなくても、共同開発はできます。

<figure>
<img src="/img/blog-remote-guide-hero-20261003.png" alt="リモートデスクトップは画面、Codex RemoteはAIへの指示、SSHはコマンドをつなぐ比較図" width="1672" height="941" decoding="async">
<figcaption>似た名前でも、つなぐものが違います。図は仕組みを説明するイメージです。</figcaption>
</figure>

### 最初の1分：自分の目的を選ぶ

| やりたいこと | 最初に選ぶ方法 | 理由 |
|---|---|---|
| 友達に「この画面のどこを押すの？」と教えてもらう | リモートデスクトップのサポート機能 | 同じ画面を見ながら説明・操作できる |
| 外出中に、自宅のCodexへ追加の指示を出す | Codex Remote | スマホなどから作業の続きを確認できる |
| 手元のノートPCから、別の開発用PCのファイルを直す | SSH／CodexのSSH接続 | 編集・テストを接続先の環境で行える |
| 2人がそれぞれ担当ページを作る | 各自のCodex＋GitHub | 作業を分けて、確認してから合わせられる |

これはこの記事の使い分けの提案です。上から順に全部導入する必要はありません。

### 3つを同じ物差しで比べる

| 比較項目 | リモートデスクトップ | Codex Remote | SSH |
|---|---|---|---|
| 主に触るもの | 接続先の画面・マウス・キーボード | Codexの会話・指示・承認・結果 | 接続先のファイル・コマンド |
| ファイルがある場所 | 接続先のPC | 接続したホストPC／その作業環境 | SSH接続先のPC |
| テストが動く場所 | 接続先のPC | 選択したホスト／実行環境 | SSH接続先のPC |
| 画面を人が直接クリック | できる | デスクトップ画面の共有とは別の機能 | 通常のSSHだけではできない |
| 他の人との使い方 | 相手の許可を得てサポート | 本記事のRemoteは同じ本人アカウントの端末間 | 人別のOSユーザー・鍵で接続を分ける |
| 接続先の電源 | 必要 | 必要。アプリの起動も必要 | 必要。SSHサーバーの起動も必要 |
| 最初の難しさ | 画面の案内に沿いやすい | 機能が表示されれば設定しやすい | アドレス・ユーザー・鍵の理解が必要 |

「ホスト」は**作業を受け持つ側のPC**です。この記事では「接続先」とも呼びます。「リモート」は、単に「離れた場所から」という意味です。

**確認日：2026年10月3日。** Codexのメニュー名や利用可否は、アプリの版・配信状況・ワークスペースの設定で変わります。現在の公式資料ではChatGPTデスクトップアプリ内の機能として説明されています。お使いの画面に「Codex」「Remote」などの表記が残っている場合もあります。以下は公式手順に基づく設定ガイドで、すべてのOS・アカウントの組み合わせで接続実験を行った記録ではありません。[OpenAI公式：Remote connections](https://learn.chatgpt.com/docs/remote-connections)

読む場所を選ぶ： [画面の共有](#desktop) ／ [Codex Remote](#remote) ／ [SSHの設定](#ssh) ／ [2人で作る練習](#team)

## 1．画面を見ながら教わるなら、リモートデスクトップ {#desktop}

<figure>
<img src="/img/blog-remote-guide-desktop-20261003.png" alt="あなたと友達が同じPC画面を見ながら操作を教え合うイメージ" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>「ここを押して」を共有できる方法。遠隔操作する人を決め、交代しながら使います。</figcaption>
</figure>

リモートデスクトップは、**離れたPCの前に座ったように、画面を見て操作する方法**です。Codexの起動、ブラウザの確認、アプリの設定など、マウスで行う作業に向いています。

たとえば、あなたのPCでエラーが出たとき。友達に画面を見てもらい、操作してもらうことができます。逆に、自分の外出用PCから、自宅PCのCodexを開く使い方もできます。

### 設定A：友達に一度だけ手伝ってもらう

ここでは、Chrome リモート デスクトップの「リモートサポート」を使います。

1. **操作してもらう側のPC**で、[Chrome リモート デスクトップのサポート画面](https://remotedesktop.google.com/support)を開きます。
2. 「サポートを受ける」の案内に沿って必要なソフトを入れ、「コードを生成」を選びます。
3. そのコードを、いま手伝ってくれる相手にだけ渡します。
4. **手伝う側のPC**でも同じページを開き、「サポートを提供する」にコードを入力します。
5. 操作してもらう側は、表示された相手のメールアドレスを確認して共有を許可します。
6. 終わったら「共有を停止」します。

**成功の目印：相手に自分の画面が見え、許可した操作ができること。** 最初はメモ帳などで確認すると安心です。

このコードは1回限りです。共有中は30分ごとに継続確認があります。画面だけでなく、ファイルやメールなども操作できる権限になるため、見られたくない情報を閉じ、作業を見守ります。Googleのパスワードを友達に渡す必要はありません。[Google公式：共有手順とアクセス範囲](https://support.google.com/chrome/answer/1649523?hl=ja)

### 設定B：自分の自宅PCへ、あとからつなぐ

自分の2台をつなぐ場合は、[リモートアクセス画面](https://remotedesktop.google.com/access)から、接続先PCにホストソフトを設定します。画面の案内に沿ってPC名やPINを設定し、手元の端末で対象PCを選んで接続します。「友達に一度だけ手伝ってもらう」設定とは分けて使いましょう。[Google公式：リモートアクセス](https://support.google.com/chrome/answer/1649523?hl=ja)

### Windows標準の「リモートデスクトップ（RDP）」を使う場合

**接続される側がWindows Homeなら、標準RDPのホストにはできません。** Pro・Enterprise・Educationなどが対象です。手元の接続する側はHomeでも構いません。これはWindows標準RDPの制約で、すべての遠隔操作ソフトに共通する制約ではありません。

接続先で「設定 → システム → リモートデスクトップ」を有効にし、接続を許可するユーザーとPC名を確認します。手元で「リモートデスクトップ接続」を開き、PC名またはIPアドレスと、そのPCのユーザー資格情報で接続します。まず同じ信頼できるネットワークで試してください。NLAという接続前の認証保護は有効のまま使います。[Microsoft公式：RDPの対象エディションと設定](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/remotepc/remote-desktop-allow-access)

家の外からつなぐ場合は、学校・会社が指定するVPNなど、許可された接続経路を先に用意します。ルーターの3389番を、記事の練習のためにインターネットへ公開する必要はありません。

### できないこと・気をつけること

- **2人が同じ画面を同時に自由に編集する道具ではありません。** マウスがぶつからないよう、操作役を交代します。画面共有の挙動はソフトによって異なります。
- **つなぐだけで相手のPCにファイルのコピーはできません。** 編集対象は接続先です。共有したい成果物は別途GitHubなどへ保存します。
- **PCが停止・スリープしていたり、ネットワークが届かなかったりすると接続できません。** 学校のPCは、勝手に設定を変えず管理者へ相談します。

## 2．外出先から自分のAIに指示するなら、Codex Remote {#remote}

<figure>
<img src="/img/blog-remote-guide-remote-20261003.png" alt="同じアカウントのスマホから自宅PCのCodexへ指示し、作業とファイルはPC側にある図" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>スマホは指示と確認の窓口。作業環境は接続先にあります。</figcaption>
</figure>

Codex Remoteは、**別の端末から、接続先にあるCodexの作業を続ける仕組み**です。「今どこまで進んだ？」「次は文字を大きくして」と送り、結果や変更点を確認できます。

ここで扱うRemoteは、**同じChatGPTアカウント・同じワークスペースで使う本人の端末同士**が基本です。友達を自分のアカウントにログインさせる共同開発手順にはしません。

### 用意するもの

- Codexを利用できるChatGPTアカウントと対象ワークスペース。
- 接続先となるMacまたはWindows PCと、最新の対応デスクトップアプリ。
- 対応するChatGPTのiOS／Androidアプリ。PC同士は「Control other devices」が使える環境。
- 接続先の電源、ネット接続、起動中のデスクトップアプリ。

組織で使う場合は、管理者によるRemote Controlの許可が必要なことがあります。CLIやIDE拡張だけから、スマホ用のペアリング設定を始めることはできません。[OpenAI公式：Remoteの準備](https://learn.chatgpt.com/docs/remote-connections#before-you-set-up-mobile-access)

### 設定：PCのQRコードをスマホで読み取る

1. **接続先PC**でアプリを開き、「Settings → Connections → Control this Mac or PC」へ進みます。
2. 「Set up」または「Add」を選び、案内に従って遠隔アクセスを有効にします。
3. **自分のスマホ**で表示されたQRコードを読み取ります。
4. スマホ側で同じアカウント・ワークスペースを確認し、求められた本人確認を完了します。
5. スマホの「Codex」、旧表記のアプリでは「Remote」から、接続先PCと会話を選びます。
6. PCのConnections設定で、必要に応じてスリープを防ぐ設定と接続端末を確認します。

**成功の目印：スマホから送った追加指示が、選んだPCの会話に届くこと。** 最初は「いま開いているプロジェクトのフォルダ名を教えて。ファイルは変更しないで」と頼むと、接続先を間違えていないか確認できます。

PCから別のPCへつなぐ場合は、手元のアプリの「Settings → Connections → Control other devices」を使います。表示されない環境では、アプリ更新と提供状況を確認してください。[OpenAI公式：設定と別端末からの継続](https://learn.chatgpt.com/docs/remote-connections)

### 何ができて、何は別なのか

指示の追加、質問への返答、承認、変更差分・テスト結果・端末出力・スクリーンショットの確認などができます。使えるファイルやプラグイン、ブラウザ、権限は**接続先の環境**に依存します。

Remoteがあるだけで、あなたがPC画面の好きな場所を直接クリックできるわけではありません。AIにアプリ操作を頼む「Computer Use」は別の機能と設定です。WindowsのComputer Useでは、ロックされていない利用可能なセッションが必要で、前面のデスクトップを使います。その間、人が同じ画面で別作業をする運用は避けます。[OpenAI公式：ホスト環境とComputer Useの条件](https://learn.chatgpt.com/docs/remote-connections)

### 接続が切れたら、3つだけ確認

1. PCがスリープしていないか。
2. PCのアプリが起動し、ネットにつながっているか。
3. 両端末のアカウント・ワークスペースが同じか。

ログアウトするとRemote Controlが無効になるため、再ログイン後に有効化が必要です。**PCが使えなくなっても、このRemoteの仕事が自動的にクラウドへ移るとは考えないでください。** 公式資料にある「Work Cloudのローカルコンピューターアクセス」は別の仕組みです。[OpenAI公式：切断時の確認とWork Cloudとの違い](https://learn.chatgpt.com/docs/remote-connections)

## 3．別のPCで編集・テストするなら、SSHでつなぐ {#ssh}

<figure>
<img src="/img/blog-remote-guide-ssh-20261003.png" alt="手元のPCからSSHの暗号化された接続を通り、開発用PCのファイルとコマンドを操作する図" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>キーボードを打つのは手元。接続後のコマンドが動くのは開発用PCです。</figcaption>
</figure>

SSH（エスエスエイチ）は、**別のPCへ暗号化して接続し、文字の命令で操作する方法**です。Codex専用ではなく、開発現場で使われる接続の仕組みです。

たとえるなら、手元のPCが「注文するカウンター」、接続先が「調理するキッチン」。注文を入れる場所と、実際に作業する場所が違います。

**SSH自体はAIではありません。SSH接続した先でCodexを動かすと、遠隔の開発環境をAIに手伝ってもらえます。** 接続先PCを高性能にすると、そのPCで動くビルドやテストには役立ちますが、クラウドのAIモデル自体をそのPCで計算するという意味ではありません。

### 先に決める3つ：行き先・利用者・鍵

| 必要なもの | たとえ | この練習の例 |
|---|---|---|
| 接続先のアドレス | 学校の住所 | `192.168.1.50` |
| 接続先のOSユーザー | 入室する人の名前 | `student` |
| SSH鍵 | 入室用の鍵 | `id_ed25519_codex` |

**アドレスとユーザー名は例です。自分の環境の値に置き換えます。** 鍵は「秘密鍵」と「公開鍵」の2点セット。秘密鍵は手元に保管し、接続先に登録するのは名前の最後が`.pub`の公開鍵だけです。

以下は、**手元がWindows、接続先がUbuntuの開発用PC**の例です。接続先には`student`という通常ユーザーがあり、そのユーザーでログインできる前提です。学校・会社の管理PCなら、インストールと接続の許可を先に確認します。

### 手順1：接続先にSSHの受け口を用意する

**実行場所：接続先Ubuntuのターミナル。** 管理を任された人が実行します。

```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable --now ssh
hostname -I
```

最後の行で表示される、手元から到達できるアドレスを使います。複数出る場合は管理者に確認しましょう。ファイアウォールを使っている環境では、手元の端末または許可したVPNからのSSH接続だけを許可します。ファイアウォール全体を無効にはしません。[Ubuntu公式：OpenSSHサーバー](https://ubuntu.com/server/docs/how-to/security/openssh-server/)

### 手順2：手元に鍵を作る

**実行場所：手元のWindowsのPowerShell。** まず`ssh -V`でOpenSSHが使えるか確認します。見つからなければ、Windowsの「オプション機能」で「OpenSSH クライアント」を追加します。

```powershell
ssh -V
New-Item -ItemType Directory -Force -Path "$HOME/.ssh" | Out-Null
ssh-keygen -t ed25519 -f "$HOME/.ssh/id_ed25519_codex"
```

作成時に求められるパスフレーズは、秘密鍵を守るための合言葉です。既に同名の鍵があれば**上書きせず**、別の名前にします。

公開鍵を表示するコマンドは次のとおりです。

```powershell
Get-Content "$HOME/.ssh/id_ed25519_codex.pub"
```

表示された`ssh-ed25519`から始まる1行が公開鍵です。`.pub`の付かないファイルは秘密鍵なので、友達へ送ったりブログに貼ったりしません。[Microsoft公式：SSH鍵の作成と管理](https://learn.microsoft.com/ja-jp/windows-server/administration/openssh/openssh_keymanagement)

### 手順3：公開鍵を接続先に登録する

**実行場所：接続先Ubuntuで、`student`本人として開いたターミナル。** 手順2の公開鍵1行を用意してから行います。

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
```

エディターが開いたら、既存の内容を消さず、末尾に公開鍵を1行追加します。`Ctrl＋O`、Enterで保存し、`Ctrl＋X`で閉じます。その後、次を実行します。

```bash
chmod 600 ~/.ssh/authorized_keys
```

これはUbuntu側の手順です。Windowsの接続先に、この`chmod`の手順をそのまま使わないでください。Windows版は後述します。[Ubuntu公式：鍵認証](https://ubuntu.com/server/docs/how-to/security/openssh-server/)

### 手順4：PCに短い呼び名を付けて接続する

**編集場所：手元のWindowsの`C:\Users\自分のユーザー名\.ssh\config`。** ファイル名は`config`で、`.txt`は付けません。既にある内容を残して、次のブロックを追加します。

```text
Host school-dev
    HostName 192.168.1.50
    User student
    IdentityFile ~/.ssh/id_ed25519_codex
    IdentitiesOnly yes
```

`school-dev`は自分で付ける呼び名です。`HostName`は実際の接続先、`User`は接続先のOSユーザー名です。GitHubの名前やメールアドレスではありません。

**実行場所：手元のPowerShell。**

```powershell
ssh school-dev
```

初回に相手の鍵の確認が出たら、表示された指紋が本物の接続先と一致するか、管理者と照合してから進みます。自分が管理するUbuntuなら、接続先で`ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`を実行し、ED25519の指紋を確認できます。種類が違う指紋同士は比較しません。

接続できたら、**SSHの接続先画面**で次を実行します。

```bash
hostname
whoami
pwd
```

**成功の目印：接続先のPC名、`student`、接続先のフォルダが表示されること。** `exit`を打つと手元に戻ります。

### 手順5：接続先へCodexを入れる

SSHが動いてからCodexを設定します。**実行場所：SSH接続中のUbuntu側。** Node.jsとnpmが準備済みなら、公式のnpm版を使えます。

```bash
node --version
npm --version
npm install -g @openai/codex
codex --version
codex login --device-auth
```

`node`や`npm`が見つからない場合は、管理者と開発環境を整えてから進みます。権限エラーを消すためだけに、むやみに管理者権限でインストールしないでください。npm以外の導入方法も[Codex CLI公式手順](https://learn.chatgpt.com/docs/cli)にあります。

ログイン用URLとコードが表示されたら、手元のブラウザで**自分のアカウント**として認証します。このコードは人に渡しません。デバイスコード認証が利用できない組織では、管理者に利用可否を確認します。接続先へのログインとCodexへのログインは、別々です。[OpenAI公式：認証](https://learn.chatgpt.com/docs/auth)

### 手順6：Codexからリモートのプロジェクトを開く

手元のデスクトップアプリで「Settings → Connections」を開き、SSHホスト`school-dev`を追加・有効化して、**接続先にあるプロジェクトフォルダ**を選びます。

Codexは`~/.ssh/config`の具体的なホスト名を見つけて接続します。`Host *`だけでは候補になりません。また、接続先のログインシェルから`codex`コマンドを実行できる必要があります。**普通の`ssh school-dev`は成功するのにアプリだけ失敗する場合は、SSH先で`codex --version`が通るか**を確認しましょう。[OpenAI公式：SSHホストへの接続](https://learn.chatgpt.com/docs/remote-connections#connect-to-an-ssh-host)

アプリのSSH機能が利用できない場合でも、SSH先でプロジェクトへ移動し、`codex`を起動するCLIの使い方は分けて考えられます。ただし、アプリの会話一覧やすべての機能がそのまま使えるという意味ではありません。

### 接続先がWindowsの場合は、受け口の設定が変わる

Windows 11なら、接続先の「オプション機能」から「OpenSSH サーバー」を追加します。**接続先で管理者として開いたPowerShell**では、次の設定も可能です。

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
Get-NetFirewallRule -Name OpenSSH-Server-In-TCP
```

サーバー導入時にSSHの受信規則が作られます。接続を許す範囲は管理者と確認します。これはRDPとは別機能なので、「Windows HomeはRDPの接続先になれない」という話と混同しないでください。[Microsoft公式：WindowsのOpenSSH設定](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)

鍵の登録先は、通常ユーザーなら接続先の`C:\Users\ユーザー名\.ssh\authorized_keys`です。既存の鍵を残して公開鍵を1行追加します。**管理者グループのユーザーは通常と登録先・アクセス権が異なる**ため、この練習では通常ユーザーを使い、Windowsの鍵管理手順に従います。Ubuntuの`chmod`を置き換えずに実行しないことがポイントです。[Microsoft公式：ユーザー別の公開鍵登録](https://learn.microsoft.com/ja-jp/windows-server/administration/openssh/openssh_keymanagement)

そのユーザーでCodex CLIを導入・認証し、SSHで入った状態でも`codex --version`が通ることを確認してから、手元のCodexに接続先を追加します。Windows・Ubuntuどちらでも、**SSHが使えることと、Codexアプリの接続機能が使えることは別々に確認**します。

### 家の外からつなぐ場合：先に専用の通り道を作る

`192.168...`は通常、自宅などの内部ネットワーク用アドレスです。そのまま外出先から届くとは限りません。例としてTailscaleなどのVPNを使うなら、次の順です。

1. 手元と接続先の両方へ、公式手順でTailscaleを導入します。
2. 自分の端末なら同じ自分のネットワークへ参加させます。友達の端末は友達自身のアカウントを招待し、必要な機器への権限を設定します。
3. 管理画面で両端末の接続を確認し、接続先のVPN内アドレスを確認します。
4. 先ほどのSSH設定の`HostName`を、そのアドレスにします。
5. `ssh school-dev`を再確認します。VPN側とPC側の両方で、必要な接続が許可されている必要があります。

ここで説明しているのは**VPNの中で通常のOpenSSHを使う方法**です。「Tailscale SSH」という別の認証機能を必須にしていません。[Tailscale公式：導入](https://tailscale.com/docs/install/start)・[利用者の招待](https://tailscale.com/docs/features/sharing/how-to/invite-users)

Codexのapp-serverを公開ネットワークへ直接さらす設定は使いません。OpenAIも、外部からの接続にはVPNなどを案内しています。[OpenAI公式：ネットワーク公開の注意点](https://learn.chatgpt.com/docs/remote-connections#authentication-and-network-exposure)

### SSH先で作ったサイトを、自分のブラウザで見る

接続先でWebの開発サーバーが`127.0.0.1:3000`で動いているとします。手元の`localhost`を開いても、そこは手元のPCなので、そのままでは別のPCのサイトは見えません。

**手元の別のターミナル**で、次の通り道を開きます。

```bash
ssh -N -L 127.0.0.1:3000:127.0.0.1:3000 school-dev
```

そのターミナルを開いたまま、手元のブラウザで`http://127.0.0.1:3000`を開きます。これはポート転送というSSHの機能です。3000番が使われているなら、左側だけ3001番にして、ブラウザも3001番へ変えます。サーバー自体は別途、接続先で起動しておきます。[OpenSSH公式：ポート転送の仕様](https://man.openbsd.org/ssh#L)

SSHの切断後も処理が必ず続くとは限りません。長時間処理には、接続先でのプロセス管理が必要です。Linuxの`tmux`などを使う方法は、基本の接続ができてから学べば十分です。

## 4．2人で作るなら、作業を分けてGitHubで合わせる {#team}

<figure>
<img src="/img/blog-remote-guide-team-20261003.png" alt="AさんとBさんが別々に作業し、レビューを通して共有の完成版に合わせる流れ" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>接続できることと、変更が安全に合わさることは別。共同開発には確認の場所を作ります。</figcaption>
</figure>

ここまでの3つは、離れたPCへつなぐ方法でした。**共同開発の中心は、「誰が何を直し、どう確認して合わせるか」です。**

文化祭サイトなら、Aさんがトップページ、Bさんがアクセス案内を担当する、と決められます。これは説明用の仮想例です。

### まず覚える4語

| 言葉 | 高校のグループ課題にたとえると |
|---|---|
| リポジトリ | 作品と変更履歴を入れる共有の保管場所 |
| ブランチ | 完成版を直接壊さずに試せる、自分の作業ルート |
| コミット | 「ここまで変更した」という記録 |
| プルリクエスト（PR） | 「この変更を完成版に入れていい？」という確認依頼 |

GitHubのPRでは変更を相談・レビューし、確認が済んでから統合できます。この統合を「マージ」と呼びます。[GitHub公式：プルリクエスト](https://docs.github.com/en/pull-requests/get-started/about-pull-requests)

### 2人用の最小セット

1. 各自が自分のGitHubアカウントとCodexの利用環境を用意します。
2. 代表者がGitHubで練習用リポジトリを作ります。名前は例として`school-festival`。READMEを付けて初期化します。
3. 個人所有のリポジトリなら「Settings → Collaborators」から相手を招待し、相手が承諾します。組織所有では管理者の権限設定に従います。
4. 各自のPCへGitを用意し、GitHubに本人として接続できる状態にします。
5. 各自がリポジトリをコピーし、自分の作業用ブランチを作ります。

招待はリポジトリへの権限を渡す操作です。パスワードの共有ではありません。[GitHub公式：共同編集者の招待](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)

### 練習：AさんがREADMEを1行直す

**実行場所：Aさんが実際に開発するPC。** SSHで開発するなら接続先です。`OWNER`はGitHubの所有者名に置き換えます。

```bash
git clone https://github.com/OWNER/school-festival.git
cd school-festival
git switch -c a/readme-intro
```

Gitの初回利用なら、このリポジトリで記録する名前とメールも設定します。メールを公開したくない場合は、GitHubのメール設定にある本人のnoreplyアドレスを使えます。

```bash
git config user.name "自分の表示名"
git config user.email "自分のGitHub用メールアドレス"
```

このフォルダをCodexで開き、次のように頼みます。

```text
README.mdに「文化祭の案内サイトです。」を1行追加して。
ほかのファイルは変更しないで。
変更後に差分を見せて。コミット・push・公開はまだしないで。
```

意図どおりか確認し、次に進みます。

```bash
git diff
git add README.md
git commit -m "Add festival introduction"
git push -u origin a/readme-intro
```

GitHubで対象リポジトリを開き、**Pull requests → New pull request**を選びます。取り込み先の`base`を`main`、変更元の`compare`を`a/readme-intro`にし、差分を確認して**Create pull request**を押します。タイトルと「READMEに案内文を1行追加」という説明を書き、PRを作ります。BさんはそのPRの**Files changed**で差分を見ます。Bさんは「予定の1行だけか」「秘密情報が入っていないか」を確認し、問題がなければマージします。READMEの練習であれば、実装のテストを無理に増やす必要はありません。プログラムを変更した場合は、そのプロジェクトのテストやビルドも行います。

**成功の目印：PRがマージ済みになり、GitHubの`main`に1行が入ること。** GitHubに記録されたことと、サイトが本番公開されたことは別です。公開はチームで決めた手順に従います。

次の作業を始めるときは、手元に未保存の変更がないか`git status`で確認してから、次を実行します。

```bash
git switch main
git pull --ff-only
git switch -c a/next-change
```

Bさんも自分のコピーと自分のブランチで作業します。同じ行を変更して競合したら、どちらを残すか相談します。エラーを消すために`reset --hard`や強制pushを使う必要はありません。

### 一台の開発用PCを共有するなら

接続先が一台でも、人ごとにOSユーザー、SSH鍵、Codexの認証、作業フォルダを分けます。**別ブランチにするだけでなく、同時作業するフォルダも分ける**のがポイントです。同じフォルダで一人がブランチを切り替えると、相手が見ているファイルも変わってしまうためです。

慣れてきたら、同じGitリポジトリから別の作業フォルダを作る「worktree」も使えます。ただしworktreeはファイルの作業場所を分ける仕組みで、OSユーザーの権限や認証を分ける仕組みではありません。詳しくは[Codex・worktree・Gitの解説記事](/blog/2026-07-24-codex-worktree-git-deploy-guide.html)へ。

### つながらないときの早見表

| 困ったこと | 最初に見る場所 |
|---|---|
| WindowsのRDP設定が使えない | 接続先がHomeではないか。管理者権限はあるか |
| RemoteにPCが出ない | アプリ起動・電源・同じアカウントとワークスペース・接続設定 |
| SSHが時間切れになる | 接続先アドレス、VPN、電源、ファイアウォール |
| SSHで`Connection refused` | SSHサーバーが起動しているか、接続ポートが正しいか |
| SSHで`Permission denied (publickey)` | ユーザー名、使う秘密鍵、接続先の公開鍵登録 |
| SSHは動くがCodexからつながらない | 接続先のログインシェルで`codex --version`が通るか |
| 接続先でサイトを起動したのに見えない | 手元と接続先の`localhost`の取り違え、ポート転送 |
| GitHubへpushできない | リポジトリへの招待、本人のGitHub認証、remoteの向き先 |

### よくある質問

**Q．3つを全部設定しないと共同開発できませんか？**  
A．いいえ。最初は「各自のCodex＋GitHub」で作業を分け、困ったときだけ画面共有を足す方法で十分です。外出先から自分の作業を見る必要が出たらRemote、共通の開発用PCを使う必要が出たらSSHを加えます。

**Q．Codex RemoteとCodexのSSH接続は同じですか？**  
A．同じConnections設定に並ぶことがありますが、役割を分けて考えます。Remoteは対応端末から接続済みホスト上の会話を続ける入口。SSH接続はリモートのファイル・シェルを開発環境として使う入口です。スマホ→デスクトップ→SSH接続先という組み合わせもあります。[OpenAI公式：接続先の選択](https://learn.chatgpt.com/docs/remote-connections)

**Q．「ローカル」と表示されれば、AIへコードは送られませんか？**  
A．そういう意味ではありません。ローカル／SSHは主にファイルやツールの実行場所の話です。OpenAIのモデルで推論する場合のデータの扱いは、ログイン方法と契約・組織設定も確認します。[OpenAI公式：認証と適用される管理方針](https://learn.chatgpt.com/docs/auth)

**Q．料金は何を見ればいいですか？**  
A．接続の道具、Codexの利用枠、接続先PCやサーバーの費用を分けます。SSH接続を追加してもCodexの利用上限が無制限になるわけではありません。APIキー認証はChatGPTプランとは別のAPI従量課金です。また公式の提供表では、SSH接続はAPIキー利用に対応しますが、モバイルのRemote Controlは対応しません。固定の「全部無料」「どのログイン方法でも同じ」と考えず、[Codexの公式料金・提供範囲](https://learn.chatgpt.com/docs/pricing#feature-availability)と、利用するVPN・OS・サーバーの条件を確認します。

### 今日やるのは、READMEを1行だけ持ち寄ること

最初の目標を「3種類を全部つなぐ」にすると、設定だけで疲れてしまいます。まずは友達と小さなリポジトリを作り、**1行の変更をPRで確認して合わせる**ところまで進めましょう。

接続方法は、その先で困ったことに合わせて選べば大丈夫です。

**画面・AI・コマンド。つなぐものを選んで、変更は分けて合わせる。**

授業や地域の活動で使うAI開発環境の相談は、[AI相談の案内ページ](/)からどうぞ。
