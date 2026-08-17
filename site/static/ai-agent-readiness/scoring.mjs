const SCORE_MULTIPLIER = 2;
const MAX_ANSWER_SCORE = 5;

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
    nameJa: '目的と人の判断',
    name: '目的と人の判断',
    nameEn: 'Purpose & Human Judgment',
    questionIds: Object.freeze(['Q01', 'Q02']),
    nextAction: '今週、AIで軽くしたい仕事を一つ選び、「誰の何が良くなるか」と人が決める場面を一枚に書く。',
    measure: 'その仕事を一回試し、かかった時間と利用者・関係者の反応を一行で残す。',
  }),
  Object.freeze({
    id: 'briefing',
    nameJa: '頼み方と仕事の分解',
    name: '頼み方と仕事の分解',
    nameEn: 'Briefing & Task Design',
    questionIds: Object.freeze(['Q03', 'Q04']),
    nextAction: '目的、相手、材料、制約、完成例、終わりの条件を含む依頼テンプレートを一つ作る。',
    measure: '同じ仕事で三回使い、AIへの追加説明や手戻りが何回減ったかを比べる。',
  }),
  Object.freeze({
    id: 'verification',
    nameJa: '確かめて直す力',
    name: '確かめて直す力',
    nameEn: 'Verification & Improvement',
    questionIds: Object.freeze(['Q05', 'Q06']),
    nextAction: '一つの成果物に、事実・出典・相手向け表現・完成条件の確認チェックを付ける。',
    measure: 'AIの誤りか使いにくさを一件見つけ、直した理由と次回の依頼文への反映を残す。',
  }),
  Object.freeze({
    id: 'safety',
    nameJa: '安全に任せる力',
    name: '安全に任せる力',
    nameEn: 'Data, Permission & Safety',
    questionIds: Object.freeze(['Q07', 'Q08']),
    nextAction: '入力禁止情報、許可が必要な操作、止める・戻す・相談する条件を、小さな仕事一つに決める。',
    measure: '安全な題材で一度試し、確認者と復旧手順まで含めて振り返る。',
  }),
  Object.freeze({
    id: 'improvement',
    nameJa: '残して続ける力',
    name: '残して続ける力',
    nameEn: 'Repeatable Practice',
    questionIds: Object.freeze(['Q09', 'Q10']),
    nextAction: 'うまくいった依頼、確認手順、成果物を次回も使える場所に残し、次の改善を一つ決める。',
    measure: '一か月後に同じ型を再利用し、時間・品質・手戻りのどれか一つを比べる。',
  }),
]);

export const FUTURE_INDICATORS = Object.freeze([
  Object.freeze({
    id: 'humanOversight',
    nameEn: 'Human Oversight',
    nameJa: '人が監督する力',
    name: '人が監督する力',
    questionIds: Object.freeze(['Q02', 'Q08']),
    description: '承認点、停止条件、説明責任を保ったままAIへ任せる備え',
  }),
  Object.freeze({
    id: 'evaluationLiteracy',
    nameEn: 'Evaluation Literacy',
    nameJa: '評価する力',
    name: '評価する力',
    questionIds: Object.freeze(['Q05', 'Q06']),
    description: '成功条件、確認、失敗分析で品質を高める備え',
  }),
  Object.freeze({
    id: 'safeOperations',
    nameEn: 'Safe AI Operations',
    nameJa: '安全に運用する力',
    name: '安全に運用する力',
    questionIds: Object.freeze(['Q07', 'Q08', 'Q10']),
    description: 'データ・権限・小さな検証から、安全に範囲を広げる備え',
  }),
  Object.freeze({
    id: 'repeatableWorkflow',
    nameEn: 'Repeatable Workflow',
    nameJa: '仕事の型を残す力',
    name: '仕事の型を残す力',
    questionIds: Object.freeze(['Q03', 'Q04', 'Q09']),
    description: '頼み方、完成条件、成果物を次回も使える形で残す備え',
  }),
  Object.freeze({
    id: 'valueCreation',
    nameEn: 'Value Creation',
    nameJa: '時間と品質を価値へ変える力',
    name: '時間と品質を価値へ変える力',
    questionIds: Object.freeze(['Q01', 'Q02', 'Q09']),
    description: '速さだけでなく品質、利用者価値、人の自由度を高める備え',
  }),
]);

const QUESTION_DEFINITIONS = [
  Object.freeze({
    id: 'Q01',
    dimensionId: 'humanPurpose',
    prompt: 'AIを使う前に、「誰の、どの仕事を、どう良くするか」を一文で決めていますか？',
    context: '例: 「毎週のイベント告知を30分短くし、初めての人にも迷わない文にする」。',
    learningPoint: '良いAI活用は、道具選びより先に「誰の何を良くするか」を決めるところから始まります。',
    options: makeOptions([
      '何を良くしたいか決めずに、AIを試すことが多い',
      '困りごとを一つ選び、個人の作業で一度試した',
      '対象者と良くなる状態を書き、複数回使った',
      '利用者の反応や時間を測り、使い方をレビューして改善した',
    ]),
  }),
  Object.freeze({
    id: 'Q02',
    dimensionId: 'humanPurpose',
    prompt: 'AIの提案をそのまま出さず、人が決める場面と確認する人を決めていますか？',
    context: 'たとえば公開、金額、個人への連絡、支援の優先順位は人が最終判断します。',
    learningPoint: 'AIが速く作れても、責任まで任せないことが信頼を守ります。先に「人が決める点」を決めます。',
    options: makeOptions([
      '人が決める場面を分けず、出力をそのまま使うことがある',
      '重要な判断は人が行うよう、一度意識して使った',
      '承認が必要な場面と確認者を手順に書き、繰り返し使った',
      '関係者と責任範囲を共有し、レビュー結果から運用を改善した',
    ]),
  }),
  Object.freeze({
    id: 'Q03',
    dimensionId: 'briefing',
    prompt: 'AIへの依頼に、目的・相手・材料・制約・完成例を入れていますか？',
    context: '長い指示が正解ではありません。相手に伝わる仕事の条件がそろっているかを見ます。',
    learningPoint: '頼み方は魔法の言葉ではなく、仕事の条件を相手へ渡す技術です。足りない情報ほど手戻りになります。',
    options: makeOptions([
      '短い依頼だけで、意図と違う結果を受け取ることが多い',
      '目的や材料を足して、一度は依頼を改善した',
      '目的、相手、制約、完成例を含む型を使っている',
      '依頼テンプレートを共有し、結果を見て型を更新している',
    ]),
  }),
  Object.freeze({
    id: 'Q04',
    dimensionId: 'briefing',
    prompt: '大きな仕事を、AIに任せる小さな作業と「終わりの条件」に分けていますか？',
    context: 'いきなり丸投げせず、下書き、整理、確認、公開のように小さく区切ります。',
    learningPoint: '任せる力は、AIにできることを増やす前に「どこまで終われば成功か」を見える形にする力です。',
    options: makeOptions([
      '仕事を一括で頼み、何を確認すればよいか迷うことが多い',
      '一部の作業を小さく分けて、一度試した',
      '作業ごとの完了条件と確認点を決め、繰り返し使った',
      '途中確認と引き継ぎまで設計し、手戻りを見て改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q05',
    dimensionId: 'verification',
    prompt: 'AIの出力を使う前に、事実・出典・計算・相手向け表現を確かめる基準がありますか？',
    context: '正しさは「AIが言った」では決まりません。仕事に出す前の合格条件を決めます。',
    learningPoint: '確認はAIを疑うためではなく、相手に安心して渡せる成果物にするための最後の仕事です。',
    options: makeOptions([
      '確認の基準がなく、AIの回答をほぼそのまま使うことがある',
      '気になる部分だけ、自分で一度確認した',
      '出典や完成条件のチェックリストを使い、毎回確認している',
      '第三者レビューや安全な演習で基準を試し、更新している',
    ]),
  }),
  Object.freeze({
    id: 'Q06',
    dimensionId: 'verification',
    prompt: '誤りや使いにくさを見つけたとき、原因と直し方を残して次回に生かしていますか？',
    context: '修正のたびにゼロから考えず、依頼・資料・確認手順のどこを直すかを残します。',
    learningPoint: '失敗は、原因と直し方を残したときに初めて次回の品質を上げる教材になります。',
    options: makeOptions([
      '失敗しても、次の会話では同じ頼み方に戻ることが多い',
      '一度だけ、指示や資料を直して再試行した',
      '誤りの理由と修正を記録し、同じ仕事で再利用している',
      '改善履歴をレビューし、チームや他の仕事にも展開している',
    ]),
  }),
  Object.freeze({
    id: 'Q07',
    dimensionId: 'safety',
    prompt: '顧客・利用者・社内の情報をAIに入れる前に、入力してよい情報と許可が必要な操作を分けていますか？',
    context: '個人情報、未公開情報、送信・公開・購入などは、便利さより先に扱いを決めます。',
    learningPoint: '安全は止めるためのルールではなく、安心してAIを使い続けるための土台です。',
    options: makeOptions([
      '入力してよい情報や操作の範囲を決めていない',
      '個人情報を避けるなど、基本の注意を一度試した',
      '入力禁止情報と許可が必要な操作を手順に書いている',
      '権限を最小にし、関係者と確認して安全な運用を改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q08',
    dimensionId: 'safety',
    prompt: 'まず小さな範囲で試し、止める・戻す・相談する条件を決めてから広げていますか？',
    context: '本番にいきなり広げず、影響の小さい題材で確認し、困ったときの戻り方も決めます。',
    learningPoint: '小さく試して戻せることは、挑戦を遅くするのでなく、失敗を恐れず前に進める方法です。',
    options: makeOptions([
      '試す範囲や止める条件を決めずに、いきなり使うことがある',
      '影響の小さい題材で、一度試して止めたことがある',
      '確認者、停止条件、戻す方法を決めてから実行している',
      '安全な演習と振り返りを行い、復旧手順を更新している',
    ]),
  }),
  Object.freeze({
    id: 'Q09',
    dimensionId: 'improvement',
    prompt: 'うまくいった依頼・確認手順・成果物を、次回も使える形で残していますか？',
    context: '会話の中だけで終わらせず、フォルダ、テンプレート、チェックリストなどに残します。',
    learningPoint: 'AI活用の差は、一度の成功より「次の自分や仲間が再利用できる形」に残せるかで広がります。',
    options: makeOptions([
      'うまくいった方法が会話や記憶の中だけに残っている',
      '成果物や依頼文を一度保存して、次回に使った',
      'テンプレートと確認手順を整え、繰り返し使っている',
      '他の人も使える形にし、利用結果からテンプレートを改善している',
    ]),
  }),
  Object.freeze({
    id: 'Q10',
    dimensionId: 'improvement',
    prompt: '月に一度、時間・品質・手戻りを振り返り、次に直す一点を決めていますか？',
    context: '全部を変えようとせず、「次は確認漏れを減らす」など一つだけ改善します。',
    learningPoint: 'AIの使い方は、一回で完成させず、小さく振り返って直し続けるほど仕事の自由度を増やせます。',
    options: makeOptions([
      '使いっぱなしで、時間や品質の変化を振り返っていない',
      '一度だけ、良かった点や困った点を振り返った',
      '時間・品質・手戻りのどれかを見て、次の改善を決めている',
      '定期レビューを続け、仕事やチームの型を更新している',
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
    const answerPoints = group.questionIds.reduce((total, questionId) => total + answers[questionId], 0);
    const maxAnswerPoints = group.questionIds.length * MAX_ANSWER_SCORE;
    const points = answerPoints * SCORE_MULTIPLIER;
    const maxPoints = maxAnswerPoints * SCORE_MULTIPLIER;
    return {
      ...group,
      name: group.nameJa,
      score: points,
      maxScore: maxPoints,
      points,
      maxPoints,
      percent: Math.round((answerPoints / maxAnswerPoints) * 100),
    };
  });
}

function assessmentGate(dimensionScores, unrestrictedLevel) {
  const byId = Object.fromEntries(dimensionScores.map((dimension) => [dimension.id, dimension]));
  let maxLevel = 5;
  const reasons = [];
  const priorityDimensionIds = new Set();

  if (byId.verification.percent < 50 || byId.safety.percent < 50) {
    maxLevel = 3;
    reasons.push('検証または安全の実践が50%未満のため、まず人の確認と権限管理を整えます。');
    if (byId.verification.percent < 50) priorityDimensionIds.add('verification');
    if (byId.safety.percent < 50) priorityDimensionIds.add('safety');
  }
  if (byId.improvement.percent < 60) {
    maxLevel = Math.min(maxLevel, 4);
    reasons.push('残して続ける力が60%未満のため、成果物・確認手順・振り返りを先に型にします。');
    priorityDimensionIds.add('improvement');
  }
  if (unrestrictedLevel.id === 5) {
    const belowOrchestratorThreshold = dimensionScores.filter(({ percent }) => percent < 60);
    if (belowOrchestratorThreshold.length > 0) {
      maxLevel = Math.min(maxLevel, 4);
      const dimensionNames = belowOrchestratorThreshold.map(({ nameJa }) => nameJa).join('・');
      reasons.push(`Level 5は全5領域60%以上が目安です。${dimensionNames}を先に整えます。`);
      belowOrchestratorThreshold.forEach(({ id }) => priorityDimensionIds.add(id));
    }
  }

  const applied = unrestrictedLevel.id > maxLevel;
  const requirementsMet = reasons.length === 0;
  return {
    applied,
    requirementsMet,
    maxLevel,
    reasons,
    priorityDimensionIds: [...priorityDimensionIds],
    message: reasons.join(' '),
  };
}

function makeConsultationData({ rawScore, level, gate, next90DayTarget, course }) {
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
  const rawScore = Object.values(validAnswers).reduce((total, value) => total + value, 0) * SCORE_MULTIPLIER;
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
      priorityDimensions: [],
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
  const priorityDimensions = rankedDimensions.filter(({ id }) => gate.priorityDimensionIds.includes(id));
  const nextDimension = priorityDimensions[0] ?? lowestDimension;
  const tiedPriorityDimensions = priorityDimensions.filter(({ percent }) => percent === nextDimension.percent);
  const selectionNote = priorityDimensions.length > 0
    ? `安全ゲート・必須基準の未達のため、「${nextDimension.nameJa}」を最優先に表示しています。対象: ${priorityDimensions.map(({ nameJa }) => nameJa).join('・')}${tiedPriorityDimensions.length > 1 ? `。同率: ${tiedPriorityDimensions.map(({ nameJa }) => nameJa).join('・')}` : ''}`
    : lowestDimensions.length > 1
    ? `最下位が同率のため、学習の土台となる「${lowestDimension.nameJa}」を先に表示しています。同率: ${lowestDimensions.map(({ nameJa }) => nameJa).join('・')}`
    : '';
  const next90DayTarget = nextDimension.percent === 100
    ? {
      dimensionId: 'capstone',
      dimensionName: '全5領域',
      title: '100点を維持・証明する90日',
      action: '小さなAI業務を一つ、目的・確認・権限・成果物・改善履歴までそろえて、他者へ引き継げる形にする。',
      measure: '第三者レビューと安全な復旧演習を一回行い、改善履歴を残す。',
      selectionNote: '全領域が満点のため、次は自己申告を成果物と第三者レビューで確かめます。',
    }
    : {
      dimensionId: nextDimension.id,
      dimensionName: nextDimension.nameJa,
      title: `${nextDimension.nameJa}を90日で一段上げる`,
      action: nextDimension.nextAction,
      measure: nextDimension.measure,
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
    priorityDimensions,
    next90DayTarget,
    ninetyDayTarget,
    consultationData,
    consultationMemo: consultationData.text,
  };
}
