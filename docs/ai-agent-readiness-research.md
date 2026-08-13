# AI Agent Readiness Compass — 調査ノート

調査日: 2026-08-13
用途: 診断設計、講習改善、YouTube・SNS・note・Webサイトへの再編集

## 結論

診断は「AIツールを何個知っているか」ではなく、次の行動を測る。

1. 人の目的と責任を先に決める
2. 仕事を分け、必要な文脈を渡す
3. 出力を一次情報・テスト・実画面で確かめる
4. データ、権限、公開、課金、削除に人の承認点を置く
5. 成果物、仕様、履歴を持ち運べる形で残す
6. 時短だけでなく、品質、利用者価値、余暇時間を測る
7. 特定モデルに依存せず、新しいモダリティや接続方式を小さく評価する

公開版は学習用セルフチェックとし、心理検査、資格、採用・適職判定、法令適合証明、将来の収入予測には使わない。科学的な能力試験と呼ぶには用途別の妥当性検証が必要であり、現段階では成果物課題や第三者レビューを併用する。

## 設計に使った公開資料

| 資料 | 診断への反映 | 注意 |
|---|---|---|
| [OECD / European Commission: Empowering Learners for the Age of AI](https://www.oecd.org/en/publications/empowering-learners-for-the-age-of-ai_65cd27d4-en.html) | Engage / Create / Manage / Shape、知識・技能・態度を成人の仕事向けへ再構成 | 学校教育向け。OECD認定とは表示しない |
| [UNESCO AI Competency Framework](https://www.unesco.org/en/articles/ai-competency-framework-students) | 人間中心、倫理、基礎・応用、設計を段階化 | 学生向けの原典を独自再構成 |
| [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) と [GenAI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | 作話、個人情報、過信、出力検証、継続的リスク管理 | 法令適合の証明にはしない |
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | workflowとagentを区別し、単純な構成、停止条件、環境からの確認を優先 | 特定製品の利用頻度は採点しない |
| [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) | model / tools / instructions、ガードレール、人間介入、リスク別権限 | 自律性の高さをそのまま高得点にしない |
| [OpenAI: Running Codex safely](https://openai.com/index/running-codex-safely/) | sandbox、承認、境界、監査を安全ゲートへ反映 | 製品仕様は更新されるため公式情報を優先 |
| [ILO–NASK: Generative AI and jobs](https://www.ilo.org/resource/news/one-four-jobs-risk-being-transformed-genai-new-ilo%E2%80%93nask-global-index-shows) | AIを人員削減の点数ではなく、仕事の変容・品質向上の学習へ結び付ける | 露出可能性は仕事全体の自動化率ではない |

## ユーザー指定動画と一次資料から整理した「今後のAI指標」

指定動画: [ReHacQ「AI業界大激震…半年間で激変」](https://www.youtube.com/watch?v=2gtWv3iib8M&list=PLOI7QjtBx9_yavYb1jZZwQXgEa2HALAKQ)
公開: 2026-08-12 / 38分01秒 / 2026-08-13確認時 約27万回

対談の個別の主張や予測は、正答や点数の閾値に使っていない。対談で見つけた論点のうち、一次資料と照合できるものを次の学習項目へ翻訳した。

- 能力の一般化と悪用可能性 → 最小権限、承認、停止、監査
- モデル選択の流動性 → 成果物、仕様、出典を持ち運べる形で保存
- 知能だけでは事業価値にならない → 時間、品質、利用者価値を測る
- 動画生成と物理AIの進展 → 文章以外のAIも目的、費用、安全で比較
- 高度化する委任 → 完了条件、テスト、途中確認、人の最終責任

この動画は関心喚起と未来を考える入口には適しているが、体系講座や一次技術資料ではない。個別発言を正答や閾値にはせず、一次資料と照合した論点の発見に使う。

## 公開YouTubeの選定

非公開の視聴履歴にはアクセスせず、共有されたURL、公開プレイリスト、公開検索結果だけを確認した。再生数は調査時点の概数であり、正確性や学習効果の証明ではない。

| 役割 | 動画 | 選定理由 |
|---|---|---|
| 最新動向 | [ユーザー指定 ReHacQ](https://www.youtube.com/watch?v=2gtWv3iib8M) | 関心を持ちやすく、社会・事業・安全を同時に考えられる |
| 日本語の入口 | [PIVOT: Claude Code解説](https://www.youtube.com/watch?v=LRSSjGwsuv0) | 2026-08-13確認時 約159万回。AIを仕事のチームとして捉えるイメージを日本語で得やすい |
| Codex公式入門 | [OpenAI: Getting started with Codex](https://www.youtube.com/watch?v=px7XlbYgk7I) | 導入、リポジトリ、AGENTS.md、依頼、CLI・IDE、MCPを公式に確認できる |
| Agent体系講座 | [Microsoft Developer: AI Agents for Beginners](https://www.youtube.com/watch?v=OhI005_aJkA) | 設計、tools、RAG、planning、multi-agent、productionを体系的に学べる |
| 人間の監督 | [安野貴博: Human on the Loop](https://www.youtube.com/watch?v=K6KX41tLH2s) | 人が全操作せず、仕組み全体を監督する考え方への入口。二次解説として扱う |

人気検索には短いマーケティング動画や古いCodex動画も混在したため、再生数だけで並べず、公式性、更新性、初心者適合、実務への接続で選別した。

## 媒体別の再編集案

- YouTube: 「AIに聞く人から、任せて確かめる人へ」を20分で解説し、公開診断へ誘導
- Shorts / Reels: 8領域を1本1問で紹介。「AIが完成と言ったら完成？」など場面問題で始める
- note / ブログ: 「100点でも安全管理が弱ければLevel 3になる理由」を根拠リンク付きで解説
- SNS: 診断結果の点数自慢ではなく「次の90日で増やす1行動」を共有
- 講習: 受講前後に同じ診断を行い、得点差より成果物、確認手順、時間・品質の変化を記録
