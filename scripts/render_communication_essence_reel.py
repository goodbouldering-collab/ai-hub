from __future__ import annotations

"""Render the 2026-08-14 communication-essence Instagram Reel.

The source artwork is deliberately reused from the accompanying AI相談 blog
article.  That keeps the Reel, the article, and the blog-index feature visually
and editorially consistent while leaving a reproducible campaign asset behind.
"""

import asyncio
import json
import math
import os
import re
import shutil
import subprocess
import wave
from array import array
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "media" / "output" / "myreel" / "2026-08-14-communication-essence"
FRAMES = CAMPAIGN / "frames"
AUDIO = CAMPAIGN / "audio"
SCENES = CAMPAIGN / "scenes"
STATIC_MEDIA = ROOT / "site" / "static" / "media" / "reels"
STATIC_IMG = ROOT / "site" / "static" / "img"

FFMPEG = Path(
    os.environ.get(
        "AI_SODAN_FFMPEG",
        "C:/Project/グッぼる/media/output/myreel/2026-07-03-finger-training-reframe/"
        "pydeps/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe",
    )
)

CANVAS = (1080, 1920)
FPS = 30
VOICE = "ja-JP-NanamiNeural"
FINAL_URL = "https://aiclimb.vercel.app/blog/2026-08-14-communication-essence-ai-consult.html"
FINAL_VIDEO = STATIC_MEDIA / "2026-08-14-communication-essence.mp4"
FINAL_COVER = STATIC_IMG / "reel-communication-essence-cover-20260814.webp"

NAVY = (23, 32, 51)
INK = (19, 43, 61)
BLUE = (74, 99, 199)
TEAL = (45, 126, 136)
SAGE = (122, 177, 157)
CREAM = (247, 243, 234)
WHITE = (255, 255, 255)
MIST = (219, 235, 235)
CORAL = (224, 110, 81)

SCENE_SPECS = [
    {
        "image": "blog-communication-essence-hero-20260814.webp",
        "lines": ["AI時代の", "伝える技術"],
        "voice": "AI時代の、伝える技術。",
        "label": "情報を増やす前に、相手の時間を見る",
        "accent": 1,
    },
    {
        "image": "blog-communication-next-step-20260814.webp",
        "lines": ["情報を増やしても", "人の時間は", "増えない"],
        "voice": "情報を増やしても、人の時間は増えない。",
        "label": "作れる量と、受け取れる量は別です",
        "accent": 2,
    },
    {
        "image": "blog-communication-100-10-1-20260814.webp",
        "lines": ["100を理解し", "10を見せる"],
        "voice": "100を理解し、10を見せる。",
        "label": "深く考えた人が、先に選ぶ",
        "accent": 0,
    },
    {
        "image": "blog-communication-four-step-sequence-20260814.webp",
        "lines": ["最後に残すのは", "次の一歩", "ただ一つ"],
        "voice": "最後に残すのは、次の一歩、ただ一つ。",
        "label": "迷いを減らして、動ける形へ",
        "accent": 1,
    },
    {
        "image": "blog-communication-ai-consult-flow-20260814.webp",
        "lines": ["伝えるとは", "相手の次の一歩を", "軽くすることだ"],
        "voice": "伝えるとは、相手の次の一歩を軽くすることだ。",
        "label": "AI相談｜持ち込む → 一緒に動かす → 手順に残す",
        "accent": 2,
    },
]


def command(
    args: list[str | Path], *, capture: bool = True, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(value) for value in args],
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )


def require_tools() -> None:
    if not FFMPEG.is_file():
        raise FileNotFoundError(f"FFmpeg is not available: {FFMPEG}")


def font(size: int, *, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/NotoSansJP-VF.ttf"),
        Path("C:/Windows/Fonts/YuGothB.ttc") if bold else Path("C:/Windows/Fonts/YuGothM.ttc"),
        Path("C:/Windows/Fonts/meiryob.ttc") if bold else Path("C:/Windows/Fonts/meiryo.ttc"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError("No Japanese font is available for Reel rendering.")


def rounded_image(image: Image.Image, size: tuple[int, int], radius: int) -> Image.Image:
    fitted = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    fitted.putalpha(mask)
    return fitted


def fit_text(draw: ImageDraw.ImageDraw, text: str, preferred: int, max_width: int, *, stroke: int = 0) -> ImageFont.FreeTypeFont:
    for size in range(preferred, 31, -2):
        face = font(size)
        bounds = draw.textbbox((0, 0), text, font=face, stroke_width=stroke)
        if bounds[2] - bounds[0] <= max_width:
            return face
    return font(30)


def draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    *,
    accent: int,
) -> tuple[list[list[int]], int]:
    faces = [fit_text(draw, line, 88 if index == accent else 76, 900, stroke=2) for index, line in enumerate(lines)]
    measurements = []
    for line, face in zip(lines, faces):
        box = draw.textbbox((0, 0), line, font=face, stroke_width=2)
        measurements.append((box[2] - box[0], box[3] - box[1]))
    gap = 28
    total_height = sum(height for _, height in measurements) + gap * (len(lines) - 1)
    y = 1115 - total_height // 2
    boxes: list[list[int]] = []
    for index, (line, face, (width, height)) in enumerate(zip(lines, faces, measurements)):
        x = (CANVAS[0] - width) // 2
        color = TEAL if index == accent else WHITE
        draw.text((x, y), line, font=face, fill=color, stroke_width=2, stroke_fill=NAVY)
        boxes.append([x, y, x + width, y + height])
        y += height + gap
    return boxes, y


def build_frame(spec: dict[str, object], number: int) -> tuple[Image.Image, dict[str, object]]:
    source_path = STATIC_IMG / str(spec["image"])
    if not source_path.is_file():
        raise FileNotFoundError(f"Article illustration not found: {source_path}")
    with Image.open(source_path) as raw:
        source = ImageOps.exif_transpose(raw).convert("RGB")

    background = ImageOps.fit(source, CANVAS, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(28))
    background = ImageEnhance.Brightness(background).enhance(0.36)
    frame = Image.alpha_composite(background.convert("RGBA"), Image.new("RGBA", CANVAS, (*NAVY, 190)))

    glow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((-260, -170, 700, 740), fill=(*TEAL, 64))
    glow_draw.ellipse((590, 1180, 1350, 2040), fill=(*SAGE, 50))
    frame = Image.alpha_composite(frame, glow)
    draw = ImageDraw.Draw(frame)

    draw.rounded_rectangle((66, 112, 448, 174), radius=31, fill=(*CREAM, 244))
    draw.text((96, 126), "AI相談  /  伝える技術", font=font(25), fill=INK)
    draw.text((904, 122), f"{number:02d}", font=font(36), fill=WHITE)

    card_box = (54, 242, 1026, 789)
    shadow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((68, 258, 1040, 805), radius=34, fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(17))
    frame = Image.alpha_composite(frame, shadow)
    frame.alpha_composite(rounded_image(source, (972, 547), 30), (card_box[0], card_box[1]))
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle(card_box, radius=30, outline=(*WHITE, 170), width=3)

    label = str(spec["label"])
    label_face = fit_text(draw, label, 33, 880)
    label_box = draw.textbbox((0, 0), label, font=label_face)
    label_width = label_box[2] - label_box[0]
    label_height = label_box[3] - label_box[1]
    label_y = 847
    draw.rounded_rectangle(
        ((CANVAS[0] - label_width) // 2 - 30, label_y - 19, (CANVAS[0] + label_width) // 2 + 30, label_y + label_height + 22),
        radius=28,
        fill=(*TEAL, 225),
    )
    draw.text(((CANVAS[0] - label_width) // 2, label_y), label, font=label_face, fill=WHITE)

    lines = [str(value) for value in spec["lines"]]
    text_boxes, next_y = draw_centered_lines(draw, lines, accent=int(spec["accent"]))

    progress_y = 1468
    for index in range(len(SCENE_SPECS)):
        fill = TEAL if index < number else (87, 111, 130)
        draw.rounded_rectangle((282 + index * 104, progress_y, 366 + index * 104, progress_y + 12), radius=6, fill=fill)
    draw.line((86, 1543, 994, 1543), fill=(*WHITE, 72), width=2)
    footer = "複雑さは、伝える人が引き受ける"
    footer_face = fit_text(draw, footer, 32, 850)
    footer_box = draw.textbbox((0, 0), footer, font=footer_face)
    draw.text(((CANVAS[0] - (footer_box[2] - footer_box[0])) // 2, 1585), footer, font=footer_face, fill=MIST)
    draw.text((82, 1710), "aiclimb.vercel.app", font=font(24, bold=False), fill=(192, 217, 222))

    left = min(box[0] for box in text_boxes)
    top = min(box[1] for box in text_boxes)
    right = max(box[2] for box in text_boxes)
    bottom = max(box[3] for box in text_boxes)
    return frame.convert("RGB"), {
        "scene": number,
        "centerText": lines,
        "centerTextLineCount": len(lines),
        "voice": str(spec["voice"]),
        "centerTextBox": [left, top, right, bottom],
        "centerTextInSafeArea": left >= 60 and right <= 1020 and top >= 900 and bottom <= 1400,
        "illustrationBox": list(card_box),
        "illustrationInSafeArea": card_box[0] >= 48 and card_box[2] <= 1032 and card_box[1] >= 220 and card_box[3] <= 900,
        "contentEndsAt": next_y,
    }


async def synthesize_voice() -> None:
    for index, spec in enumerate(SCENE_SPECS, start=1):
        voice_file = AUDIO / f"voice-{index:02d}.mp3"
        communicate = edge_tts.Communicate(str(spec["voice"]), voice=VOICE, rate="-8%")
        await communicate.save(str(voice_file))


def probe_duration(path: Path) -> float:
    result = command([FFMPEG, "-hide_banner", "-i", path], check=False)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise RuntimeError(f"Could not read audio duration for {path}: {result.stderr}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def write_concat(paths: list[Path], destination: Path) -> None:
    lines = ["file '" + path.resolve().as_posix().replace("'", "'\\''") + "'" for path in paths]
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_bgm(destination: Path, duration: float) -> None:
    sample_rate = 44_100
    samples = int(math.ceil(duration * sample_rate))
    fade = min(1.4, max(0.4, duration / 8))
    pcm = array("h")
    for index in range(samples):
        t = index / sample_rate
        envelope = min(1.0, t / fade, max(0.0, (duration - t) / fade))
        movement = 0.68 + 0.32 * math.sin(2 * math.pi * 0.055 * t)
        value = (
            math.sin(2 * math.pi * 174.61 * t) * 0.020
            + math.sin(2 * math.pi * 261.63 * t) * 0.012
            + math.sin(2 * math.pi * 392.00 * t) * 0.006
        ) * movement * envelope
        sample = max(-32767, min(32767, int(value * 32767)))
        pcm.append(sample)
        pcm.append(sample)
    with wave.open(str(destination), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())


def make_story(frame: Image.Image, destination: Path) -> None:
    story = frame.convert("RGBA")
    overlay = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # Hide the Reel's own centre caption before adding the Story-specific CTA.
    draw.rounded_rectangle((34, 930, 1046, 1502), radius=44, fill=(*NAVY, 255))
    draw.rounded_rectangle((68, 1062, 1012, 1442), radius=38, fill=(*CREAM, 255))
    story = Image.alpha_composite(story, overlay)
    draw = ImageDraw.Draw(story)
    y = 1116
    for line, face, fill in [
        ("情報を増やすより、", font(59), INK),
        ("相手の次の一歩を軽くする。", font(51), TEAL),
        ("4つの順番を記事で読む", font(36, bold=False), INK),
    ]:
        box = draw.textbbox((0, 0), line, font=face)
        draw.text(((CANVAS[0] - (box[2] - box[0])) // 2, y), line, font=face, fill=fill)
        y += (box[3] - box[1]) + 34
    draw.text((370, 1544), "↓ 詳細はこちら", font=font(35), fill=WHITE)
    story.convert("RGB").save(destination, "PNG", optimize=True)


def make_storyboard(frame_paths: list[Path], destination: Path) -> None:
    board = Image.new("RGB", (1080, 462), NAVY)
    draw = ImageDraw.Draw(board)
    for index, path in enumerate(frame_paths):
        with Image.open(path) as image:
            thumb = image.resize((216, 384), Image.Resampling.LANCZOS)
        board.paste(thumb, (index * 216, 0))
        draw.text((index * 216 + 15, 404), f"{index + 1} / {len(frame_paths)}", font=font(24), fill=WHITE)
    board.save(destination, "PNG", optimize=True)


def validate_video(path: Path) -> dict[str, object]:
    info = command([FFMPEG, "-hide_banner", "-i", path], check=False)
    decoded = command([FFMPEG, "-v", "error", "-i", path, "-f", "null", "-"])
    details = info.stderr
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", details)
    video_match = re.search(
        r"Video:\s*([^,]+).*?\b(\d{2,5})x(\d{2,5}).*?(\d+(?:\.\d+)?)\s*fps",
        details,
        re.S,
    )
    pixel_match = re.search(r"Video:\s*[^,]+,\s*([^, ]+)", details)
    audio_match = re.search(r"Audio:\s*([^,]+)", details)
    if not duration_match or not video_match or not pixel_match:
        raise RuntimeError(f"Could not read generated video metadata: {details}")
    hours, minutes, seconds = duration_match.groups()
    codec, width, height, fps = video_match.groups()
    return {
        "decodeExitCode": decoded.returncode,
        "decodeErrors": decoded.stderr.strip(),
        "size": [int(width), int(height)],
        "fps": float(fps),
        "durationSeconds": round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3),
        "codec": codec.strip().split(" ")[0],
        "pixelFormat": pixel_match.group(1).split("(")[0],
        "audioStreamPresent": audio_match is not None,
        "audioCodec": audio_match.group(1).strip() if audio_match else None,
        "bytes": path.stat().st_size,
    }


def render() -> dict[str, object]:
    require_tools()
    for folder in (CAMPAIGN, FRAMES, AUDIO, SCENES, STATIC_MEDIA, STATIC_IMG):
        folder.mkdir(parents=True, exist_ok=True)

    frame_paths: list[Path] = []
    frame_checks: list[dict[str, object]] = []
    for index, spec in enumerate(SCENE_SPECS, start=1):
        frame, check = build_frame(spec, index)
        frame_path = FRAMES / f"frame-{index:02d}.png"
        frame.save(frame_path, "PNG", optimize=True)
        frame_paths.append(frame_path)
        frame_checks.append(check)

    shutil.copy2(frame_paths[0], CAMPAIGN / "cover.png")
    with Image.open(frame_paths[0]) as cover:
        cover.save(FINAL_COVER, "WEBP", quality=90, method=6)
    with Image.open(frame_paths[-1]) as last_frame:
        make_story(last_frame, CAMPAIGN / "story.png")
    make_storyboard(frame_paths, CAMPAIGN / "storyboard.png")

    asyncio.run(synthesize_voice())
    durations = [max(4.8, probe_duration(AUDIO / f"voice-{index:02d}.mp3") + 1.05) for index in range(1, len(SCENE_SPECS) + 1)]

    scene_paths: list[Path] = []
    audio_paths: list[Path] = []
    for index, duration in enumerate(durations, start=1):
        scene_path = SCENES / f"scene-{index:02d}.mp4"
        command(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-framerate",
                str(FPS),
                "-t",
                f"{duration:.3f}",
                "-i",
                frame_paths[index - 1],
                "-vf",
                "zoompan=z='min(zoom+0.00045,1.06)':d=1:s=1080x1920:fps=30,format=yuv420p",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "19",
                "-pix_fmt",
                "yuv420p",
                scene_path,
            ]
        )
        scene_paths.append(scene_path)
        audio_path = AUDIO / f"segment-{index:02d}.m4a"
        command(
            [
                FFMPEG,
                "-y",
                "-i",
                AUDIO / f"voice-{index:02d}.mp3",
                "-filter:a",
                f"adelay=400|400,apad=whole_dur={duration:.3f}",
                "-t",
                f"{duration:.3f}",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-c:a",
                "aac",
                "-b:a",
                "160k",
                audio_path,
            ]
        )
        audio_paths.append(audio_path)

    video_list = CAMPAIGN / "video-concat.txt"
    audio_list = CAMPAIGN / "audio-concat.txt"
    write_concat(scene_paths, video_list)
    write_concat(audio_paths, audio_list)
    visual = CAMPAIGN / "visual.mp4"
    narration = AUDIO / "narration.m4a"
    command([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", visual])
    command([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", audio_list, "-c", "copy", narration])

    total_duration = sum(durations)
    bgm = AUDIO / "original-soft-pad.wav"
    create_bgm(bgm, total_duration)
    local_final = CAMPAIGN / "reel.mp4"
    command(
        [
            FFMPEG,
            "-y",
            "-i",
            visual,
            "-i",
            narration,
            "-i",
            bgm,
            "-filter_complex",
            "[2:a]volume=0.18[bg];[bg][1:a]sidechaincompress=threshold=0.025:ratio=10:attack=20:release=520[ducked];[ducked][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]",
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            "-shortest",
            local_final,
        ]
    )
    shutil.copy2(local_final, FINAL_VIDEO)

    video_check = validate_video(local_final)
    qa = {
        "campaign": "2026-08-14-communication-essence",
        "articleUrl": FINAL_URL,
        "videoPath": "site/static/media/reels/2026-08-14-communication-essence.mp4",
        "coverPath": "site/static/img/reel-communication-essence-cover-20260814.webp",
        "voice": {"engine": "edge-tts", "voice": VOICE, "rate": "-8%"},
        "bgm": {
            "type": "original self-made soft pad",
            "source": "generated in this script",
            "baseMixVolume": 0.18,
            "ducking": "sidechaincompress threshold=0.025 ratio=10 attack=20 release=520",
        },
        "sceneDurationsSeconds": [round(value, 3) for value in durations],
        "frameChecks": frame_checks,
        "videoCheck": video_check,
        "exactlyFiveCenterTexts": len(frame_checks) == 5,
        "allCenterTextsThreeLinesOrLess": all(check["centerTextLineCount"] <= 3 for check in frame_checks),
        "allCenterTextsInSafeArea": all(check["centerTextInSafeArea"] for check in frame_checks),
        "allIllustrationsInSafeArea": all(check["illustrationInSafeArea"] for check in frame_checks),
        "videoDimensionsPass": video_check["size"] == [1080, 1920],
        "videoDurationPass": 15 <= float(video_check["durationSeconds"]) <= 60,
        "fpsPass": abs(float(video_check["fps"]) - 30) < 0.1,
        "codecPass": video_check["codec"] == "h264",
        "pixelFormatPass": video_check["pixelFormat"] == "yuv420p",
        "audioPresent": bool(video_check["audioStreamPresent"]),
    }
    (CAMPAIGN / "qa-report.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


if __name__ == "__main__":
    result = render()
    print(json.dumps(result, ensure_ascii=False, indent=2))
