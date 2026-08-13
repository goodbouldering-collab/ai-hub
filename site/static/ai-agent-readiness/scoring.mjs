const makeOptions = (labels) => labels.map((label, index) => ({
  value: [0, 2, 4, 5][index],
  label,
}));

export const COURSE_ROUTES = Object.freeze({
  'ai-consult-entry': Object.freeze({
    id: 'ai-consult-entry',
    name: 'AI無料相談で入口を整理',
    title: 'AI無料相談で入口を整理',
    price: '無料',
    duration: '要予約',
    description: 'いま困っている仕事を一つ選び、最初の安全な一歩を一緒に決めます。',
    summary: 'いま困っている仕事を一つ選び、最初の安全な一歩を一緒に決めます。',
    cta: '無料相談を予約する',
    url: 'https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE',
  }),
  'ai-agent-course': Object.freeze({
    id: 'ai-agent-course',
    name: 'AIエージェント講習',
    title: 'AIエージェント講習 120分',
    price: '5,500円',
    duration: '120分',
    description: '仕事の分解、任せ方、確認方法を実際の業務で練習します。',
    summary: '仕事の分解、任せ方、確認方法を実際の業務で練習します。',
    cta: '講習の内容を見る',
    url: 'https://goodbouldering.com/?pid=188553378',
  }),
  'ai-coding': Object.freeze({
    id: 'ai-coding',
    name: 'AIコーディング講習',
    title: 'AIコーディング講習 120分',
    price: '11,000円',
    duration: '120分',
    description: 'Codex等を使い、コード・Git・テスト・公開までを安全に進める力を磨きます。',
    summary: 'Codex等を使い、コード・Git・テスト・公開までを安全に進める力を磨きます。',
    cta: 'AIコーディング講習を予約する',
    url: 'https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH',
  }),
  'ai-support': Object.freeze({
    id: 'ai-support',
    name: 'AI伴走支援',
    title: 'AI伴走支援を相談する',
    price: '個別相談',
    duration: '継続支援',
    description: '複数の業務やチームへ広げる前に、運用設計と支援範囲を確認します。',
    summary: '複数の業務やチームへ広げる前に、運用設計と支援範囲を確認します。',
    cta: '伴走支援の詳細を見る',
    url: '/#packages',
  }),
});

export const LEVELS = Object.freeze([
  Object.freeze({
    id: 1,
    min: 0,
    max: 24,
    nameEn: 'Explorer',
    nameJa: 'AIの入口を見つける',
    name: 'AIの入口を見つける',
    label: 'Level 1 Explorer',
    description: 'まずは身近な一つの仕事で、AIに頼る部分と人が決める部分を分ける段階です。',
    summary: 'まずは身近な一つの仕事で、AIに頼る部分と人が決める部分を分ける段階です。',
    courseId: 'ai-consult-entry',
  }),
  Object.freeze({
    id: 2,
    min: 25,
    max: 44,
    nameEn: 'Guided AI User',
    nameJa: '対話で仕事を整える',
    name: '対話で仕事を整える',
    label: 'Level 2 Guided AI User',
    description: 'AIとの対話を仕事に使い始め、指示と確認の型を作る段階です。',
    summary: 'AIとの対話を仕事に使い始め、指示と確認の型を作る段階です。',
    courseId: 'ai-agent-course',
  }),
  Object.freeze({
    id: 3,
    min: 45,
    max: 64,
    nameEn: 'Workflow Builder',
    nameJa: '再現できる仕事の型にする',
    name: '再現できる仕事の型にする',
    label: 'Level 3 Workflow Builder',
    description: '一度の成功を手順、判断基準、記録へ変え、繰り返せる段階です。',
    summary: '一度の成功を手順、判断基準、記録へ変え、繰り返せる段階です。',
    courseId: 'ai-agent-course',
  }),
  Object.freeze({
    id: 4,
    min: 65,
    max: 84,
    nameEn: 'Agent Operator',
    nameJa: '任せて検証する',
    name: '任せて検証する',
    label: 'Level 4 Agent Operator',
    description: 'AIエージェントへ範囲を決めて委任し、途中確認と復旧まで管理できる段階です。',
    summary: 'AIエージェントへ範囲を決めて委任し、途中確認と復旧まで管理できる段階です。',
    courseId: 'ai-coding',
  }),
  Object.freeze({
    id: 5,
    min: 85,
    max: 100,
    nameEn: 'Agent Orchestrator',
    nameJa: '複数AIと仕組みを率いる',
    name: '複数AIと仕組みを率いる',
    label: 'Level 5 Agent Orchestrator',
    description: '複数のAI・人・道具を組み合わせ、成果と安全を継続改善できる段階です。',
    summary: '複数のAI・人・道具を組み合わせ、成果と安全を継続改善できる段階です。',
    courseId: 'ai-support',
  }),
]);

export const DIMENSIONS = Object.freeze([
  Object.freeze({
    id: 'humanPurpose',
    nameJa: '人間中心・価値設計',
    name: '人間中心・価値設計',
    nameEn: 'Human Purpose',
    questionIds: Object.freeze(['Q01', 'Q02']),
    nextAction: '対象業務を一つ選び、時間・品質・人が判断する点を紙1枚に決める。',
    measure: '着手前後の所要時間と、利用者にとっての改善を1回記録する。',
  }),
  Object.freeze({
    id: 'aiContext',
    nameJa: 'AI基礎・文脈設計',
    name: 'AI基礎・文脈設計',
    nameEn: 'AI & Context Literacy',
    questionIds: Object.freeze(['Q03', 'Q04', 'Q05']),
    nextAction: '目的、背景、制約、出力例を含む依頼テンプレートを一つ作る。',
    measure: '同じ業務で3回使い、追加修正の回数を比べる。',
  }),
  Object.freeze({
    id: 'workflowValue',
    nameJa: '業務分解・価値測定',
    name: '業務分解・価値測定',
    nameEn: 'Workflow & Value',
    questionIds: Object.freeze(['Q06', 'Q07', 'Q08', 'Q09']),
    nextAction: '一つの定型業務を入力・判断・作業・確認・保存に分けて手順化する。',
    measure: '90日で3回実行し、時間、手戻り、品質の変化を残す。',
  }),
  Object.freeze({
    id: 'verification',
    nameJa: '検証・評価',
    name: '検証・評価',
    nameEn: 'Verification & Evaluation',
    questionIds: Object.freeze(['Q10', 'Q11']),
    nextAction: 'AIの出力を採用する前の合格条件と確認チェックリストを作る。',
    measure: '誤りを一件見つけ、原因と再発防止を記録する。',
  }),
  Object.freeze({
    id: 'safety',
    nameJa: 'データ・権限・安全',
    name: 'データ・権限・安全',
    nameEn: 'Data, Permission & Safety',
    questionIds: Object.freeze(['Q12', 'Q13', 'Q14']),
    nextAction: '入力禁止情報、許可が必要な操作、停止条件の三つを明文化する。',
    measure: '実務フロー一つを権限最小化し、復旧手順まで試す。',
  }),
  Object.freeze({
    id: 'codingSystems',
    nameJa: 'コード・システム',
    name: 'コード・システム',
    nameEn: 'Coding & Systems',
    questionIds: Object.freeze(['Q15', 'Q16']),
    nextAction: '小さな変更をAIと作り、差分確認、テスト、履歴保存まで完了する。',
    measure: '再現できる成果物を一つ公開またはチーム内共有する。',
  }),
  Object.freeze({
    id: 'agentOperations',
    nameJa: 'エージェント運用',
    name: 'エージェント運用',
    nameEn: 'Agent Operations',
    questionIds: Object.freeze(['Q17', 'Q18']),
    nextAction: '完了条件、禁止事項、確認点を決めた小さな仕事をAIへ委任する。',
    measure: '途中確認と引き継ぎ記録を含む実行を3回行う。',
  }),
  Object.freeze({
    id: 'futureAdaptability',
    nameJa: '将来適応力',
    name: '将来適応力',
    nameEn: 'Future Adaptability',
    questionIds: Object.freeze(['Q19', 'Q20']),
    nextAction: '一つの成果物を別のAIでも使える形式に整え、道具を比較する。',
    measure: '月1回、目的に合うAI・画像・音声・動画・外部ツールを見直す。',
  }),
]);

export const FUTURE_INDICATORS = Object.freeze([
  Object.freeze({
    id: 'humanOversight',
    nameEn: 'Human Oversight',
    nameJa: '人が監督する力',
    name: '人が監督する力',
    questionIds: Object.freeze(['Q02', 'Q10', 'Q13', 'Q18']),
    description: '承認点、停止条件、説明責任を保ったままAIへ任せる備え',
  }),
  Object.freeze({
    id: 'evaluationLiteracy',
    nameEn: 'Evaluation Literacy',
    nameJa: '評価する力',
    name: '評価する力',
    questionIds: Object.freeze(['Q08', 'Q10', 'Q11']),
    description: '成功条件、テスト、失敗分析で品質を高める備え',
  }),
  Object.freeze({
    id: 'portability',
    nameEn: 'Portability',
    nameJa: '成果物を持ち運ぶ力',
    name: '成果物を持ち運ぶ力',
    questionIds: Object.freeze(['Q09', 'Q16', 'Q19']),
    description: 'モデルや製品が変わっても仕様、記録、成果物を生かす備え',
  }),
  Object.freeze({
    id: 'multimodalTooling',
    nameEn: 'Tool-using Agent & Multimodal',
    nameJa: '道具を使うAIと複数メディア',
    name: '道具を使うAIと複数メディア',
    questionIds: Object.freeze(['Q15', 'Q17', 'Q20']),
    description: '文章だけでなく画像、音声、動画、API等を目的で選ぶ備え',
  }),
  Object.freeze({
    id: 'valueCreation',
    nameEn: 'Value Creation',
    nameJa: '時間と品質を価値へ変える力',
    name: '時間と品質を価値へ変える力',
    questionIds: Object.freeze(['Q01', 'Q02', 'Q07', 'Q08']),
    description: '速さだけでなく品質、利用者価値、人の自由度を高める備え',
  }),
]);

const QUESTION_DEFINITIONS = [
  Object.freeze({
    id: 'Q01',
    dimensionId: 'humanPurpose',
    prompt: 'AIを使う前に、誰のどんな困りごとを減らすか決めていますか？',
    context: '直近90日の仕事、学習、地域活動を思い出してください。',
    options: makeOptions([
      '目的を決めて使った経験はまだない',
      '困りごとを考え、個人の作業で一度試した',
      '対象者と改善したい状態を決め、複数回使った',
      '利用者の反応や成果を測り、使い方を改善した',
    ]),
  }),
  Object.freeze({
    id: 'Q02',
    dimensionId: 'humanPurpose',
    prompt: 'AIに任せる部分と、人が責任を持って判断する部分を分けていますか？',
    context: '速さだけでなく、本人の選択や尊厳を守る判断も含みます。',
    options: makeOptions([
      '分けて考えたことはまだない',
      '重要な判断は人が行うよう一度意識した',
      '承認が必要な場面を手順に書き、繰り返し運用した',
      '関係者と責任範囲を共有し、レビューや演習結果から改善した',
    ]),
  }),
  Object.freeze({
    id: 'Q03',
    dimensionId: 'aiContext',
    prompt: 'AIがもっともらしく誤ることや、文脈で答えが変わることを前提に使えますか？',
    context: '仕組みの暗記ではなく、限界を踏まえた実際の使い方を答えます。',
    options: makeOptions([
      'AIの得意不得意を説明できず、確認せず使うことがある',
      '誤りがあると理解し、重要な出力を一度確認した',
      '得意不得意に応じて仕事を選び、確認方法を変えている',
      '周囲にも限界を説明し、用途別の利用基準を改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q04',
    dimensionId: 'aiContext',
    prompt: '目的、背景、制約、期待する形式をAIへ具体的に渡せますか？',
    context: '単発の質問ではなく、仕事を進めるための文脈設計です。',
    options: makeOptions([
      '短い質問だけで、必要な情報を整理して渡したことがない',
      '例を見ながら目的や出力形式を指定して試した',
      '再利用できる依頼テンプレートで、安定した結果を得ている',
      '他者も使えるテンプレートを整備し、結果から改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q05',
    dimensionId: 'aiContext',
    prompt: 'AIの最初の回答を完成品とせず、対話で修正できますか？',
    context: '不足の指摘、例の追加、別案比較などの行動を見ます。',
    options: makeOptions([
      '最初の回答をそのまま使うか、諦めることが多い',
      '追加質問や書き直しを一度試した',
      '評価基準を伝えて複数案を比較し、実務で選んでいる',
      '修正履歴を残し、他者も再現できる対話手順にしている',
    ]),
  }),
  Object.freeze({
    id: 'Q06',
    dimensionId: 'workflowValue',
    prompt: '大きな仕事を、AIに渡せる小さな作業と人の判断に分けられますか？',
    context: '入力、調査、作成、確認、承認、保存などに分けます。',
    options: makeOptions([
      '仕事を丸ごと頼み、途中の作業を分けたことがない',
      '例を見ながら一つの仕事を小さく分けて試した',
      '複数の仕事で分解し、担当と完了条件を明確にしている',
      'チームで使える分解手順を整え、結果から更新している',
    ]),
  }),
  Object.freeze({
    id: 'Q07',
    dimensionId: 'workflowValue',
    prompt: 'うまくいったAI活用を、繰り返せる業務手順にしていますか？',
    context: 'プロンプトだけでなく入力元、確認、保存先まで含めます。',
    options: makeOptions([
      'その場限りの利用で、手順を残したことがない',
      '自分用に手順や入力例を一度残した',
      '同じ手順を複数回使い、同程度の品質を再現している',
      '他者へ展開し、時間や品質を見て手順を改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q08',
    dimensionId: 'workflowValue',
    prompt: 'AI導入の効果を、時間短縮以外の品質や利用者価値でも測っていますか？',
    context: '誤り、手戻り、満足度、学習成果、余裕時間なども指標です。',
    options: makeOptions([
      '便利そうという感覚だけで、変化を測ったことがない',
      '作業時間など一つの変化を一度記録した',
      '時間と品質の両方を複数回測り、導入判断に使っている',
      '関係者の価値まで定期評価し、続行や停止を見直している',
    ]),
  }),
  Object.freeze({
    id: 'Q09',
    dimensionId: 'workflowValue',
    prompt: 'AIが作った成果物と判断の経緯を、後から使える形で残していますか？',
    context: '仕様、出典、版、決定理由、次の作業が追える状態を見ます。',
    options: makeOptions([
      '会話画面だけに残り、後から探せないことが多い',
      '重要な成果物をファイルへ保存したことがある',
      '出典や版と一緒に整理し、別の日にも再利用している',
      '共通形式でチーム共有し、引き継ぎや監査にも使っている',
    ]),
  }),
  Object.freeze({
    id: 'Q10',
    dimensionId: 'verification',
    prompt: 'AIの出力を採用する前に、合格条件と確認方法を決めていますか？',
    context: '出典照合、計算確認、実画面確認、テストなどを含みます。',
    options: makeOptions([
      '読みやすければ採用し、決まった確認方法はない',
      '重要な事実や数字を一度、別の情報で確認した',
      '用途別チェックリストやテストで毎回確認している',
      '第三者レビューと失敗記録を使い、合格条件を改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q11',
    dimensionId: 'verification',
    prompt: '失敗しやすい例や例外条件でもAIの仕組みを試していますか？',
    context: '正常な一例だけでなく、空欄、誤入力、極端な条件も確認します。',
    options: makeOptions([
      'うまくいった一例だけで使い始めることが多い',
      '失敗例や例外を一度試し、修正した',
      '代表的な正常・異常ケースを毎回テストし記録している',
      '失敗例や安全な演習結果も共有し、継続的にテストを増やしている',
    ]),
  }),
  Object.freeze({
    id: 'Q12',
    dimensionId: 'safety',
    prompt: '個人情報、機密情報、著作物をAIへ入れる前に扱いを判断できますか？',
    context: '利用規約、組織ルール、本人同意、匿名化も含みます。',
    options: makeOptions([
      '入力してよい情報と禁止情報を区別できていない',
      '迷う情報を入れず、規約や担当者を一度確認した',
      '情報区分と匿名化の手順を決め、日常的に守っている',
      '関係者へ教育し、ルール違反や変更を受けて更新している',
    ]),
  }),
  Object.freeze({
    id: 'Q13',
    dimensionId: 'safety',
    prompt: 'AIへ与えるファイル・外部サービス・更新権限を必要最小限にできますか？',
    context: '閲覧と書込み、本番と練習、実行前承認を分けます。',
    options: makeOptions([
      '求められた権限をそのまま与え、範囲を確認していない',
      '重要操作の前に人が確認する設定を一度使った',
      '最小権限、練習環境、承認点を決めて繰り返し運用している',
      '権限記録を監査し、役割や点検結果に応じて定期更新している',
    ]),
  }),
  Object.freeze({
    id: 'Q14',
    dimensionId: 'safety',
    prompt: 'AIの処理を止め、元に戻し、何が起きたか確認する準備がありますか？',
    context: '停止条件、バックアップ、復旧、操作記録を見ます。',
    options: makeOptions([
      '問題時の停止や復旧方法を決めていない',
      '保存やバックアップから一度戻したことがある',
      '停止条件と復旧手順を決め、事前に試している',
      '操作記録から原因を調べ、演習と手順改善を続けている',
    ]),
  }),
  Object.freeze({
    id: 'Q15',
    dimensionId: 'codingSystems',
    prompt: 'AIと一緒にファイル、コード、データ、外部ツールを扱えますか？',
    context: 'HTML、表計算、スクリプト、API、データベース等から必要な範囲を見ます。',
    options: makeOptions([
      'AIとの文章対話以外はまだ試していない',
      '手順を見ながらファイルや簡単なコードを一度扱った',
      '実務用の小さな仕組みを作り、動作を確認して使っている',
      '複数の道具を安全につなぎ、他者が使える形へ整えている',
    ]),
  }),
  Object.freeze({
    id: 'Q16',
    dimensionId: 'codingSystems',
    prompt: 'AIが変更した内容を比較し、テストし、履歴から戻せますか？',
    context: 'Git等の名称より、差分・テスト・公開・復旧の実践を重視します。',
    options: makeOptions([
      '変更点が分からないまま上書きすることがある',
      '元ファイルを残し、変更前後を一度比較した',
      '差分確認、テスト、履歴保存を行ってから反映している',
      '自動テストと段階公開を整え、安全な復旧演習または実障害から戻せる',
    ]),
  }),
  Object.freeze({
    id: 'Q17',
    dimensionId: 'agentOperations',
    prompt: 'AIエージェントへ、範囲と完了条件を決めた仕事を任せられますか？',
    context: '自分で全操作する対話ではなく、計画・実行・確認を伴う委任です。',
    options: makeOptions([
      'エージェントへ仕事を任せた経験はまだない',
      '手順を見ながら小さな作業を一度任せた',
      '目的、禁止事項、完了条件を渡し、結果を検証している',
      '複数業務へ展開し、成功率や手戻りを見て改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q18',
    dimensionId: 'agentOperations',
    prompt: '長い作業や複数エージェントを、途中確認と引き継ぎで管理できますか？',
    context: '並列化そのものより、監督、停止、統合、説明責任を見ます。',
    options: makeOptions([
      '途中経過を確認せず、最後の出力だけを見ることが多い',
      '途中で状況を確認し、必要なら止めたことがある',
      '確認点、担当、成果物を決めて長い作業を完了している',
      '複数のAIと人の引き継ぎを設計し、運用品質を改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q19',
    dimensionId: 'futureAdaptability',
    prompt: '特定のAI製品が変わっても、成果物と仕事の型を移せますか？',
    context: '開いたファイル形式、仕様書、プロンプト、出典、履歴を見ます。',
    options: makeOptions([
      '成果が一つの会話や製品の中だけに残っている',
      '重要な成果物を一般的な形式で一度保存した',
      '別のAIでも使える仕様と資料にし、切替を試している',
      '複数モデルを目的で選び、移行手順を継続的に更新している',
    ]),
  }),
  Object.freeze({
    id: 'Q20',
    dimensionId: 'futureAdaptability',
    prompt: '文章以外のAIや新しい道具を、流行ではなく目的で選べますか？',
    context: '画像、音声、動画、検索、API、MCP、ロボット等への備えです。',
    options: makeOptions([
      '新しいAIの違いを調べたり試したりしていない',
      '一つの新機能を安全な題材で試した',
      '目的、品質、費用、危険性を比べて道具を選んでいる',
      '定期的に評価し、不要な道具をやめて運用を更新している',
    ]),
  }),
];

export const QUESTIONS = Object.freeze(QUESTION_DEFINITIONS.map((question) => Object.freeze({
  ...question,
  title: question.prompt,
  scenario: question.context,
})));

const ALLOWED_SCORES = new Set([0, 2, 4, 5]);

export function levelForScore(score) {
  const numericScore = Number.isFinite(Number(score)) ? Number(score) : 0;
  const boundedScore = Math.max(0, Math.min(100, numericScore));
  return LEVELS.find((level) => boundedScore >= level.min && boundedScore <= level.max) ?? LEVELS[0];
}

function scoresForGroups(groups, answers) {
  return groups.map((group) => {
    const points = group.questionIds.reduce((total, questionId) => total + answers[questionId], 0);
    const maxPoints = group.questionIds.length * 5;
    return {
      ...group,
      name: group.nameJa,
      score: points,
      maxScore: maxPoints,
      points,
      maxPoints,
      percent: Math.round((points / maxPoints) * 100),
    };
  });
}

function assessmentGate(dimensionScores, unrestrictedLevel) {
  const byId = Object.fromEntries(dimensionScores.map((dimension) => [dimension.id, dimension]));
  let maxLevel = 5;
  const reasons = [];

  if (byId.verification.percent < 50 || byId.safety.percent < 50) {
    maxLevel = 3;
    reasons.push('検証または安全の実践が50%未満のため、まず人の確認と権限管理を整えます。');
  }
  if (byId.agentOperations.percent < 60) {
    maxLevel = Math.min(maxLevel, 4);
    reasons.push('エージェント運用が60%未満のため、委任・途中確認・復旧を先に練習します。');
  }
  if (unrestrictedLevel.id === 5) {
    const belowOrchestratorThreshold = dimensionScores.filter(({ percent }) => percent < 60);
    if (belowOrchestratorThreshold.length > 0) {
      maxLevel = Math.min(maxLevel, 4);
      const dimensionNames = belowOrchestratorThreshold.map(({ nameJa }) => nameJa).join('・');
      reasons.push(`Level 5は全8領域60%以上が目安です。${dimensionNames}を先に整えます。`);
    }
  }

  const applied = unrestrictedLevel.id > maxLevel;
  const requirementsMet = reasons.length === 0;
  return {
    applied,
    requirementsMet,
    maxLevel,
    reasons,
    message: reasons.join(' '),
  };
}

function makeConsultationData({ rawScore, level, gate, lowestDimension, next90DayTarget, course }) {
  const data = {
    score: rawScore,
    levelId: level.id,
    levelName: `${level.nameEn} / ${level.nameJa}`,
    focusDimension: next90DayTarget.dimensionName,
    target: next90DayTarget.action,
    measure: next90DayTarget.measure,
    recommendedCourse: course.title,
    gateNote: gate.requirementsMet ? '安全ゲートによるレベル調整なし' : gate.message,
  };
  const text = [
    'AI Agent Readiness Compass 相談メモ',
    `現在地: ${data.score}点・Level ${data.levelId} ${data.levelName}`,
    `優先領域: ${data.focusDimension}`,
    `90日目標: ${data.target}`,
    `確認指標: ${data.measure}`,
    `AI相談の案内（任意）: ${data.recommendedCourse}`,
    `安全確認: ${data.gateNote}`,
  ].join('\n');
  return { ...data, text };
}

export function scoreAssessment(answers = {}) {
  const validAnswers = {};
  const missingQuestionIds = [];

  for (const question of QUESTIONS) {
    const answer = Number(answers[question.id]);
    if (!ALLOWED_SCORES.has(answer) || answers[question.id] === '' || answers[question.id] == null) {
      missingQuestionIds.push(question.id);
      continue;
    }
    validAnswers[question.id] = answer;
  }

  const answeredCount = QUESTIONS.length - missingQuestionIds.length;
  const rawScore = Object.values(validAnswers).reduce((total, value) => total + value, 0);
  if (missingQuestionIds.length > 0) {
    return {
      complete: false,
      answeredCount,
      totalQuestions: QUESTIONS.length,
      missingQuestionIds,
      rawScore,
      level: null,
      unrestrictedLevel: null,
      dimensionScores: [],
      futureScores: [],
      gate: null,
      course: null,
      lowestDimension: null,
      lowestDimensions: [],
      next90DayTarget: null,
      ninetyDayTarget: null,
      consultationData: null,
      consultationMemo: '',
    };
  }

  const unrestrictedLevel = levelForScore(rawScore);
  const dimensionScores = scoresForGroups(DIMENSIONS, validAnswers);
  const futureScores = scoresForGroups(FUTURE_INDICATORS, validAnswers);
  const gate = assessmentGate(dimensionScores, unrestrictedLevel);
  const level = LEVELS[Math.min(unrestrictedLevel.id, gate.maxLevel) - 1];
  const course = COURSE_ROUTES[level.courseId];
  const rankedDimensions = [...dimensionScores].sort((left, right) => (
    left.percent - right.percent || DIMENSIONS.findIndex(({ id }) => id === left.id) - DIMENSIONS.findIndex(({ id }) => id === right.id)
  ));
  const lowestDimension = rankedDimensions[0];
  const lowestDimensions = rankedDimensions.filter(({ percent }) => percent === lowestDimension.percent);
  const selectionNote = lowestDimensions.length > 1
    ? `最下位が同率のため、学習の土台となる「${lowestDimension.nameJa}」を先に表示しています。同率: ${lowestDimensions.map(({ nameJa }) => nameJa).join('・')}`
    : '';
  const next90DayTarget = lowestDimension.percent === 100
    ? {
      dimensionId: 'capstone',
      dimensionName: '全8領域',
      title: '100点を維持・証明する90日',
      action: '小さなAIエージェント業務を一つ、他者へ引き継げる仕様・権限・評価・復旧手順としてまとめる。',
      measure: '第三者レビューと安全な復旧演習を一回行い、改善履歴を残す。',
      selectionNote: '全領域が満点のため、次は自己申告を成果物と第三者レビューで確かめます。',
    }
    : {
      dimensionId: lowestDimension.id,
      dimensionName: lowestDimension.nameJa,
      title: `${lowestDimension.nameJa}を90日で一段上げる`,
      action: lowestDimension.nextAction,
      measure: lowestDimension.measure,
      selectionNote,
    };
  const ninetyDayTarget = {
    level: level.id,
    score: rawScore,
    label: next90DayTarget.title,
    steps: [next90DayTarget.action, next90DayTarget.measure],
    ...next90DayTarget,
  };
  const consultationData = makeConsultationData({
    rawScore,
    level,
    gate,
    lowestDimension,
    next90DayTarget,
    course,
  });

  return {
    complete: true,
    answeredCount,
    totalQuestions: QUESTIONS.length,
    missingQuestionIds,
    rawScore,
    level,
    unrestrictedLevel,
    dimensionScores,
    futureScores,
    gate,
    course,
    lowestDimension,
    lowestDimensions,
    next90DayTarget,
    ninetyDayTarget,
    consultationData,
    consultationMemo: consultationData.text,
  };
}
