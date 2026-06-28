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

const slug = "ai-consult-hikone-20260629";
const outDir = path.join(ROOT, "site", "static", "media", slug);
const audioPath = path.join(outDir, "ai-consult-hikone-narration.wav");
const videoPath = path.join(outDir, "ai-consult-hikone-course.webm");
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

  function drawBackground(slide, t) {
    const grad = ctx.createLinearGradient(0, 0, width, height);
    grad.addColorStop(0, "#F7FBFF");
    grad.addColorStop(0.52, "#FFFFFF");
    grad.addColorStop(1, "#F6F1FF");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    ctx.globalAlpha = 0.12;
    ctx.fillStyle = slide.accent;
    ctx.beginPath();
    ctx.arc(1030 + Math.sin(t * 2.2) * 16, 150, 238, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(150 + Math.cos(t * 1.8) * 18, 640, 170, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    ctx.strokeStyle = "rgba(15, 23, 42, .08)";
    ctx.lineWidth = 1;
    for (let x = 44; x < width; x += 48) {
      ctx.beginPath();
      ctx.moveTo(x, 92);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 124; y < height; y += 48) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  }

  function drawSlide(slide, index, local, globalProgress) {
    const ease = 1 - Math.pow(1 - Math.min(local * 2.2, 1), 3);
    const drift = Math.sin(local * Math.PI) * 10;

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
    ctx.translate(0, (1 - ease) * 28);
    ctx.globalAlpha = Math.max(0.08, ease);

    ctx.fillStyle = slide.accent;
    roundRect(64, 128, 250, 42, 21);
    ctx.fill();
    ctx.fillStyle = "#FFFFFF";
    ctx.font = `900 18px ${mono}`;
    ctx.fillText(slide.kicker, 88, 156);

    ctx.fillStyle = "#071426";
    ctx.font = `900 60px ${font}`;
    let y = wrapText(slide.title, 64, 248, 720, 72);

    ctx.fillStyle = "#334155";
    ctx.font = `600 29px ${font}`;
    y = wrapText(slide.body, 68, y + 24, 760, 42);

    ctx.fillStyle = "rgba(255, 255, 255, .92)";
    ctx.shadowColor = "rgba(15, 23, 42, .14)";
    ctx.shadowBlur = 32;
    ctx.shadowOffsetY = 14;
    roundRect(834, 146 + drift, 366, 424, 28);
    ctx.fill();
    ctx.shadowColor = "transparent";
    ctx.strokeStyle = "rgba(15, 23, 42, .12)";
    ctx.lineWidth = 1.5;
    roundRect(834, 146 + drift, 366, 424, 28);
    ctx.stroke();

    ctx.fillStyle = slide.accent;
    ctx.font = `900 ${slide.stat.length > 8 ? 46 : 64}px ${font}`;
    wrapText(slide.stat, 874, 246 + drift, 286, 62);
    ctx.fillStyle = "#334155";
    ctx.font = `800 22px ${font}`;
    wrapText(slide.statLabel, 876, 320 + drift, 280, 32);

    slide.bullets.forEach((bullet, bulletIndex) => {
      const by = 388 + drift + bulletIndex * 44;
      ctx.fillStyle = slide.accent;
      ctx.beginPath();
      ctx.arc(886, by - 7, 9, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#071426";
      ctx.font = `800 22px ${font}`;
      ctx.fillText(bullet, 910, by);
    });

    ctx.restore();

    ctx.fillStyle = "rgba(7, 20, 38, .72)";
    ctx.font = `800 18px ${font}`;
    ctx.fillText("悩み -> AIの考え方 -> 成果物 -> 発信 -> 次の改善", 64, 674);
  }

  function drawAtTime(seconds, totalDuration) {
    const sceneLength = totalDuration / slides.length;
    const rawIndex = Math.min(Math.floor(seconds / sceneLength), slides.length - 1);
    const sceneStart = rawIndex * sceneLength;
    const local = Math.min(Math.max((seconds - sceneStart) / sceneLength, 0), 1);
    const globalProgress = Math.min(seconds / totalDuration, 1);

    if (local < 0.12 && rawIndex > 0) {
      drawSlide(slides[rawIndex - 1], rawIndex - 1, 0.88, globalProgress);
      ctx.globalAlpha = local / 0.12;
      drawSlide(slides[rawIndex], rawIndex, local, globalProgress);
      ctx.globalAlpha = 1;
    } else {
      drawSlide(slides[rawIndex], rawIndex, local, globalProgress);
    }
  }

  let audio = null;
  let audioContext = null;
  let audioDestination = null;
  let duration = 72;
  if (audioDataUrl) {
    audio = new Audio(audioDataUrl);
    audio.preload = "auto";
    await new Promise((resolve, reject) => {
      audio.onloadedmetadata = resolve;
      audio.onerror = reject;
    });
    duration = Math.max(30, audio.duration + 0.5);
    audioContext = new AudioContext();
    audioDestination = audioContext.createMediaStreamDestination();
    const source = audioContext.createMediaElementSource(audio);
    source.connect(audioDestination);
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
  if (audioDestination) {
    tracks.push(...audioDestination.stream.getAudioTracks());
  }
  const stream = new MediaStream(tracks);
  const mime = MediaRecorder.isTypeSupported("video/webm;codecs=vp8,opus")
    ? "video/webm;codecs=vp8,opus"
    : (MediaRecorder.isTypeSupported("video/webm;codecs=vp8") ? "video/webm;codecs=vp8" : "video/webm");
  const recorder = new MediaRecorder(stream, {
    mimeType: mime,
    videoBitsPerSecond: 1600000,
    audioBitsPerSecond: 96000,
  });
  const chunks = [];
  recorder.ondataavailable = (event) => {
    if (event.data && event.data.size) chunks.push(event.data);
  };

  recorder.start(500);
  const track = canvasStream.getVideoTracks()[0];
  if (audio) {
    await audioContext.resume();
    audio.currentTime = 0;
    await audio.play();
  }

  const totalFrames = Math.ceil(duration * fps);
  for (let frame = 0; frame < totalFrames; frame += 1) {
    drawAtTime(frame / fps, duration);
    if (track.requestFrame) track.requestFrame();
    await new Promise((resolve) => setTimeout(resolve, 1000 / fps));
  }

  if (audio) {
    audio.pause();
  }
  recorder.stop();
  await new Promise((resolve) => {
    recorder.onstop = resolve;
  });
  stream.getTracks().forEach((mediaTrack) => mediaTrack.stop());
  if (audioContext) {
    await audioContext.close();
  }

  const blob = new Blob(chunks, { type: mime });
  const buffer = await blob.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return { video: btoa(binary), poster, sceneImages, duration, mime };
}, { slides, audioDataUrl });

fs.writeFileSync(videoPath, Buffer.from(result.video, "base64"));
fs.writeFileSync(posterPath, Buffer.from(result.poster, "base64"));
result.sceneImages.forEach((image, index) => {
  const filename = `ai-consult-hikone-scene-${String(index + 1).padStart(2, "0")}.png`;
  fs.writeFileSync(path.join(outDir, filename), Buffer.from(image, "base64"));
});

await browser.close();

console.log(`Wrote ${path.relative(ROOT, videoPath)} (${fs.statSync(videoPath).size} bytes)`);
console.log(`Wrote ${path.relative(ROOT, posterPath)} (${fs.statSync(posterPath).size} bytes)`);
console.log(`Wrote ${result.sceneImages.length} scene images`);
console.log(`Duration ${result.duration.toFixed(1)}s, ${result.mime}`);
