# 出典台帳

最終確認日: 2026-08-01

## 日本の法令・行政ガイド

1. [個人情報保護委員会: 生成AIサービスの利用に関する注意喚起等](https://www.ppc.go.jp/news/careful_information/230602_AI_utilize_alert/)
   - 個人データを入力する際の利用目的、本人同意、機械学習利用の確認。
2. [個人情報保護委員会: 外国にある第三者への提供編](https://www.ppc.go.jp/personalinfo/legal/guidelines_offshore/)
   - 国外事業者・外国制度を含む取扱いの確認。
3. [個人情報保護委員会: 匿名加工情報・仮名加工情報FAQ](https://www.ppc.go.jp/all_faq_index/faq1-q14-1/)
   - 匿名化と仮名化を混同しないための定義確認。
4. [個人情報保護委員会: 仮名加工情報FAQ](https://www.ppc.go.jp/all_faq_index/faq2-q2-2/)
   - 仮名加工情報の取扱い。
5. [個人情報保護委員会: 漏えい等報告・本人通知の義務化](https://www.ppc.go.jp/news/kaiseihou_feature/roueitouhoukoku_gimuka/)
   - 誤入力が直ちに全件報告ではないこと、報告対象類型の確認。
6. [経済産業省: AI事業者ガイドライン第1.2版](https://www.meti.go.jp/shingikai/mono_info_service/ai_shakai_jisso/20260331_report.html)
   - リスクベースのガバナンス、プライバシー、セキュリティ。

## OpenAI

7. [OpenAI: How does ChatGPT work support enterprise privacy and data commitments?](https://learn.chatgpt.com/docs/enterprise/work-admin-faq#how-does-chatgpt-work-support-enterprise-privacy-and-data-commitments)
   - 業務データの学習除外、暗号化、アクセス制御、監査、プラン・機能差。
8. [OpenAI: Understand data flow and security for apps and connectors](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors#understand-data-flow-and-security)
   - 接続先の権限継承、同期インデックス、接続サービス独自の保持・ログ。
9. [OpenAI API: Your data](https://developers.openai.com/api/docs/guides/your-data)
   - APIの学習方針、不正利用監視ログ、保持、Zero Data Retention等。
10. [OpenAI Help: Data sharing and privacy in ChatGPT Business](https://help.openai.com/en/articles/8798634-managing-data-sharing-and-privacy-in-chatgpt-business)
    - Business/Codexの業務データと学習方針。
11. [OpenAI Help: Enterprise privacy](https://help.openai.com/en/articles/8983130-what-is-the-chatgpt-enterprise-and-team-data-policy)
    - 個人向けとBusiness/Enterprise/Edu/APIの既定差。
12. [OpenAI Help: Temporary Chat](https://help.openai.com/en/articles/7730893-temporary-chat)
    - 履歴・学習利用と最大30日の安全目的保持。
13. [OpenAI Help: Chat and file retention](https://help.openai.com/en/articles/8983778-chat-and-file-retention-policies-in-chatgpt)
    - 通常チャット・削除済みチャット・ファイルの保持。
14. [OpenAI: March 20 ChatGPT outage](https://openai.com/index/march-20-chatgpt-outage/)
    - 2023年の障害で一部利用者情報が他利用者へ表示された実例。

## Microsoft

15. [Microsoft Learn: Manage Copilot in Windows](https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot)
    - 個人向けMicrosoft CopilotとEntra IDのMicrosoft 365 Copilot Chatの区別。
16. [Microsoft Learn: Privacy and protections in Microsoft 365 Copilot](https://learn.microsoft.com/en-ca/copilot/privacy-and-protections)
    - M365サービス境界、基盤モデル学習除外、Exchange上の監査・eDiscoveryログ。
17. [Microsoft Support: Microsoft Copilot privacy controls](https://support.microsoft.com/en-us/microsoft-copilot/microsoft-copilot-privacy-controls)
    - 個人アカウント側の履歴と学習設定。
18. [Microsoft Learn: Data, Privacy, and Security for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/security-microsoft-365-copilot)
    - 既存権限の尊重と過剰共有リスク。
19. [Microsoft Learn: Prepare SharePoint for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/get-ready-copilot-sharepoint-advanced-management)
    - SharePointの過剰共有の発見と是正。

## セキュリティ標準・実務

20. [OWASP: Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
    - エージェントの機能・権限・自律性を最小化し、高影響操作は人が承認。
21. [NCSC: Guidelines for secure AI system development](https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development/introduction)
    - AIシステムの設計・開発・運用・保守を通じた安全策。
22. [NCSC: Secure design](https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development/guidelines/secure-design)
    - 外部API、機密データ、最小権限、プロンプトインジェクション。
23. [NIST: Artificial Intelligence Risk Management Framework, Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
    - プライバシー、記憶、推論、データガバナンスのリスク。

## 組織利用・事故事例

24. [Gartner Japan: シャドーAIに関する調査](https://www.gartner.co.jp/ja/newsroom/press-releases/pr-20260618-aibs-shadow-ai)
    - 単純な遮断ではなく、可視化・評価・承認・統制を推奨。
25. [Microsoft Work Trend Index 2024](https://www.microsoft.com/en-us/worklab/work-trend-index/ai-at-work-is-here-now-comes-the-hard-part)
    - 世界調査でAI利用者の78%が私物AIを職場へ持ち込んだという報告。ベンダー調査・2024年資料として限定的に使用。
26. [IBM: Cost of a Data Breach Report 2025](https://www.ibm.com/reports/data-breach)
    - シャドーAIを含む未統制環境の侵害コスト。
27. [IBM newsroom: AI model/application breaches and access controls](https://newsroom.ibm.com/2025-07-30-ibm-report-13-of-organizations-reported-breaches-of-ai-models-or-applications%2C-97-of-which-reported-lacking-proper-ai-access-controls)
    - 調査対象のAI関連侵害とアクセス制御不足。母集団・調査条件付きで扱う。
28. [Bloomberg Law: Samsung bans staff AI use after sensitive code incident](https://news.bloomberglaw.com/tech-and-telecom-law/samsung-bans-staffs-ai-use-after-spotting-chatgpt-data-leak-2)
    - 従業員が機密ソースコード等を外部AIへ入力した報道。一般公開・他ユーザー閲覧が確認された事例とは表現しない。

## 採用しなかった断定

- 「AIに入力すればモデルが必ず丸暗記し、別ユーザーにそのまま回答する」
- 「企業向けプランなら何を入力しても安全」
- 「全面禁止が情報漏えいを必ず増やす」
- 「CopilotならMicrosoft製なので無条件で安全」
- 「AIが生成したコードを使っただけで、実行時データがAI会社へ送られる」
