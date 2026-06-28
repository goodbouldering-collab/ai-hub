import fs from "node:fs";
import path from "node:path";
import Module from "node:module";
import { spawnSync } from "node:child_process";

const ROOT = process.cwd();
const depsRoot =
  "C:/Users/yui/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const pnpmModules = path.join(depsRoot, ".pnpm", "node_modules");
process.env.NODE_PATH = [pnpmModules, process.env.NODE_PATH].filter(Boolean).join(path.delimiter);
Module._initPaths();

const require = Module.createRequire(import.meta.url);
const { chromium } = require(path.join(depsRoot, "playwright"));

const slug = "ai-consult-hikone-20260629";
const outDir = path.join(ROOT, "site", "static", "media", slug);
const audioPath = path.join(outDir, "ai-consult-hikone-narration.wav");
const audioMp3Path = path.join(outDir, "ai-consult-hikone-narration.mp3");
const videoPath = path.join(outDir, "ai-consult-hikone-course.webm");
const visualVideoPath = path.join(ROOT, "_tmp", slug, "ai-consult-hikone-course-visual.webm");
const posterPath = path.join(outDir, "ai-consult-hikone-poster.png");

const slides = [
  {
    kicker: "01 / WHY",
    title: "AIを、彦根の現場へ",
    body: "AIは知識ではなく、時間を増やし、仕事を前に進めるための実践道具です。",
    bullets: ["地域事業者", "学校・福祉", "個人事業主"],
    stat: "2-6h",
    statLabel: "短時間で考え方を体験",
    accent: "#0EA5A8",
  },
  {
    kicker: "02 / WORLD CLASS",
    title: "世界レベルの道具を知る",
    body: "コーデックス、AIエージェント、画像生成、SNS改善を、彦根の仕事に接続します。",
    bullets: ["調べる", "作る", "直す", "公開する"],
    stat: "Codex",
    statLabel: "チャットから作業へ",
    accent: "#2563EB",
  },
  {
    kicker: "03 / LOOP",
    title: "短時間でAIの考え方を入れる",
    body: "指示、材料、修正、確認、改善。このループを講座中に何度も回します。",
    bullets: ["指示", "確認", "修正", "改善"],
    stat: "Loop",
    statLabel: "聞いて終わらない",
    accent: "#F59E0B",
  },
  {
    kicker: "04 / PRACTICE",
    title: "実践者が教える",
    body: "複数事業を動かすソロプレナー兼エンジニアが、現場で使える形へ翻訳します。",
    bullets: ["9事業運営", "業務アプリ制作", "集客導線改善"],
    stat: "200万-1500万",
    statLabel: "規模相当の制作経験",
    accent: "#E11D48",
  },
  {
    kicker: "05 / OUTPUT",
    title: "成果物が必ず残る",
    body: "SNS投稿、ホームページ改善、業務アプリ、AIエージェントの型を事業ごとに作ります。",
    bullets: ["投稿", "HP改善", "業務アプリ", "AIエージェント"],
    stat: "70+",
    statLabel: "受講者が実践へ",
    accent: "#16A34A",
  },
  {
    kicker: "06 / ACCESS",
    title: "低コストで続ける",
    body: "5,500円から始められ、10回でも55,000円。高額研修の前に、自分の仕事で試せます。",
    bullets: ["1回 5,500円", "10回 55,000円", "個別相談へ接続"],
    stat: "5,500円",
    statLabel: "始めやすい入口",
    accent: "#7C3AED",
  },
];

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

fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(path.dirname(visualVideoPath), { recursive: true });
const audioDataUrl = fs.existsSync(audioPath)
  ? `data:audio/wav;base64,${fs.readFileSync(audioPath).toString("base64")}`
  : "";

const browser = await chromium.launch({
  headless: true,
  executablePath: chromePath,
  args: ["--autoplay-policy=no-user-gesture-required", "--use-fake-ui-for-media-stream"],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

const result = await page.evaluate(async ({ slides, audioDataUrl }) => {
  const width = 1280;
  const height = 720;
  const fps = 30;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  document.body.style.margin = "0";
  document.body.append(canvas);
  const ctx = canvas.getContext("2d");
  const font = '"Yu Gothic", "Yu Gothic UI", "Meiryo", sans-serif';
  const mono = '"Cascadia Mono", "Consolas", monospace';

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
    for (const char of text) {
      const test = line + char;
      if (ctx.measureText(test).width > maxWidth && line) {
        ctx.fillText(line, x, y);
        y += lineHeight;
        line = char;
      } else {
        line = test;
      }
    }
    if (line) {
      ctx.fillText(line, x, y);
      y += lineHeight;
    }
    return y;
  }

  function easeOutCubic(x) {
    return 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);
  }

  function easeInOut(x) {
    x = Math.min(Math.max(x, 0), 1);
    return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  }

  function drawFlowLine(points, progress, color, width = 6) {
    ctx.save();
    ctx.lineWidth = width;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = color;
    ctx.globalAlpha = 0.72;
    ctx.beginPath();
    const maxIndex = Math.max(1, Math.floor((points.length - 1) * progress));
    ctx.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i <= maxIndex; i += 1) {
      ctx.lineTo(points[i][0], points[i][1]);
    }
    const next = points[maxIndex + 1];
    if (next) {
      const prev = points[maxIndex];
      const local = (points.length - 1) * progress - maxIndex;
      ctx.lineTo(prev[0] + (next[0] - prev[0]) * local, prev[1] + (next[1] - prev[1]) * local);
    }
    ctx.stroke();
    ctx.restore();
  }

  function drawBackground(slide, t) {
    const grad = ctx.createLinearGradient(0, 0, width, height);
    grad.addColorStop(0, "#F2FAFF");
    grad.addColorStop(0.48, "#FFFFFF");
    grad.addColorStop(1, "#F7F2FF");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    ctx.globalAlpha = 0.16;
    ctx.fillStyle = slide.accent;
    ctx.beginPath();
    ctx.arc(1020 + Math.sin(t * 0.8) * 34, 158 + Math.cos(t * 0.7) * 18, 252, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(152 + Math.cos(t * 0.9) * 26, 630 + Math.sin(t * 0.65) * 12, 182, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    ctx.strokeStyle = "rgba(15, 23, 42, .075)";
    ctx.lineWidth = 1;
    const gridShift = (t * 18) % 48;
    for (let x = 44 - gridShift; x < width; x += 48) {
      ctx.beginPath();
      ctx.moveTo(x, 92);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 124 + gridShift * 0.45; y < height; y += 48) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    ctx.save();
    ctx.globalAlpha = 0.34;
    ctx.strokeStyle = slide.accent;
    ctx.lineWidth = 2;
    for (let lane = 0; lane < 4; lane += 1) {
      const y = 210 + lane * 92 + Math.sin(t * 1.1 + lane) * 10;
      ctx.beginPath();
      for (let x = -60; x <= width + 80; x += 28) {
        const wave = Math.sin(x * 0.014 + t * 2.2 + lane) * (12 + lane * 3);
        if (x === -60) ctx.moveTo(x, y + wave);
        else ctx.lineTo(x, y + wave);
      }
      ctx.stroke();
    }
    ctx.restore();

    ctx.save();
    ctx.globalAlpha = 0.42;
    ctx.fillStyle = slide.accent;
    for (let i = 0; i < 16; i += 1) {
      const x = 100 + ((i * 173 + t * 28) % 1120);
      const y = 126 + ((i * 97 + Math.sin(t + i) * 34) % 500);
      const r = 2.5 + (i % 4);
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawSlide(slide, index, local, globalProgress) {
    const entrance = easeOutCubic(local * 2.35);
    const steady = Math.sin(local * Math.PI * 2);
    const drift = Math.sin(local * Math.PI) * 18;
    const scenePulse = 0.5 + Math.sin(local * Math.PI * 6) * 0.5;

    drawBackground(slide, globalProgress * 10);

    ctx.fillStyle = "#071426";
    ctx.fillRect(0, 0, width, 86);
    ctx.fillStyle = slide.accent;
    ctx.fillRect(0, 0, width * globalProgress, 8);

    ctx.fillStyle = "#E6F1FF";
    ctx.font = `800 20px ${font}`;
    ctx.fillText("AI相談 彦根 / 実践AI講座", 64, 54);
    ctx.textAlign = "right";
    ctx.font = `800 18px ${mono}`;
    ctx.fillText(`${String(index + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}`, width - 64, 54);
    ctx.textAlign = "left";

    ctx.save();
    ctx.globalAlpha = 0.85;
    drawFlowLine(
      [[68, 650], [224, 628], [388, 656], [548, 620], [716, 650], [882, 614], [1070, 642], [1214, 612]],
      Math.min(1, globalProgress * 1.1),
      slide.accent,
      5,
    );
    const dotX = 68 + Math.min(1, globalProgress * 1.1) * 1146;
    ctx.fillStyle = "#FFFFFF";
    ctx.shadowColor = slide.accent;
    ctx.shadowBlur = 22;
    ctx.beginPath();
    ctx.arc(dotX, 636 + Math.sin(globalProgress * 18) * 14, 9 + scenePulse * 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowColor = "transparent";
    ctx.restore();

    ctx.save();
    ctx.translate((1 - entrance) * -42, (1 - entrance) * 28);
    ctx.globalAlpha = Math.max(0.08, entrance);

    ctx.fillStyle = slide.accent;
    roundRect(64, 126, 250, 42, 21);
    ctx.fill();
    ctx.fillStyle = "#FFFFFF";
    ctx.font = `900 18px ${mono}`;
    ctx.fillText(slide.kicker, 88, 154);

    ctx.fillStyle = "#071426";
    ctx.font = `900 66px ${font}`;
    let y = wrapText(slide.title, 64, 242, 690, 78);

    ctx.fillStyle = "#334155";
    ctx.font = `600 30px ${font}`;
    y = wrapText(slide.body, 68, y + 20, 700, 42);

    const miniY = Math.min(566, y + 26);
    const steps = ["悩み", "材料", "制作", "確認", "公開"];
    steps.forEach((step, stepIndex) => {
      const active = Math.min(1, Math.max(0, local * 5.2 - stepIndex * 0.72));
      const x = 70 + stepIndex * 134;
      ctx.globalAlpha = 0.22 + active * 0.78;
      ctx.fillStyle = active > 0.9 ? slide.accent : "#FFFFFF";
      ctx.strokeStyle = active > 0.9 ? slide.accent : "rgba(7,20,38,.16)";
      ctx.lineWidth = 2;
      roundRect(x, miniY, 104, 44, 22);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = active > 0.9 ? "#FFFFFF" : "#334155";
      ctx.font = `900 20px ${font}`;
      ctx.fillText(step, x + 29, miniY + 29);
      if (stepIndex < steps.length - 1) {
        ctx.strokeStyle = "rgba(7,20,38,.24)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x + 110, miniY + 22);
        ctx.lineTo(x + 128, miniY + 22);
        ctx.stroke();
      }
      ctx.globalAlpha = Math.max(0.08, entrance);
    });

    ctx.restore();

    ctx.save();
    const cardEase = easeOutCubic(local * 1.9 - 0.12);
    ctx.translate((1 - cardEase) * 80, Math.sin(local * Math.PI * 2) * 8);
    ctx.globalAlpha = Math.max(0.1, cardEase);
    ctx.fillStyle = "rgba(255, 255, 255, .92)";
    ctx.shadowColor = "rgba(15, 23, 42, .14)";
    ctx.shadowBlur = 32;
    ctx.shadowOffsetY = 14;
    roundRect(812, 128 + drift, 402, 458, 30);
    ctx.fill();
    ctx.shadowColor = "transparent";
    ctx.strokeStyle = "rgba(15, 23, 42, .12)";
    ctx.lineWidth = 1.5;
    roundRect(812, 128 + drift, 402, 458, 30);
    ctx.stroke();

    ctx.globalAlpha = 0.2 + scenePulse * 0.12;
    ctx.strokeStyle = slide.accent;
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(1012, 246 + drift, 106, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * Math.min(1, local * 1.25));
    ctx.stroke();
    ctx.globalAlpha = Math.max(0.1, cardEase);

    ctx.fillStyle = slide.accent;
    ctx.font = `900 ${slide.stat.length > 8 ? 48 : 70}px ${font}`;
    wrapText(slide.stat, 850, 260 + drift, 330, 68);
    ctx.fillStyle = "#334155";
    ctx.font = `800 23px ${font}`;
    wrapText(slide.statLabel, 854, 338 + drift, 310, 34);

    slide.bullets.forEach((bullet, bulletIndex) => {
      const bulletEase = easeOutCubic(local * 4 - bulletIndex * 0.42);
      const by = 414 + drift + bulletIndex * 44;
      ctx.globalAlpha = Math.max(0, bulletEase);
      ctx.fillStyle = slide.accent;
      ctx.beginPath();
      ctx.arc(864 + (1 - bulletEase) * 20, by - 7, 9, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#071426";
      ctx.font = `800 22px ${font}`;
      ctx.fillText(bullet, 890 + (1 - bulletEase) * 20, by);
    });

    ctx.restore();

    ctx.fillStyle = "rgba(7, 20, 38, .72)";
    ctx.font = `800 18px ${font}`;
    ctx.fillText("悩み -> AIの考え方 -> 成果物 -> 発信 -> 次の改善", 64, 684);
  }

  function drawAtTime(seconds, totalDuration) {
    const sceneLength = totalDuration / slides.length;
    const rawIndex = Math.min(Math.floor(seconds / sceneLength), slides.length - 1);
    const sceneStart = rawIndex * sceneLength;
    const local = Math.min(Math.max((seconds - sceneStart) / sceneLength, 0), 1);
    const globalProgress = Math.min(seconds / totalDuration, 1);

    if (local < 0.16 && rawIndex > 0) {
      drawSlide(slides[rawIndex - 1], rawIndex - 1, 0.88, globalProgress);
      const wipe = easeInOut(local / 0.16);
      ctx.save();
      ctx.beginPath();
      ctx.rect(width * (1 - wipe), 0, width * wipe, height);
      ctx.clip();
      drawSlide(slides[rawIndex], rawIndex, local, globalProgress);
      ctx.restore();
      ctx.save();
      ctx.globalAlpha = 0.85;
      ctx.fillStyle = slides[rawIndex].accent;
      ctx.fillRect(width * (1 - wipe) - 18, 0, 22, height);
      ctx.restore();
    } else {
      drawSlide(slides[rawIndex], rawIndex, local, globalProgress);
    }
  }

  let audio = null;
  let duration = 72;
  if (audioDataUrl) {
    audio = new Audio(audioDataUrl);
    audio.preload = "auto";
    await new Promise((resolve, reject) => {
      audio.onloadedmetadata = resolve;
      audio.onerror = reject;
    });
    duration = Math.max(30, audio.duration + 0.5);
  }

  drawAtTime(duration * 0.16, duration);
  const poster = canvas.toDataURL("image/png").split(",")[1];

  const sceneImages = [];
  for (let i = 0; i < slides.length; i += 1) {
    drawSlide(slides[i], i, 0.5, (i + 0.5) / slides.length);
    sceneImages.push(canvas.toDataURL("image/png").split(",")[1]);
  }

  const canvasStream = canvas.captureStream(fps);
  const tracks = [...canvasStream.getVideoTracks()];
  const stream = new MediaStream(tracks);
  const mime = MediaRecorder.isTypeSupported("video/webm;codecs=vp8")
    ? "video/webm;codecs=vp8"
    : "video/webm";
  const recorder = new MediaRecorder(stream, {
    mimeType: mime,
    videoBitsPerSecond: 3200000,
  });
  const chunks = [];
  recorder.ondataavailable = (event) => {
    if (event.data && event.data.size) chunks.push(event.data);
  };

  recorder.start(500);
  const track = canvasStream.getVideoTracks()[0];

  const totalFrames = Math.ceil(duration * fps);
  for (let frame = 0; frame < totalFrames; frame += 1) {
    drawAtTime(frame / fps, duration);
    if (track.requestFrame) track.requestFrame();
    await new Promise((resolve) => setTimeout(resolve, 1000 / fps));
  }

  recorder.stop();
  await new Promise((resolve) => {
    recorder.onstop = resolve;
  });
  stream.getTracks().forEach((mediaTrack) => mediaTrack.stop());

  const blob = new Blob(chunks, { type: mime });
  const buffer = await blob.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return { video: btoa(binary), poster, sceneImages, duration, mime };
}, { slides, audioDataUrl });

fs.writeFileSync(visualVideoPath, Buffer.from(result.video, "base64"));
fs.writeFileSync(posterPath, Buffer.from(result.poster, "base64"));
result.sceneImages.forEach((image, index) => {
  const filename = `ai-consult-hikone-scene-${String(index + 1).padStart(2, "0")}.png`;
  fs.writeFileSync(path.join(outDir, filename), Buffer.from(image, "base64"));
});

await browser.close();

if (fs.existsSync(audioMp3Path)) {
  const mux = spawnSync("ffmpeg", [
    "-y",
    "-i", visualVideoPath,
    "-i", audioMp3Path,
    "-c:v", "copy",
    "-c:a", "libopus",
    "-b:a", "128k",
    "-shortest",
    videoPath,
  ], { stdio: "inherit" });
  if (mux.status !== 0) {
    throw new Error(`ffmpeg mux failed with exit code ${mux.status}`);
  }
} else {
  fs.copyFileSync(visualVideoPath, videoPath);
}

console.log(`Wrote ${path.relative(ROOT, videoPath)} (${fs.statSync(videoPath).size} bytes)`);
console.log(`Wrote ${path.relative(ROOT, posterPath)} (${fs.statSync(posterPath).size} bytes)`);
console.log(`Wrote ${result.sceneImages.length} scene images`);
console.log(`Duration ${result.duration.toFixed(1)}s, ${result.mime}`);
