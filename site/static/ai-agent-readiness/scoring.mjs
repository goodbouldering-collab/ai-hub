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
    description: 'AIが作ったコードを読み、直し、確認して安全に公開する力を磨きます。',
    summary: 'AIが作ったコードを読み、直し、確認して安全に公開する力を磨きます。',
    cta: 'AIコーディング講習を予約する',
    url: 'https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH',
  }),
  'ai-support': Object.freeze({
    id: 'ai-support',
    name: 'AI伴走支援',
    title: 'AI伴走支援を相談する',
    price: '月額88,000円',
    duration: '6ヶ月',
    description: '組織がAIアプリサイトを自作・改善・運用できるまで学ぶ6ヶ月。',
    summary: '組織がAIアプリサイトを自作・改善・運用できるまで学ぶ6ヶ月。',
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

export const ADDON_SOURCE = Object.freeze({
  title: 'エンジニアなら、これくらいAI使えないとね。',
  url: 'https://www.youtube.com/watch?v=92n-hUhRE58',
  checkedAt: '2026-08-21',
  note: '動画の自動生成字幕から、製品名や金額ではなく実務行動の論点だけを再編集しています。',
});

const freezeAddonQuestion = (question) => Object.freeze({
  ...question,
  title: question.prompt,
  scenario: question.context,
  options: Object.freeze(question.options.map((option) => Object.freeze({ ...option }))),
  recommendedCourseIds: Object.freeze([...question.recommendedCourseIds]),
});

const ADDON_QUESTION_DEFINITIONS = Object.freeze({
  V01: freezeAddonQuestion({
    id: 'V01',
    axis: 'usageDepth',
    prompt: 'AIはブラウザで答えを聞くだけですか。それとも資料・ファイル・道具を渡して、一連の仕事を任せていますか？',
    context: '会話の回数ではなく、下書き、作業、確認、成果物まで実際の仕事がどう変わったかを見ます。',
    options: makeOptions([
      '質問や文章作成が中心で、成果物へは自分でコピペしている',
      '資料やファイルを渡し、一つの作業を任せたことがある',
      '複数の作業を任せ、途中と最後を自分で確認している',
      '人・AI・道具の役割を決め、再現できる仕事の流れとして改善している',
    ]),
    nextAction: '今週一つの仕事を選び、資料を渡す、成果物を作る、人が確認する、の3段階で試す。',
    recommendedCourseIds: ['ai-agent-course', 'ai-consult-entry'],
  }),
  V02: freezeAddonQuestion({
    id: 'V02',
    axis: 'enablement',
    prompt: '使いたいAIが社内規定や端末制限で使えないとき、許可された範囲と代替手段を整理していますか？',
    context: '使えないことを個人の努力不足にせず、利用できる製品、入力できる情報、申請先、代替手順を確認します。',
    options: makeOptions([
      '制約が分からず、使わないか個人判断で使っている',
      '使える製品や情報の範囲を一度確認した',
      '申請、代替手段、確認者を決めて繰り返し運用している',
      '利用状況と事故のない実績を見ながら、関係者と許可範囲を改善している',
    ]),
    nextAction: '利用できるAI、入力禁止情報、許可が必要な操作、相談先を一枚に整理する。',
    recommendedCourseIds: ['ai-consult-entry', 'ai-support'],
  }),
  V03: freezeAddonQuestion({
    id: 'V03',
    axis: 'enablement',
    prompt: '新しいAIツールを配る前に、対象者が価値を体験できる研修や小さな課題を用意していますか？',
    context: '道具だけを渡すのでなく、日常の困りごとを一つ軽くする体験から始めます。',
    options: makeOptions([
      'ツールを案内しただけで、使い方や題材は各自に任せている',
      '基本操作の説明や小さな体験会を一度行った',
      '職種別の課題と確認方法を用意し、受講後も使えるようにしている',
      '成果物と利用状況を見て研修内容や支援方法を定期的に改善している',
    ]),
    nextAction: '一つの職種と一つの仕事に絞り、30分で成果物を作る体験課題を用意する。',
    recommendedCourseIds: ['ai-agent-course', 'ai-support'],
  }),
  V04: freezeAddonQuestion({
    id: 'V04',
    axis: 'safety',
    prompt: '個人情報・秘密情報・公開操作を、入力禁止だけでなく権限、確認、停止、復旧まで含めて管理していますか？',
    context: 'クラウドかローカルかだけで決めず、何を誰がどこまで扱い、問題時にどう止めて戻すかを見ます。',
    options: makeOptions([
      '入力や操作の範囲を決めていない',
      '個人情報を避けるなど、基本の注意を一度試した',
      '権限、確認者、停止条件、戻し方を手順にしている',
      '安全な演習とレビューを行い、権限と復旧手順を改善している',
    ]),
    nextAction: '一つの業務で、入力禁止情報、許可操作、確認者、停止と復旧を決める。',
    recommendedCourseIds: ['ai-consult-entry', 'ai-support'],
  }),
  V05: freezeAddonQuestion({
    id: 'V05',
    axis: 'value',
    prompt: 'AI利用料と人の確認時間に対して、短縮時間・品質・売上・利用者価値のどれが増えたか説明できますか？',
    context: '動画内の個別の金額ではなく、自分の業務で費用と成果を同じ期間で比べられるかを見ます。',
    options: makeOptions([
      '利用料だけを見ており、成果を測っていない',
      '一つの仕事で、時間か品質の変化を一度記録した',
      '利用料と確認時間を含め、毎月同じ指標で比較している',
      '成果とリスクをレビューし、予算上限や使う仕事を継続的に見直している',
    ]),
    nextAction: '一業務について、月額費用、確認時間、短縮時間、品質の変化を一か月だけ記録する。',
    recommendedCourseIds: ['ai-consult-entry', 'ai-support'],
  }),
  V06: freezeAddonQuestion({
    id: 'V06',
    axis: 'value',
    prompt: 'AIで空いた時間を、顧客対応・教育・企画・地域活動など何へ振り向けるか決めていますか？',
    context: '作業を速くするだけで終わらず、人の自由度や利用者への価値が増えたかを見ます。',
    options: makeOptions([
      '短縮した時間を何に使うか決めていない',
      '空いた時間で増やしたい活動を一つ決めた',
      '実際に時間を振り向け、利用者や仕事への効果を記録している',
      'チームで時間の使い道を共有し、成果と負担を見ながら配分を改善している',
    ]),
    nextAction: '減らしたい作業と、その後に10分増やしたい活動を一組で書く。',
    recommendedCourseIds: ['ai-consult-entry', 'ai-agent-course'],
  }),
  V07: freezeAddonQuestion({
    id: 'V07',
    axis: 'knowledge',
    prompt: 'プロジェクト固有の目的、禁止事項、完成条件、失敗から得た学びを、次回も使える形で残していますか？',
    context: '毎回長く説明するのでなく、AIと人が必要な情報へたどり着ける場所を整えます。',
    options: makeOptions([
      '会話や担当者の記憶に頼り、毎回説明し直している',
      '目的や注意点を一つの文書に残したことがある',
      '目的、制約、完成条件、確認手順を必要最小限で更新している',
      '人とAIのフィードバックを承認して取り込み、他の仕事にも再利用している',
    ]),
    nextAction: '一つのプロジェクトに、目的、禁止事項、完成条件、確認方法を15行以内で残す。',
    recommendedCourseIds: ['ai-agent-course', 'ai-coding'],
  }),
  V08: freezeAddonQuestion({
    id: 'V08',
    axis: 'knowledge',
    prompt: '過去の指示やルールが、新しいAIの力を必要以上に縛っていないか定期的に見直していますか？',
    context: 'ルールを全部消すのでなく、必須の境界と古くなった手順を分けます。',
    options: makeOptions([
      '一度作った指示やルールを見直していない',
      '不要な指示を一度外したり短くしたりした',
      'モデルや仕事が変わるとき、必須ルールと手順を分けて見直している',
      '変更前後の成果と事故の有無を比べ、最小限のルールへ継続改善している',
    ]),
    nextAction: '古い指示を、守る境界、作業手順、参考情報に分け、不要な重複を一つ外す。',
    recommendedCourseIds: ['ai-coding', 'ai-support'],
  }),
  V09: freezeAddonQuestion({
    id: 'V09',
    axis: 'knowledge',
    prompt: 'SNSや動画で見た新しいAI活用法を、出典・自分の仕事との適合・小さな検証で確かめてから取り入れていますか？',
    context: '話題だから全部採用するのでなく、公式情報、必要性、安全な試行で選別します。',
    options: makeOptions([
      '話題になった方法を、そのまま試したりルールへ追加したりする',
      '出典か公式情報を一度確認した',
      '自分の仕事への必要性を考え、安全な範囲で比較している',
      '採用・不採用の理由と結果を残し、チームの判断基準を改善している',
    ]),
    nextAction: '気になる手法を一つ選び、公式情報、期待する効果、試す範囲、採用条件を書く。',
    recommendedCourseIds: ['ai-agent-course', 'ai-coding'],
  }),
  V10: freezeAddonQuestion({
    id: 'V10',
    axis: 'verification',
    prompt: 'AIに設計や実装を任せる範囲をリスクで分け、必要なところへ人や専門家のレビューを置いていますか？',
    context: '文章の下書き、業務ロジック、個人情報、課金、インフラでは、失敗したときの影響が違います。',
    options: makeOptions([
      'リスクを分けず、同じ確認方法で任せている',
      '重要な変更だけ、自分か詳しい人が一度確認した',
      '影響度ごとに承認者、テスト、公開条件を決めている',
      '失敗事例とレビュー結果から、委任範囲と確認基準を改善している',
    ]),
    nextAction: '一つの変更を低・中・高リスクに分け、それぞれの確認者と公開条件を決める。',
    recommendedCourseIds: ['ai-coding', 'ai-support'],
  }),
  V11: freezeAddonQuestion({
    id: 'V11',
    axis: 'verification',
    prompt: 'AIに成果物を作らせる前に利用者の流れを決め、テストと実画面で通ることを確かめていますか？',
    context: 'コード量ではなく、利用者が目的を達成でき、壊れたときに気づける確認を用意します。',
    options: makeOptions([
      '生成された成果物を目で少し見るだけで使っている',
      '主な操作を自分で一度試した',
      '利用者シナリオ、単体テスト、主要画面の確認を毎回行っている',
      '失敗を再現するテストを残し、PC・スマホ・本番まで自動と人で継続確認している',
    ]),
    nextAction: '利用者が行う三つの操作を書き、一つを自動テスト、一つをブラウザで確認する。',
    recommendedCourseIds: ['ai-coding'],
  }),
  V12: freezeAddonQuestion({
    id: 'V12',
    axis: 'humanJudgment',
    prompt: '要約・文章・返信をAIへ任せても、自分で説明する、異論を出す、たとえる、相手と直接話す力を残していますか？',
    context: 'AIを使わないことが目的ではなく、人にしか担えない判断と関係づくりを意識して使います。',
    options: makeOptions([
      '内容を十分理解せず、AIの要約や返信をそのまま使うことがある',
      '送る前に読み、自分の言葉を一つ加えたことがある',
      '理由、異論、相手への配慮を自分で確認し、必要な場面は直接話している',
      'AI利用後も説明力と対話の質を振り返り、任せる範囲を改善している',
    ]),
    nextAction: '次のAI生成文に、自分の判断理由か相手への一言を必ず一つ加える。',
    recommendedCourseIds: ['ai-agent-course', 'ai-consult-entry'],
  }),
});

const makeAddonTrack = ({ questionIds, ...track }) => Object.freeze({
  ...track,
  questionIds: Object.freeze([...questionIds]),
  questions: Object.freeze(questionIds.map((questionId) => ADDON_QUESTION_DEFINITIONS[questionId])),
});

export const ADDON_TRACKS = Object.freeze({
  implementation: makeAddonTrack({
    id: 'implementation',
    title: '実装編 6問',
    eyebrow: '作る・任せる・確かめる',
    description: 'コピペ利用から一歩進み、文脈、ルール、レビュー、テスト、実画面確認までを振り返ります。',
    questionIds: ['V01', 'V07', 'V08', 'V09', 'V10', 'V11'],
  }),
  organization: makeAddonTrack({
    id: 'organization',
    title: '組織導入編 6問',
    eyebrow: '安全に導入し、価値へつなげる',
    description: '利用制約、研修、安全、費用対効果、空いた時間、人の対話を振り返ります。',
    questionIds: ['V02', 'V03', 'V04', 'V05', 'V06', 'V12'],
  }),
});

export const ADDON_BANDS = Object.freeze([
  Object.freeze({
    id: 'start',
    min: 0,
    max: 39,
    title: 'まず一つ試す',
    description: '広げる前に、影響の小さい仕事を一つ選び、AIへ任せる範囲と人が確認する点を決める段階です。',
  }),
  Object.freeze({
    id: 'shape',
    min: 40,
    max: 69,
    title: '仕事の型を整える',
    description: '一度の成功を、目的・材料・確認・記録まで含む再現できる手順へ整える段階です。',
  }),
  Object.freeze({
    id: 'verify',
    min: 70,
    max: 89,
    title: '任せて確かめる',
    description: '任せる範囲を広げながら、品質、安全、利用者の流れを人とテストで確かめる段階です。',
  }),
  Object.freeze({
    id: 'improve',
    min: 90,
    max: 100,
    title: '広げながら改善する',
    description: '成果とリスクを定期的に振り返り、他の仕事や人にも安全に広げる段階です。',
  }),
]);

const ALLOWED_SCORES = new Set([0, 2, 4, 5]);

export function addonBandForPercent(percent) {
  const numericPercent = Number.isFinite(Number(percent)) ? Number(percent) : 0;
  const boundedPercent = Math.max(0, Math.min(100, numericPercent));
  return ADDON_BANDS.find((band) => boundedPercent >= band.min && boundedPercent <= band.max) ?? ADDON_BANDS[0];
}

export function scoreAddonTrack(trackId, answers = {}) {
  const track = ADDON_TRACKS[trackId];
  if (!track) {
    throw new TypeError(`Unknown add-on track: ${trackId}`);
  }

  const validAnswers = {};
  const missingQuestionIds = [];
  for (const question of track.questions) {
    const answer = Number(answers[question.id]);
    if (!ALLOWED_SCORES.has(answer) || answers[question.id] === '' || answers[question.id] == null) {
      missingQuestionIds.push(question.id);
      continue;
    }
    validAnswers[question.id] = answer;
  }

  const rawScore = Object.values(validAnswers).reduce((total, score) => total + score, 0);
  const maxScore = track.questions.length * MAX_ANSWER_SCORE;
  const answeredCount = track.questions.length - missingQuestionIds.length;
  if (missingQuestionIds.length > 0) {
    return {
      complete: false,
      track,
      answeredCount,
      totalQuestions: track.questions.length,
      missingQuestionIds,
      rawScore,
      maxScore,
      percent: Math.round((rawScore / maxScore) * 100),
      band: null,
      lowestQuestions: [],
      nextActions: [],
      recommendedCourses: [],
    };
  }

  const percent = Math.round((rawScore / maxScore) * 100);
  const rankedQuestions = track.questions
    .map((question, index) => ({ ...question, answer: validAnswers[question.id], trackIndex: index }))
    .sort((left, right) => left.answer - right.answer || left.trackIndex - right.trackIndex);
  const lowestQuestions = rankedQuestions.slice(0, 2);
  const nextActions = lowestQuestions.map(({ id, prompt, nextAction }) => ({ id, prompt, nextAction }));
  const recommendedCourseIds = [...new Set(lowestQuestions.flatMap(({ recommendedCourseIds: ids }) => ids))].slice(0, 2);
  const recommendedCourses = recommendedCourseIds.map((courseId) => COURSE_ROUTES[courseId]);

  return {
    complete: true,
    track,
    answeredCount,
    totalQuestions: track.questions.length,
    missingQuestionIds,
    rawScore,
    maxScore,
    percent,
    band: addonBandForPercent(percent),
    lowestQuestions,
    nextActions,
    recommendedCourses,
  };
}

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
