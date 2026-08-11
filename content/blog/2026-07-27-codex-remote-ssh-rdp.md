---
title: "外出先から自宅PCのCodexを安全に動かす方法｜Remote SSH・Remote・RDPの使い分け"
date: 2026-07-27
authorship_note: "※内容は運営者が考え、AIで整えています。"
role: ブログ / Codex・AI開発環境
gen_by: 由井辰美 / AI相談
summary: 外出先のノートPCから自宅の高性能PCにあるCodex開発環境を使うために、Remote SSH・Codex Remote・Windowsリモートデスクトップの違い、設定手順、つながらないときの確認順を公式情報に基づいて整理します。
image: /img/blog-codex-remote-hero-20260727.png
---

<style>
.codex-remote-lead{margin:0 0 28px;padding:18px 20px;border-left:5px solid #0ea5a8;border-radius:0 10px 10px 0;background:#eefbfa;color:#173042;}
.codex-remote-lead strong{color:#075e63;}
.codex-remote-figure{margin:14px 0 28px;}
.codex-remote-figure img{display:block;width:100%;height:auto;border-radius:14px;background:#e8eef3;box-shadow:0 18px 50px rgba(15,23,42,.14);}
.codex-remote-figure figcaption{margin-top:10px;color:#526273;font-size:.92rem;line-height:1.7;}
.codex-remote-check{margin:20px 0;padding:18px 20px;border:1px solid rgba(14,165,168,.28);border-radius:12px;background:#f7fffe;}
.codex-remote-check p:first-child{margin-top:0;}
.codex-remote-cta{margin:34px 0 12px;padding:24px;border-radius:16px;background:#10283b;color:#fff;}
.codex-remote-cta h3{margin:0 0 10px;color:#fff;}
.codex-remote-cta p{color:#d9e7ee;}
.codex-remote-cta a{display:inline-block;margin-top:8px;padding:12px 18px;border-radius:999px;background:#f47b57;color:#fff;font-weight:800;text-decoration:none;}
</style>

<figure class="codex-remote-figure">
  <img src="/img/blog-codex-remote-hero-20260727.png" alt="外出先のノートPCとスマートフォンから自宅の高性能デスクトップへ安全に接続するイメージ" loading="eager" decoding="async">
  <figcaption>軽い端末を持ち歩き、プロジェクトと重い処理は自宅PCへ集約する。3つの接続方法は、競わせるのではなく役割で使い分けます。</figcaption>
</figure>

<div class="codex-remote-lead">
<strong>結論は、普段の開発をRemote SSH、進捗確認や追加指示をCodex Remote、初期設定や画面操作をTailscale経由のRDPに分けることです。</strong> こうすると、外出用ノートPCへ開発環境を毎回複製せず、自宅PCのファイル、Git、Node.js、Python、認証情報を一か所で管理できます。
</div>

外出先でもAIを使って開発を続けたい。ただし、ノートPCへ大きなリポジトリや開発ツールをすべて入れるのは重く、更新のたびに管理が増えます。この悩みは、持ち歩くPCを「操作端末」、自宅の高性能PCを「開発環境」に分けると整理できます。

この記事では、Windowsを中心に、CodexのRemote SSH、Codex Remote、Windowsリモートデスクトップの違いを説明します。画面名や提供範囲は更新されることがあるため、内容は2026年7月27日時点の公式情報を基準にしています。

## ノートPCへ開発環境を毎回複製すると管理作業が増える

<figure class="codex-remote-figure">
  <img src="/img/blog-codex-remote-duplication-20260727.png" alt="ノートPCと自宅PCへ同じ開発環境を複製し、バージョンやファイルの違いが増えているイメージ" loading="lazy" decoding="async">
  <figcaption>2台へ同じ環境を作ると、コードだけでなくツール、設定、認証、作業中の状態まで二重管理になりやすくなります。</figcaption>
</figure>

Gitでコードを同期できても、開発環境のすべてが同じになるわけではありません。2台で作業すると、次のような差が少しずつ増えます。

- Node.js、Python、パッケージのバージョンが違う
- `.env`やローカル設定が片方にしかない
- GitHubや外部サービスの認証を端末ごとにやり直す
- ビルド成果物やGit管理外ファイルが片方に残る
- 片方では動くのに、もう片方ではPATHが通っていない
- どちらのブランチと作業ツリーが最新か分からなくなる

これはAI開発ツールでも同じです。Codexが操作するファイル、ターミナル、Git、資格情報、権限は、実際に作業するホスト側にあります。外出用PCへ毎回環境を複製するより、開発の本体を自宅PCへ集約し、外から安全に接続するほうが管理しやすくなります。

| 置く場所 | 主な役割 |
|---|---|
| 外出用ノートPC | ChatGPTデスクトップ、SSHクライアント、Tailscale、RDPクライアント |
| 自宅の高性能PC | プロジェクト本体、Git、Codex CLI、Node.js、Python、テスト・ビルド環境 |
| GitHubなどのリモート | バージョン管理、バックアップ、共同作業 |

ただし、自宅PCへ集約することと、バックアップを自宅PCだけにすることは別です。ソースコードはGitで履歴を残し、秘密情報はリポジトリへ入れず、必要なデータには別のバックアップを用意します。

## 共有フォルダではなくRemote SSHを使うと開発環境を一本化できる

<figure class="codex-remote-figure">
  <img src="/img/blog-codex-remote-ssh-centralize-20260727.png" alt="外出先のノートPCから暗号化されたSSH接続で自宅PCの開発環境を操作するイメージ" loading="lazy" decoding="async">
  <figcaption>ファイルだけを共有するのではなく、自宅PC上でコマンド、Git、ビルドまで実行するのがRemote SSHの強みです。</figcaption>
</figure>

共有フォルダはファイルを開くには便利ですが、開発ではファイル監視、依存関係、アクセス権、Git、ビルド速度が絡みます。Remote SSHなら、画面は外出用PCに表示しながら、ファイル操作とコマンド実行を自宅PC側へそろえられます。

安全に始める流れは次のとおりです。

1. 2台へTailscaleを入れ、同じtailnetへ参加させる
2. 自宅PCでWindows OpenSSH Serverを有効にする
3. 外出用PCから通常のSSH接続を確認する
4. SSH鍵を作り、自宅PCへ公開鍵を登録する
5. 外出用PCの`~/.ssh/config`へ具体的な接続名を作る
6. 自宅PCへCodex CLIを入れ、ログインシェルのPATHから実行できるようにする
7. ChatGPTデスクトップの「Settings → Connections」からSSH接続先を選ぶ

Windows OpenSSH Serverは、自宅PCの管理者PowerShellで状態を確認してから有効にします。

```powershell
Get-WindowsCapability -Online |
  Where-Object Name -like 'OpenSSH*'

Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

OpenSSH Serverを導入すると、通常はTCP 22番を許可するWindowsファイアウォール規則も作成されます。ここで必要なのはWindows内の受信許可です。**家庭用ルーターで22番ポートをインターネットへ直接公開する必要はありません。** 外部からはTailscaleなどのVPN・メッシュネットワークを経由させます。

最初の接続確認は、外出用PCから行います。

```powershell
ssh 自宅PCのユーザー名@自宅PCのTailscale-IP
```

接続できたら、外出用PCのSSH設定に分かりやすい別名を作ります。

```sshconfig
Host home-codex
    HostName 100.x.x.x
    User your-windows-user
    IdentityFile C:/Users/your-local-user/.ssh/id_ed25519_home_codex
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

`Host *`だけではなく、`Host home-codex`のような具体的な別名を作ることがポイントです。保存後に次の確認が通れば、ChatGPTデスクトップから選ぶ準備ができています。

```powershell
ssh home-codex
```

公開鍵の保存場所はWindowsのユーザー権限で変わります。

- 標準ユーザー: `C:\Users\ユーザー名\.ssh\authorized_keys`
- Administratorsグループのユーザー: `C:\ProgramData\ssh\administrators_authorized_keys`

管理者用ファイルは、Microsoftの案内に沿ったアクセス権設定も必要です。鍵を置いただけで通らないときは、保存場所とACLを確認します。

最後に、SSHで自宅PCへ入った状態からCodexが見えるか確認します。

```powershell
where.exe codex
codex --version
```

ChatGPTデスクトップは、SSH先のログインシェルからCodexを起動します。自宅PCの画面で動いていても、SSHセッションのPATHから見つからなければ接続できません。Codex CLIの導入と認証は公式ページの最新手順を使い、上の2コマンドが成功する状態まで確認します。

## 接続できない原因はスリープ・SSH鍵・PATHの順に確認する

<figure class="codex-remote-figure">
  <img src="/img/blog-codex-remote-troubleshoot-20260727.png" alt="電源状態、SSH鍵、コマンドのPATHを順番に点検するトラブルシューティングのイメージ" loading="lazy" decoding="async">
  <figcaption>原因を一度に探さず、PCが起きているか、SSHで入れるか、Codexが見えるかの順で切り分けます。</figcaption>
</figure>

遠隔接続で困ったときは、設定を全部やり直す前に「通信」「認証」「実行環境」の3段階へ分けます。

**1. 自宅PCが起きていて、通信できるか**

自宅PCがスリープすると、SSHもRemoteも止まります。画面だけ消す設定は問題ありませんが、電源接続時のスリープは無効にします。Tailscaleは自宅PCで「Run Unattended」を有効にすると、Windowsへサインインする前から接続しやすくなります。

```powershell
tailscale status
tailscale ping 自宅PC名
Test-NetConnection 自宅PCのTailscale-IP -Port 22
```

自宅PC側では、SSHサービスと待ち受けを確認します。

```powershell
Get-Service sshd
Get-NetTCPConnection -LocalPort 22 -State Listen
```

**2. SSHのユーザー名と鍵が合っているか**

通信できるのに`Permission denied`になる場合は、ユーザー名、公開鍵の内容、保存場所、アクセス権を確認します。Windows HelloのPINと、SSHで使うアカウント認証は別物です。最終的にはパスワード依存を減らし、専用のSSH鍵と必要最小限の権限で運用します。

詳しい接続ログは次で確認できます。

```powershell
ssh -vvv home-codex
```

**3. SSH先のPATHからCodexを実行できるか**

SSH接続は成功するのにChatGPTデスクトップで開けない場合は、SSH先で次を実行します。

```powershell
where.exe codex
codex --version
```

見つからなければ、Codex CLIを導入したWindowsユーザー、PATH、シェルの違いを確認します。導入直後なら、一度SSHを終了し、新しいセッションでやり直します。

**4. Codex Remoteだけ表示されない場合**

Codex Remoteは、ホストとなる自宅PCのChatGPTアプリが起動し、Remoteが有効で、同じChatGPTアカウントとワークスペースを使っている必要があります。QRコードでペアリングした端末から、ホスト上のCodexチャットへ追加指示や承認を送れます。

別の対応デスクトップから操作する「Control other devices」は段階的に提供される機能です。項目が表示されない場合でも、Remote SSHやTailscale経由のRDPは別の接続手段として利用できます。

<div class="codex-remote-check">
<p><strong>切り分けの合格ライン</strong></p>

<ol>
  <li><code>tailscale ping</code>が通る</li>
  <li><code>Test-NetConnection ... -Port 22</code>が成功する</li>
  <li><code>ssh home-codex</code>でログインできる</li>
  <li>SSH先で<code>codex --version</code>が表示される</li>
  <li>ChatGPTデスクトップに<code>home-codex</code>が表示される</li>
</ol>
</div>

## SSHを主軸にRemoteとRDPを補助にすると運用が安定する

<figure class="codex-remote-figure">
  <img src="/img/blog-codex-remote-three-layer-20260727.png" alt="Remote SSH、Codex Remote、Windowsリモートデスクトップを役割別に使い分けるイメージ" loading="lazy" decoding="async">
  <figcaption>3つの方法は代替関係ではありません。開発、指示・承認、画面操作の役割に分けると無理がありません。</figcaption>
</figure>

毎日の運用では、1つの接続方法ですべてを済ませようとしないほうが安定します。

| 方法 | 遠隔で操作するもの | 向いている作業 | 主な前提 |
|---|---|---|---|
| Remote SSH | 自宅PCのファイル、ターミナル、Git、開発ツール | 普段の開発、テスト、ビルド | SSH接続、SSH先のCodex CLIとPATH |
| Codex Remote | 自宅PCで動くCodexチャット | 進捗確認、追加指示、質問への回答、承認 | ホストのChatGPTアプリ、同一アカウント、Remote有効 |
| Tailscale＋RDP | 自宅PCのWindows画面全体 | 初回ログイン、ブラウザ認証、Windows設定、緊急保守 | 接続先がWindows Pro系、RDP有効 |

おすすめの構成は次のとおりです。

```text
外出用ノートPC
├─ ChatGPTデスクトップ
├─ Tailscale
├─ OpenSSH Client
└─ リモートデスクトップ接続
        │
        ├─ Remote SSH：普段の開発
        ├─ Codex Remote：指示・承認・結果確認
        └─ RDP：画面操作と初期設定
        │
自宅の高性能PC
├─ プロジェクト本体
├─ Git / Codex CLI / Node.js / Python
├─ OpenSSH Server
├─ Tailscale
└─ ChatGPTデスクトップ
```

RDPの接続先になれるのは、Windows Pro、Enterprise、Educationなどです。Windows Homeは接続する側には使えますが、標準機能でRDPの接続先にはできません。自宅PCがHomeの場合でもRemote SSHとCodex Remoteは別の仕組みなので、RDPだけを必須と考える必要はありません。

Codex Remote自体は、認証された安全なリレーを利用し、自宅PCをインターネットへ直接公開しません。一方、Remote SSHやRDPを外部ネットワークから使う場合は、Tailscaleなどの保護されたネットワーク内へ閉じます。

運用を始める前に、次の安全確認をしておきます。

- ルーターで22番と3389番を直接公開しない
- SSHは専用鍵を使い、秘密鍵にはパスフレーズを付ける
- 普段は管理者権限を使わない
- Codexの危険な操作やネット接続は、必要な承認を残す
- 自宅PCのスリープ、再起動後のTailscale、`sshd`自動起動を確認する
- ソースコードは定期的にGitへ保存する
- `.env`、秘密鍵、個人情報をGitへ入れない
- 自宅PCを第三者が同時操作する場合は、Codexの画面操作と競合させない

### Windows Homeでも利用できますか

Remote SSHとCodex Remoteは、RDPとは別の仕組みです。Windows HomeでもSSH接続やRemoteの条件を満たせば利用できます。ただし、Windows標準RDPの「接続先」にはWindows Pro系が必要です。

### Codex RemoteにTailscaleは必要ですか

Codex Remoteは安全なリレーを使うため、RemoteだけならTailscaleは必須ではありません。ただし、Remote SSHとRDPを自宅の外から使う場合は、ポートを直接公開せず、TailscaleなどのVPN・メッシュネットワークを使う構成が安全です。

### Handoffを使うと全ファイルが別PCへコピーされますか

HandoffはチャットとGitの状態を、同じリポジトリを保存している別の接続先へ移す機能です。PC内の全ファイルを丸ごと同期する仕組みではありません。Git管理外の大容量ファイル、データベース、`.env`、秘密鍵は別に管理します。

### 最初に何から設定すればよいですか

最初はTailscaleとOpenSSH Serverを設定し、外出用PCから`ssh home-codex`が通るところまで進めます。次にSSH先で`codex --version`を確認し、最後にChatGPTデスクトップへ接続先を登録します。RDPは、ブラウザ認証やWindows設定が必要な場面に追加します。

### 参考にした公式情報

- [OpenAI「Remote connections」](https://learn.chatgpt.com/docs/remote-connections)
- [OpenAI Help「Codex in ChatGPT desktop」](https://help.openai.com/en/articles/20001275/)
- [OpenAI「Codex CLI」](https://learn.chatgpt.com/docs/codex/cli)
- [Microsoft Learn「Windows 用 OpenSSH Server の概要」](https://learn.microsoft.com/ja-jp/windows-server/administration/openssh/openssh_install_firstuse)
- [Microsoft Learn「Windows での OpenSSH Server 構成」](https://learn.microsoft.com/ja-jp/windows-server/administration/OpenSSH/openssh-server-configuration)
- [Microsoft Support「リモート デスクトップの使用方法」](https://support.microsoft.com/ja-jp/windows/experience/connectivity-networking/how-to-use-remote-desktop)
- [Tailscale「Access remote desktops using Windows RDP」](https://tailscale.com/docs/solutions/access-remote-desktops-using-windows-rdp)
- [Tailscale「Run unattended」](https://tailscale.com/docs/how-to/run-unattended)

<div class="codex-remote-cta">
  <h3>自分のPC構成に合わせて、安全な接続手順を整理したい方へ</h3>
  <p>AI相談では、彦根・滋賀の事業者、学校、福祉施設、個人事業主の方へ、CodexやAI開発ツールを現場で使い続けるための環境づくりを支援しています。機種、Windows版、普段の作業、外出頻度を確認し、必要な方法だけに絞って一緒に整えます。</p>
  <a href="/#contact">AI個別相談でPC構成を整理する</a>
</div>
