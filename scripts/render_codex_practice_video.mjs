import fs from "node:fs";
import path from "node:path";
import Module from "node:module";

const ROOT = process.cwd();
const depsRoot =
  "C:/Users/yui/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const pnpmModules = path.join(depsRoot, ".pnpm", "node_modules");
process.env.NODE_PATH = [pnpmModules, process.env.NODE_PATH].filter(Boolean).join(path.delimiter);
Module._initPaths();

const require = Module.createRequire(import.meta.url);
const { chromium } = require(path.join(depsRoot, "playwright"));

const outDir = path.join(ROOT, "content", "lectures", "assets");
const mode = process.argv[2] || "practice";

const practiceSlides = [
  {
    kicker: "01 / WORKSPACE",
    title: "導入の次は仕事場づくり",
    body: "Codexは単発の相談先ではなく、プロジェクト、履歴、差分、設定、連携を持つ作業場です。",
    bullets: ["Projectで範囲を分ける", "Threadで目的を分ける", "設定と手順をファイルに残す"],
    accent: "#2563eb",
  },
  {
    kicker: "02 / MODES",
    title: "Local / Worktree / Cloud",
    body: "どこで動かすかで、安全性と速度が変わります。",
    bullets: ["Local: 手元フォルダを直接編集", "Worktree: Gitの別作業場で並行作業", "Cloud: 設定済み環境でリモート実行"],
    accent: "#0f8b8d",
  },
  {
    kicker: "03 / FOLDERS",
    title: "見せるものと守るものを分ける",
    body: "Codexに渡すフォルダは、資料、作業ログ、成果物、秘密情報を分離して設計します。",
    bullets: ["contentは教材", "outputsは生成物", ".envは絶対に渡さない"],
    accent: "#e85d5a",
  },
  {
    kicker: "04 / RULES",
    title: "AGENTS.mdを運用ルールにする",
    body: "毎回の説明を減らすため、ビルド、確認、触ってよい範囲、公開条件をAGENTS.mdへ置きます。",
    bullets: ["守るべきルール", "確認コマンド", "公開前のチェック"],
    accent: "#2f9d58",
  },
  {
    kicker: "05 / SETTINGS",
    title: ".codex/config.tomlで既定値を決める",
    body: "model、sandbox、approval、MCP、feature flagsをプロジェクトやユーザー単位で管理します。",
    bullets: ["workspace-write", "on-request", "web_search / memories / hooks"],
    accent: "#f2b705",
  },
  {
    kicker: "06 / SKILLS",
    title: "skillsは繰り返し作業の手順書",
    body: "作業の型をSKILL.mdにして、必要な時だけ読み込ませます。",
    bullets: ["progressive disclosure", "explicit trigger", "implicit trigger"],
    accent: "#7c3aed",
  },
  {
    kicker: "07 / PLUGINS",
    title: "pluginsは道具箱",
    body: "skills、apps、MCP serversをまとめて、Figma、Drive、GitHub、Canvaなどと接続します。",
    bullets: ["Plugin Directory", "role-specific plugins", "MCP連携"],
    accent: "#0891b2",
  },
  {
    kicker: "08 / GUARDS",
    title: "hooksとrulesで止める",
    body: "自動チェックと許可ルールを分け、危険なコマンドや公開前の抜け漏れを止めます。",
    bullets: ["PreToolUse", "PostToolUse", "Stop / Notification"],
    accent: "#dc2626",
  },
  {
    kicker: "09 / AUTOMATIONS",
    title: "automationsで定期作業を任せる",
    body: "毎朝のbrief、PR確認、週次レポート、サイト監視をCodexに戻します。",
    bullets: ["Triage", "standalone", "project / thread automation"],
    accent: "#0d9488",
  },
  {
    kicker: "10 / HIDDEN FEATURES",
    title: "隠れ機能で速度を上げる",
    body: "Command menu、slash commands、deep links、pets、memories、appshotsを使う場面まで覚えます。",
    bullets: ["/plan /goal /review", "codex://settings", "Appshots / Memories"],
    accent: "#ea580c",
  },
  {
    kicker: "11 / OFFICIAL UPDATES",
    title: "公式更新先を固定する",
    body: "新機能はXで速報、Changelogで仕様、Feature Maturityで本番判断を確認します。",
    bullets: ["@OpenAI / @OpenAIDevs", "Codex Changelog", "Feature Maturity / GitHub releases"],
    accent: "#1d4ed8",
  },
  {
    kicker: "12 / OUTCOME",
    title: "最終形は運用できる作業場",
    body: "導入で終わらず、プロジェクト、設定、手順、自動化、確認先まで整えます。",
    bullets: ["小さく依頼", "差分を見る", "公開して検証する"],
    accent: "#111827",
  },
];

const prepSlides = [
  {
    kicker: "01 / START",
    title: "Codex準備は入口を整える",
    body: "最初の目的は、ログイン、作業場所、依頼の小ささ、差分確認を迷わず進める状態にすることです。",
    bullets: ["ChatGPTでサインイン", "Projectを選ぶ", "最初は小さく頼む"],
    accent: "#2563eb",
  },
  {
    kicker: "02 / WORKSPACE",
    title: "会話ではなく作業場",
    body: "ChatGPTは相談相手。Codexはフォルダを読み、編集し、確認まで進める共同作業者です。",
    bullets: ["ファイルを読む", "変更を提案する", "結果を確認する"],
    accent: "#0f8b8d",
  },
  {
    kicker: "03 / SIGN IN",
    title: "最初はChatGPTでログイン",
    body: "公式手順どおり、Codexを開き、ChatGPTアカウントでサインインして作業を始めます。",
    bullets: ["Codexを開く", "ChatGPTでサインイン", "プロジェクトを選ぶ"],
    accent: "#2f9d58",
  },
  {
    kicker: "04 / SCOPE",
    title: "触る場所を先に限定する",
    body: "安全装置の第一歩は、Codexに見せるフォルダやGitリポジトリを明確にすることです。",
    bullets: ["作業用フォルダを1つ選ぶ", "秘密情報を混ぜない", "最初は空フォルダでもよい"],
    accent: "#e85d5a",
  },
  {
    kicker: "05 / PROMPT",
    title: "最初の依頼は小さく",
    body: "いきなり全体改修を任せず、1ファイル、1画面、1文章から始めます。",
    bullets: ["まず説明してもらう", "候補を3つ出してもらう", "変更前に確認する"],
    accent: "#f2b705",
  },
  {
    kicker: "06 / DIFF",
    title: "差分を見て採用する",
    body: "Codexの成果は、言葉ではなく変更差分とブラウザ表示で確認します。",
    bullets: ["変更ファイルを見る", "ブラウザで確認する", "戻せる状態を保つ"],
    accent: "#7c3aed",
  },
  {
    kicker: "07 / REVIEW",
    title: "公開前は独立レビュー",
    body: "作った直後は見落としが出ます。別視点で壊れそうな点を先に出します。",
    bullets: ["表示崩れ", "リンク切れ", "秘密情報の混入"],
    accent: "#dc2626",
  },
  {
    kicker: "08 / AGENTS",
    title: "AGENTS.mdにルールを残す",
    body: "毎回言いたくないルールは、プロジェクトのAGENTS.mdに置きます。",
    bullets: ["触ってよい範囲", "確認コマンド", "公開前条件"],
    accent: "#0891b2",
  },
  {
    kicker: "09 / OFFICIAL",
    title: "公式アップデートを追う",
    body: "Codexは更新が速いので、X、OpenAI News、Changelog、GitHub releasesを確認先にします。",
    bullets: ["@OpenAI / @OpenAIDevs", "Codex Changelog", "Feature Maturity"],
    accent: "#1d4ed8",
  },
  {
    kicker: "10 / NEXT",
    title: "準備の次は実践へ",
    body: "準備編のゴールは導入完了ではなく、小さな成果物を作り、次の運用ルールを決めることです。",
    bullets: ["1ページを直す", "1資料を整理する", "実践編で作業場を育てる"],
    accent: "#111827",
  },
];

const decks = {
  practice: {
    header: "AIハブ / Codex実践",
    pointLabel: "実務ポイント",
    baseName: "codex-app-practice",
    slides: practiceSlides,
  },
  prep: {
    header: "AIハブ / Codex準備",
    pointLabel: "準備ポイント",
    baseName: "codex-app-onboarding",
    slides: prepSlides,
  },
};

const deck = decks[mode];
if (!deck) {
  throw new Error(`Unknown mode: ${mode}. Use "practice" or "prep".`);
}

const { slides } = deck;
const videoPath = path.join(outDir, `${deck.baseName}.webm`);
const posterPath = path.join(outDir, `${deck.baseName}-poster.png`);

function findChrome() {
  const candidates = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  ];
  return candidates.find((candidate) => fs.existsSync(candidate));
}

const chromePath = findChrome();
if (!chromePath) {
  throw new Error("Chrome or Edge executable was not found.");
}

const browser = await chromium.launch({
  headless: true,
  executablePath: chromePath,
  args: ["--autoplay-policy=no-user-gesture-required", "--use-fake-ui-for-media-stream"],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

const result = await page.evaluate(async ({ slides, header, pointLabel }) => {
  const width = 1280;
  const height = 720;
  const fps = 30;
  const framesPerSlide = 150;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  document.body.append(canvas);
  const ctx = canvas.getContext("2d");

  const font = '"Yu Gothic", "Meiryo", "Hiragino Sans", Arial, sans-serif';

  function roundRect(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function wrapText(text, x, y, maxWidth, lineHeight) {
    let line = "";
    const lines = [];
    for (const char of text) {
      const test = line + char;
      if (ctx.measureText(test).width > maxWidth && line) {
        lines.push(line);
        line = char;
      } else {
        line = test;
      }
    }
    if (line) lines.push(line);
    for (const row of lines) {
      ctx.fillText(row, x, y);
      y += lineHeight;
    }
    return y;
  }

  function draw(slide, slideIndex, frame, totalFrames) {
    const local = (frame % framesPerSlide) / framesPerSlide;
    const progress = frame / totalFrames;
    const ease = 1 - Math.pow(1 - Math.min(local * 1.8, 1), 3);

    const grad = ctx.createLinearGradient(0, 0, width, height);
    grad.addColorStop(0, "#f8fafc");
    grad.addColorStop(0.55, "#ffffff");
    grad.addColorStop(1, "#eef6ff");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, width, 92);
    ctx.fillStyle = slide.accent;
    ctx.fillRect(0, 0, width * progress, 8);

    ctx.globalAlpha = 0.08;
    ctx.fillStyle = slide.accent;
    ctx.beginPath();
    ctx.arc(1110 + Math.sin(frame / 22) * 18, 160, 210, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(108 + Math.cos(frame / 28) * 12, 648, 150, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    ctx.fillStyle = "#e5e7eb";
    ctx.font = `700 20px ${font}`;
    ctx.fillText(header, 64, 58);
    ctx.textAlign = "right";
    ctx.fillText(`${String(slideIndex + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}`, width - 64, 58);
    ctx.textAlign = "left";

    ctx.save();
    ctx.translate(0, (1 - ease) * 26);
    ctx.globalAlpha = Math.max(0.15, ease);

    ctx.fillStyle = slide.accent;
    roundRect(64, 132, 246, 42, 21);
    ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.font = `800 18px ${font}`;
    ctx.fillText(slide.kicker, 86, 160);

    ctx.fillStyle = "#0f172a";
    ctx.font = `900 58px ${font}`;
    const nextY = wrapText(slide.title, 64, 250, 780, 72);

    ctx.fillStyle = "#334155";
    ctx.font = `500 28px ${font}`;
    wrapText(slide.body, 68, nextY + 26, 780, 42);

    const cardX = 840;
    const cardY = 182;
    ctx.fillStyle = "#ffffff";
    ctx.shadowColor = "rgba(15, 23, 42, .16)";
    ctx.shadowBlur = 34;
    ctx.shadowOffsetY = 14;
    roundRect(cardX, cardY, 360, 370, 24);
    ctx.fill();
    ctx.shadowColor = "transparent";

    ctx.fillStyle = "#0f172a";
    ctx.font = `900 28px ${font}`;
    ctx.fillText(pointLabel, cardX + 36, cardY + 62);
    ctx.font = `600 24px ${font}`;
    slide.bullets.forEach((bullet, index) => {
      const y = cardY + 128 + index * 78;
      ctx.fillStyle = slide.accent;
      ctx.beginPath();
      ctx.arc(cardX + 46, y - 8, 12, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#334155";
      wrapText(bullet, cardX + 76, y, 250, 32);
    });

    ctx.restore();

    ctx.fillStyle = "#cbd5e1";
    ctx.font = `700 18px ${font}`;
    ctx.fillText("Official updates: OpenAI / OpenAI Developers / Codex Changelog / Feature Maturity", 64, 674);
  }

  const totalFrames = slides.length * framesPerSlide;
  draw(slides[0], 0, Math.floor(framesPerSlide * 0.45), totalFrames);
  const poster = canvas.toDataURL("image/png").split(",")[1];

  const stream = canvas.captureStream(fps);
  const mime = MediaRecorder.isTypeSupported("video/webm;codecs=vp8")
    ? "video/webm;codecs=vp8"
    : "video/webm";
  const recorder = new MediaRecorder(stream, {
    mimeType: mime,
    videoBitsPerSecond: 1400000,
  });
  const chunks = [];
  recorder.ondataavailable = (event) => {
    if (event.data && event.data.size) chunks.push(event.data);
  };
  recorder.start(500);
  const track = stream.getVideoTracks()[0];

  for (let frame = 0; frame < totalFrames; frame += 1) {
    const slideIndex = Math.min(Math.floor(frame / framesPerSlide), slides.length - 1);
    draw(slides[slideIndex], slideIndex, frame, totalFrames);
    if (track.requestFrame) track.requestFrame();
    await new Promise((resolve) => setTimeout(resolve, 1000 / fps));
  }

  await new Promise((resolve) => setTimeout(resolve, 400));
  recorder.stop();
  await new Promise((resolve) => {
    recorder.onstop = resolve;
  });

  const blob = new Blob(chunks, { type: mime });
  const buffer = await blob.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return { video: btoa(binary), poster };
}, { slides, header: deck.header, pointLabel: deck.pointLabel });

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(videoPath, Buffer.from(result.video, "base64"));
fs.writeFileSync(posterPath, Buffer.from(result.poster, "base64"));
await browser.close();

console.log(`Wrote ${path.relative(ROOT, videoPath)} (${fs.statSync(videoPath).size} bytes)`);
console.log(`Wrote ${path.relative(ROOT, posterPath)} (${fs.statSync(posterPath).size} bytes)`);
