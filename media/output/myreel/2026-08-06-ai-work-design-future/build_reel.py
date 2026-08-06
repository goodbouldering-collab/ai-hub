from __future__ import annotations

import asyncio
import html
import json
import math
import re
import shutil
import struct
import subprocess
import wave
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
SOURCE_DIR = ROOT / "source"
FRAME_DIR = ROOT / "frames"
VOICE_DIR = ROOT / "voice"
BUILD_DIR = ROOT / "_build"
SITE_IMAGE_DIR = REPO / "site" / "static" / "img"
SITE_VIDEO_DIR = REPO / "site" / "static" / "video"

WIDTH = 1080
HEIGHT = 1920
FPS = 30

BLOG_URL = "https://ai-hub-jp.vercel.app/blog/2026-08-06-ai-work-design-future.html"
ACCOUNT = "@climbingconsul"
ARTICLE_TITLE = "AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」"
REVIEW_STATE = "review_ready_waiting_final_approval"
PUBLICATION_STATE = "未投稿"
VOICE_ID = "ja-JP-NanamiNeural"
VOICE_LABEL = "Microsoft Nanami Neural（日本語・女性）"
VOICE_RATE = "+0%"
VOICE_PITCH = "+0Hz"
VOICE_VOLUME = "+0%"
MUSIC_DUCKING_DB = 6
MUSIC_SIDECHAIN_THRESHOLD = 0.015
MUSIC_SIDECHAIN_RATIO = 1.4
MUSIC_BED_GAIN = 0.22
MUSIC_RIGHTS_BASIS = "self-generated/no external samples"
AUDIO_QA_THRESHOLDS = {
    "minimum_music_gain_reduction_db": 10.0,
    "minimum_ducking_db": 5.0,
    "maximum_ducking_db": 8.0,
    "minimum_narration_over_bgm_db": 8.0,
    "maximum_ducked_bgm_mean_dbfs": -30.0,
}

COLORS = {
    "blue": "#4F6FD8",
    "deep": "#3E58B8",
    "lilac": "#9184D8",
    "rose": "#E88EA0",
    "rose_soft": "#FFF0F3",
    "sky": "#F8FBFF",
    "ink": "#172033",
    "muted": "#6B7891",
    "line": "#DCE4F2",
    "white": "#FFFFFF",
}

BEATS = [
    {
        "label": "AI時代の問い",
        "text": ["AI時代に、デザインは", "不要になるのか？", "仕事設計の視点から考えます。"],
        "narration": "AI時代に、デザインは不要になるのか？ 仕事設計の視点から考えます。",
        "duration_seconds": 5.4,
        "image": "blog-ai-work-design-hero-20260806.webp",
        "accent": COLORS["deep"],
    },
    {
        "label": "速さのあとに残る仕事",
        "text": ["AIで仕事が", "速くなったのに", "なぜ決められない？"],
        "narration": "AIで仕事が、速くなったのに、なぜ決められない？",
        "duration_seconds": 4.0,
        "image": "blog-ai-work-design-hero-20260806.webp",
        "accent": COLORS["rose"],
    },
    {
        "label": "制作はAIへ",
        "text": ["AIが得意なのは", "作る・並べる", "選択肢を増やす"],
        "narration": "AIが得意なのは、作る、並べる、選択肢を増やす",
        "duration_seconds": 4.6,
        "image": "blog-ai-work-design-speed-20260806.webp",
        "accent": COLORS["blue"],
    },
    {
        "label": "判断と責任は人へ",
        "text": ["人が担うのは", "目的・優先順位", "最後の責任"],
        "narration": "人が担うのは、目的、優先順位、最後の責任",
        "duration_seconds": 4.2,
        "image": "blog-ai-work-design-system-20260806.webp",
        "accent": COLORS["rose"],
    },
    {
        "label": "すべての職種に共通",
        "text": ["これはデザインだけでなく", "すべての仕事の", "ワークデザイン"],
        "narration": "これはデザインだけでなく、すべての仕事の、ワークデザイン",
        "duration_seconds": 5.0,
        "image": "blog-ai-work-design-experience-20260806.webp",
        "accent": COLORS["lilac"],
    },
    {
        "label": "続きはAI相談のブログへ",
        "text": ["任せる・決める・確かめる", "3つに分けて", "明日から使おう"],
        "narration": "任せる、決める、確かめる、3つに分けて、明日から使おう",
        "duration_seconds": 5.6,
        "image": "blog-ai-work-design-three-lanes-20260806.webp",
        "accent": COLORS["deep"],
    },
]

TOTAL_SECONDS = round(sum(float(beat["duration_seconds"]) for beat in BEATS), 1)

CAPTION = f"""AIで資料もサイトもアプリも、驚くほど早く形になる。
でも、最後の「どれを選ぶか」で仕事が止まることがあります。

私自身、以前なら1か月単位で考えていた作業が2時間ほどで初稿まで進んでも、方向を決めるのに2日、3日かかることがあります。

AIが弱いからではありません。
作る時間が短くなったぶん、目的・優先順位・責任が濃く残るからです。

これはデザイナーだけの話ではなく、経営者、プロジェクトリーダー、先生、福祉の現場、個人事業主にも共通する「ワークデザイン」の話です。

まず一つの仕事を、
・AIに任せる
・人が決める
・結果を確かめる
の3つに分けてみてください。

詳しい考え方と15分で作れるメモは、AI相談のブログにまとめました。
{BLOG_URL}

#AI活用 #ワークデザイン #仕事術 #DX #デザイン #プロジェクト管理 #AI相談"""

STORY_COPY = "作業は速い。でも、決める仕事は残る。\nAI時代の『ワークデザイン』を約29秒で整理しました。"
STORY_LINK_LABEL = "詳細はこちら"
BRAND_COMMENT = "AIに全部任せるより、『任せる・決める・確かめる』を分けると現場で続きます。自分の仕事ならどう分けるか、気軽にDMしてください。"


def scene_starts() -> list[float]:
    starts: list[float] = []
    elapsed = 0.0
    for beat in BEATS:
        starts.append(round(elapsed, 3))
        elapsed += float(beat["duration_seconds"])
    return starts


def review_metadata_line() -> str:
    return f"約{TOTAL_SECONDS:.1f}秒 / {len(BEATS)}場面 / {REVIEW_STATE} / {PUBLICATION_STATE}"


def review_metadata() -> dict[str, object]:
    return {
        "article_title": ARTICLE_TITLE,
        "duration_seconds": TOTAL_SECONDS,
        "duration_label": f"約{TOTAL_SECONDS:.1f}秒",
        "scene_count": len(BEATS),
        "scene_label": f"{len(BEATS)}場面",
        "review_state": REVIEW_STATE,
        "publication_state": PUBLICATION_STATE,
        "summary": review_metadata_line(),
    }


def spoken_words(text: str) -> str:
    return re.sub(r"[\s、。・！？!?]", "", text)


def tts_text(text: str) -> str:
    text = re.sub(r"[、・]", "", text)
    text = re.sub(r"[。！？!?]+\s*", "、", text)
    return re.sub(r"\s+", "", text).strip("、")


def estimated_ducking_db(sidechain_level_db: float) -> float:
    threshold_db = 20.0 * math.log10(MUSIC_SIDECHAIN_THRESHOLD)
    level_above_threshold = max(0.0, sidechain_level_db - threshold_db)
    return level_above_threshold * (1.0 - 1.0 / MUSIC_SIDECHAIN_RATIO)


def _narration_intervals(voice_timings: list[dict[str, object]]) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    for start, timing in zip(scene_starts(), voice_timings):
        spoken_duration = float(timing["trimmed_duration_seconds"])
        interval_start = round(start + 0.02, 3)
        interval_end = round(min(start + float(timing["scene_duration_seconds"]), interval_start + spoken_duration), 3)
        if interval_end > interval_start:
            intervals.append((interval_start, interval_end))
    return intervals


def _ffmpeg_mean_dbfs(path: Path, intervals: list[tuple[float, float]]) -> float:
    ffmpeg = locate_ffmpeg()
    command = [str(ffmpeg), "-hide_banner", "-i", str(path)]
    if intervals:
        filters: list[str] = []
        labels: list[str] = []
        for index, (start, end) in enumerate(intervals):
            label = f"segment{index}"
            filters.append(
                f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[{label}]"
            )
            labels.append(f"[{label}]")
        filters.append(
            "".join(labels)
            + f"concat=n={len(labels)}:v=0:a=1,volumedetect[measured]"
        )
        command.extend(["-filter_complex", ";".join(filters), "-map", "[measured]"])
    else:
        command.extend(["-af", "volumedetect"])
    command.extend(["-f", "null", "NUL"])
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio measurement failed for {path}: {result.stderr}")
    match = re.search(r"mean_volume:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*dB", result.stderr, re.I)
    if not match or match.group(1).lower() == "-inf":
        raise RuntimeError(f"Could not measure a finite mean volume for {path}")
    return float(match.group(1))


def measure_audio_qa(
    narration: Path,
    music_source: Path,
    music_bed: Path,
    ducked_music: Path,
    voice_timings: list[dict[str, object]],
) -> dict[str, object]:
    intervals = _narration_intervals(voice_timings)
    narration_mean = _ffmpeg_mean_dbfs(narration, intervals)
    music_source_mean = _ffmpeg_mean_dbfs(music_source, intervals)
    music_bed_mean = _ffmpeg_mean_dbfs(music_bed, intervals)
    ducked_mean = _ffmpeg_mean_dbfs(ducked_music, intervals)
    music_input_gain = round(music_bed_mean - music_source_mean, 2)
    measured_ducking = round(music_bed_mean - ducked_mean, 2)
    narration_over_bgm = round(narration_mean - ducked_mean, 2)
    thresholds = dict(AUDIO_QA_THRESHOLDS)
    checks = {
        "self_generated_rights": MUSIC_RIGHTS_BASIS == "self-generated/no external samples",
        "music_gain_is_low": -music_input_gain >= thresholds["minimum_music_gain_reduction_db"],
        "ducking_meets_minimum": measured_ducking >= thresholds["minimum_ducking_db"],
        "ducking_not_excessive": measured_ducking <= thresholds["maximum_ducking_db"],
        "narration_is_primary": narration_over_bgm >= thresholds["minimum_narration_over_bgm_db"],
        "ducked_bgm_is_light": ducked_mean <= thresholds["maximum_ducked_bgm_mean_dbfs"],
    }
    return {
        "measurement_method": "ffmpeg_volumedetect_rms_dbfs",
        "measurement_scope": "generated narration-active intervals",
        "analysis_intervals_seconds": [
            {"start": start, "end": end} for start, end in intervals
        ],
        "rights_basis": MUSIC_RIGHTS_BASIS,
        "source": "Python standard-library synthesis at 48 kHz stereo",
        "external_samples": False,
        "narration_mean_dbfs": round(narration_mean, 2),
        "music_source_mean_dbfs": round(music_source_mean, 2),
        "music_bed_mean_dbfs": round(music_bed_mean, 2),
        "ducked_bgm_mean_dbfs": round(ducked_mean, 2),
        "music_input_gain_db": music_input_gain,
        "measured_ducking_db": measured_ducking,
        "narration_over_ducked_bgm_db": narration_over_bgm,
        "thresholds": thresholds,
        "checks": checks,
    }


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def find_font(bold: bool = False) -> Path:
    candidates = (
        [
            Path("C:/Windows/Fonts/YuGothB.ttc"),
            Path("C:/Windows/Fonts/meiryob.ttc"),
            Path("C:/Windows/Fonts/msgothic.ttc"),
        ]
        if bold
        else [
            Path("C:/Windows/Fonts/YuGothM.ttc"),
            Path("C:/Windows/Fonts/meiryo.ttc"),
            Path("C:/Windows/Fonts/msgothic.ttc"),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Japanese font was not found in C:/Windows/Fonts")


FONT_REGULAR = find_font(False)
FONT_BOLD = find_font(True)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def rounded_image(image: Image.Image, size: tuple[int, int], radius: int) -> Image.Image:
    fitted = ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    result = Image.new("RGBA", size, (255, 255, 255, 0))
    result.paste(fitted.convert("RGBA"), (0, 0), mask)
    return result


def fit_text_font(lines: list[str], max_width: int, start_size: int = 88, min_size: int = 54) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for size in range(start_size, min_size - 1, -2):
        candidate = font(size, bold=True)
        if all(probe.textbbox((0, 0), line, font=candidate)[2] <= max_width for line in lines):
            return candidate
    return font(min_size, bold=True)


def draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    y: int,
    box_width: int,
    fill: str,
    line_gap: int = 22,
) -> tuple[int, int]:
    selected = fit_text_font(lines, box_width)
    boxes = [draw.textbbox((0, 0), line, font=selected) for line in lines]
    heights = [box[3] - box[1] for box in boxes]
    total = sum(heights) + line_gap * (len(lines) - 1)
    current_y = y
    for line, box, line_height in zip(lines, boxes, heights):
        line_width = box[2] - box[0]
        x = (WIDTH - line_width) // 2
        draw.text((x, current_y - box[1]), line, font=selected, fill=hex_rgba(fill), stroke_width=1, stroke_fill=hex_rgba(fill))
        current_y += line_height + line_gap
    return y, y + total


def create_frame(index: int, beat: dict[str, object]) -> Path:
    source = Image.open(SOURCE_DIR / str(beat["image"])).convert("RGB")
    background = ImageOps.fit(source, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(34)).convert("RGBA")
    background.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), hex_rgba(COLORS["sky"], 218)))

    art = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))
    art_draw = ImageDraw.Draw(art)
    accent = str(beat["accent"])
    art_draw.ellipse((-190, -150, 430, 470), fill=hex_rgba(accent, 46))
    art_draw.ellipse((790, 1390, 1240, 1880), fill=hex_rgba(COLORS["lilac"], 34))

    # Top progress indicator remains below Instagram's top UI safe area.
    progress_y = 222
    progress_left = 108
    progress_gap = 16
    progress_width = (WIDTH - progress_left * 2 - progress_gap * (len(BEATS) - 1)) // len(BEATS)
    for dot in range(len(BEATS)):
        x1 = progress_left + dot * (progress_width + progress_gap)
        color = accent if dot == index else COLORS["line"]
        art_draw.rounded_rectangle((x1, progress_y, x1 + progress_width, progress_y + 12), radius=6, fill=hex_rgba(color))

    label_font = font(31, bold=True)
    label = str(beat["label"])
    label_box = art_draw.textbbox((0, 0), label, font=label_font)
    label_w = label_box[2] - label_box[0]
    label_x = (WIDTH - label_w) // 2
    art_draw.rounded_rectangle((label_x - 30, 262, label_x + label_w + 30, 320), radius=29, fill=hex_rgba(COLORS["white"], 238))
    art_draw.text((label_x, 274 - label_box[1]), label, font=label_font, fill=hex_rgba(COLORS["deep"]))

    # Visual card.
    card_x, card_y, card_w, card_h = 90, 360, 900, 506
    shadow = Image.new("RGBA", (card_w + 44, card_h + 44), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((22, 22, card_w + 21, card_h + 21), radius=42, fill=(40, 54, 100, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    art.alpha_composite(shadow, (card_x - 22, card_y - 10))
    visual = rounded_image(source, (card_w, card_h), 34)
    art.alpha_composite(visual, (card_x, card_y))
    art_draw.rounded_rectangle((card_x, card_y, card_x + card_w - 1, card_y + card_h - 1), radius=34, outline=hex_rgba(COLORS["white"]), width=5)

    # Main message card. Its bottom stays above Reels caption/action UI.
    text_y1, text_y2 = 930, 1440
    art_draw.rounded_rectangle((76, text_y1, WIDTH - 76, text_y2), radius=44, fill=hex_rgba(COLORS["white"], 242), outline=hex_rgba(COLORS["line"]), width=2)
    art_draw.rounded_rectangle((76, text_y1, 92, text_y2), radius=8, fill=hex_rgba(accent))
    lines = list(beat["text"])
    draw_centered_lines(art_draw, lines, 1015, 820, COLORS["ink"], line_gap=24)

    brand_font = font(34, bold=True)
    brand = "AI相談"
    brand_box = art_draw.textbbox((0, 0), brand, font=brand_font)
    brand_w = brand_box[2] - brand_box[0]
    art_draw.text(((WIDTH - brand_w) // 2, 1492 - brand_box[1]), brand, font=brand_font, fill=hex_rgba(COLORS["deep"]))
    handle_font = font(25)
    handle_box = art_draw.textbbox((0, 0), ACCOUNT, font=handle_font)
    handle_w = handle_box[2] - handle_box[0]
    art_draw.text(((WIDTH - handle_w) // 2, 1544 - handle_box[1]), ACCOUNT, font=handle_font, fill=hex_rgba(COLORS["muted"]))

    frame = Image.alpha_composite(background, art).convert("RGB")
    output = FRAME_DIR / f"frame-{index + 1:02d}.png"
    frame.save(output, "PNG", optimize=True)
    return output


def locate_ffmpeg() -> Path:
    candidates = [
        Path("C:/Project/グッぼる/media/output/myreel/2026-07-03-finger-training-reframe/pydeps/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"),
    ]
    system = shutil.which("ffmpeg")
    if system:
        candidates.append(Path(system))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("ffmpeg was not found")


def run_ffmpeg(frame_paths: list[Path]) -> Path:
    ffmpeg = locate_ffmpeg()
    output = BUILD_DIR / "reel-video-only.mp4"
    concat_file = BUILD_DIR / "frames.concat.txt"
    concat_lines: list[str] = []
    for index, (path, start, beat) in enumerate(zip(frame_paths, scene_starts(), BEATS), start=1):
        escaped_path = path.resolve().as_posix().replace("'", "'\\''")
        concat_lines.extend(
            [
                f"# scene={index} start={start:.1f}",
                f"file '{escaped_path}'",
                f"duration {float(beat['duration_seconds']):.1f}",
            ]
        )
    final_path = frame_paths[-1].resolve().as_posix().replace("'", "'\\''")
    concat_lines.append(f"file '{final_path}'")
    concat_file.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    command = [
        str(ffmpeg),
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-t",
        str(TOTAL_SECONDS),
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-an",
        str(output),
    ]
    subprocess.run(command, check=True)
    return output


def media_duration(path: Path) -> float:
    ffmpeg = locate_ffmpeg()
    result = subprocess.run([str(ffmpeg), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    details = result.stderr
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", details)
    if not match:
        raise RuntimeError(f"Could not read media duration: {path}")
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


async def generate_voice_raw() -> list[Path]:
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, beat in enumerate(BEATS, start=1):
        text = tts_text(str(beat["narration"]))
        output = VOICE_DIR / f"beat-{index:02d}-raw.mp3"
        communicate = edge_tts.Communicate(
            text=text,
            voice=VOICE_ID,
            rate=VOICE_RATE,
            volume=VOICE_VOLUME,
            pitch=VOICE_PITCH,
        )
        await communicate.save(str(output))
        outputs.append(output)
    return outputs


def normalize_voice_clips(raw_clips: list[Path]) -> tuple[list[Path], list[dict[str, object]]]:
    ffmpeg = locate_ffmpeg()
    outputs: list[Path] = []
    timings: list[dict[str, object]] = []
    for index, (source, beat) in enumerate(zip(raw_clips, BEATS), start=1):
        text = str(beat["narration"])
        scene_duration = float(beat["duration_seconds"])
        raw_duration = media_duration(source)
        trimmed = BUILD_DIR / f"beat-{index:02d}-trimmed.wav"
        trim_filter = (
            "silenceremove=start_periods=1:start_silence=0:start_threshold=-45dB,"
            "areverse,"
            "silenceremove=start_periods=1:start_silence=0:start_threshold=-45dB,"
            "areverse,aresample=48000,aformat=sample_fmts=s16:channel_layouts=stereo"
        )
        subprocess.run(
            [
                str(ffmpeg),
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-af",
                trim_filter,
                "-ar",
                "48000",
                "-ac",
                "2",
                str(trimmed),
            ],
            check=True,
        )
        trimmed_duration = media_duration(trimmed)
        if trimmed_duration + 0.04 > scene_duration:
            raise RuntimeError(
                f"Beat {index} narration is {trimmed_duration:.2f}s and does not fit "
                f"the {scene_duration:.2f}s scene without speed-up"
            )
        tempo = 1.0
        output = BUILD_DIR / f"beat-{index:02d}-normalized.wav"
        audio_filter = (
            "aresample=48000,"
            "aformat=sample_fmts=s16:channel_layouts=stereo,"
            "loudnorm=I=-16:TP=-1.5:LRA=7,"
            f"adelay=20|20,apad=whole_dur={scene_duration:.3f},"
            f"atrim=end={scene_duration:.3f},asetpts=N/SR/TB,"
            f"afade=t=in:st=0:d=0.02,afade=t=out:st={scene_duration - 0.04:.3f}:d=0.04"
        )
        command = [
            str(ffmpeg),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(trimmed),
            "-af",
            audio_filter,
            "-ar",
            "48000",
            "-ac",
            "2",
            str(output),
        ]
        subprocess.run(command, check=True)
        outputs.append(output)
        timings.append(
            {
                "beat": index,
                "text": text,
                "raw_duration_seconds": round(raw_duration, 2),
                "trimmed_duration_seconds": round(trimmed_duration, 2),
                "tempo_multiplier": round(tempo, 3),
                "scene_duration_seconds": scene_duration,
                "normalized_duration_seconds": round(media_duration(output), 2),
            }
        )
    return outputs, timings


def create_background_music() -> Path:
    sample_rate = 48_000
    channels = 2
    total_frames = int(round(TOTAL_SECONDS * sample_rate))
    fade_in_frames = int(0.35 * sample_rate)
    fade_out_frames = int(0.8 * sample_rate)
    seconds_per_beat = 60.0 / 92.0
    chords = (
        (220.00, 261.63, 329.63),
        (196.00, 246.94, 293.66),
        (174.61, 220.00, 261.63),
        (196.00, 246.94, 329.63),
    )
    output = ROOT / "background-music.wav"
    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        chunk = bytearray()
        for frame_index in range(total_frames):
            time_seconds = frame_index / sample_rate
            beat_position = time_seconds / seconds_per_beat
            chord = chords[int(beat_position // 4) % len(chords)]
            pad = sum(math.sin(2.0 * math.pi * frequency * time_seconds) for frequency in chord) / len(chord)
            pulse_phase = beat_position % 1.0
            pulse_envelope = math.exp(-5.2 * pulse_phase)
            pulse = math.sin(2.0 * math.pi * 110.0 * time_seconds) * pulse_envelope
            shimmer = math.sin(2.0 * math.pi * chord[1] * 2.0 * time_seconds) * 0.10
            envelope = min(1.0, frame_index / max(1, fade_in_frames))
            frames_remaining = total_frames - frame_index - 1
            envelope *= min(1.0, frames_remaining / max(1, fade_out_frames))
            sample = (0.075 * pad + 0.040 * pulse + 0.012 * shimmer) * envelope
            left = int(max(-1.0, min(1.0, sample * 0.98)) * 32767)
            right = int(max(-1.0, min(1.0, sample * 1.02)) * 32767)
            chunk.extend(struct.pack("<hh", left, right))
            if len(chunk) >= 16_384:
                wav_file.writeframesraw(chunk)
                chunk.clear()
        if chunk:
            wav_file.writeframesraw(chunk)
    return output


def create_music_mix_tracks(narration: Path, background_music: Path) -> tuple[Path, Path]:
    ffmpeg = locate_ffmpeg()
    music_bed = ROOT / "music-bed.wav"
    ducked_music = ROOT / "ducked-background-music.wav"
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(background_music),
            "-af",
            f"volume={MUSIC_BED_GAIN}",
            "-t",
            str(TOTAL_SECONDS),
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(music_bed),
        ],
        check=True,
    )
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(music_bed),
            "-i",
            str(narration),
            "-filter_complex",
            (
                "[0:a][1:a]"
                f"sidechaincompress=threshold={MUSIC_SIDECHAIN_THRESHOLD}:ratio={MUSIC_SIDECHAIN_RATIO}:"
                "attack=20:release=350,"
                f"atrim=end={TOTAL_SECONDS}[ducked]"
            ),
            "-map",
            "[ducked]",
            "-t",
            str(TOTAL_SECONDS),
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(ducked_music),
        ],
        check=True,
    )
    return music_bed, ducked_music


def concatenate_voice(clips: list[Path]) -> Path:
    ffmpeg = locate_ffmpeg()
    output = ROOT / "narration.m4a"
    command = [str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error"]
    for clip in clips:
        command.extend(["-i", str(clip)])
    delayed = []
    labels = []
    for index, start in enumerate(scene_starts()):
        delay_ms = round(start * 1000)
        label = f"a{index}"
        delayed.append(f"[{index}:a]adelay={delay_ms}|{delay_ms}[{label}]")
        labels.append(f"[{label}]")
    filter_graph = (
        ";".join(delayed)
        + ";"
        + "".join(labels)
        + f"amix=inputs={len(clips)}:normalize=0:duration=longest,"
        + f"apad=whole_dur={TOTAL_SECONDS},atrim=end={TOTAL_SECONDS}[outa]"
    )
    command.extend(
        [
            "-filter_complex",
            filter_graph,
            "-map",
            "[outa]",
            "-t",
            str(TOTAL_SECONDS),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            str(output),
        ]
    )
    subprocess.run(command, check=True)
    return output


def mix_voice(video_only: Path, narration: Path, ducked_music: Path) -> Path:
    ffmpeg = locate_ffmpeg()
    output = ROOT / "reel.mp4"
    command = [
        str(ffmpeg),
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_only),
        "-i",
        str(narration),
        "-i",
        str(ducked_music),
        "-filter_complex",
        (
            "[2:a][1:a]"
            "amix=inputs=2:weights='1 1':normalize=0:duration=longest,"
            f"atrim=end={TOTAL_SECONDS},alimiter=limit=0.95[outa]"
        ),
        "-map",
        "0:v:0",
        "-map",
        "[outa]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-t",
        str(TOTAL_SECONDS),
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(command, check=True)
    return output


def make_cover(frame_paths: list[Path]) -> Path:
    cover = Image.open(frame_paths[0]).convert("RGB")
    output = ROOT / "cover.png"
    cover.save(output, "PNG", optimize=True)
    return output


def make_storyboard(frame_paths: list[Path]) -> Path:
    thumb_w, thumb_h = 160, 284
    canvas = Image.new("RGB", (1080, 520), hex_rgba(COLORS["sky"])[:3])
    draw = ImageDraw.Draw(canvas)
    title_font = font(34, bold=True)
    title = "AIとデザインの未来｜約29秒リール（6場面）"
    draw.text((40, 34), title, font=title_font, fill=hex_rgba(COLORS["ink"])[:3])
    for index, path in enumerate(frame_paths):
        image = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = 20 + index * 176
        canvas.paste(image, (x, 116))
        draw.rounded_rectangle((x, 116, x + thumb_w - 1, 116 + thumb_h - 1), radius=12, outline=hex_rgba(COLORS["line"])[:3], width=2)
        number_font = font(20, bold=True)
        duration = float(BEATS[index]["duration_seconds"])
        draw.text((x + 8, 425), f"{index + 1}｜{duration:.1f}秒", font=number_font, fill=hex_rgba(COLORS["deep"])[:3])
    output = ROOT / "storyboard.png"
    canvas.save(output, "PNG", optimize=True)
    return output


def make_preview_gif(frame_paths: list[Path]) -> Path:
    previews = [Image.open(path).convert("RGB").resize((360, 640), Image.Resampling.LANCZOS) for path in frame_paths]
    output = ROOT / "preview.gif"
    durations_ms = [round(float(beat["duration_seconds"]) * 1000) for beat in BEATS]
    previews[0].save(output, save_all=True, append_images=previews[1:], duration=durations_ms, loop=0, optimize=True)
    return output


def make_story_preview() -> Path:
    source = Image.open(SOURCE_DIR / "blog-ai-work-design-hero-20260806.webp").convert("RGB")
    background = ImageOps.fit(source, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(32)).convert("RGBA")
    background.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), hex_rgba(COLORS["sky"], 220)))
    art = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(art)
    draw.ellipse((-210, -160, 450, 500), fill=hex_rgba(COLORS["rose"], 48))
    draw.ellipse((760, 1400, 1240, 1910), fill=hex_rgba(COLORS["lilac"], 40))

    brand_font = font(34, bold=True)
    draw.text((82, 250), "AI相談", font=brand_font, fill=hex_rgba(COLORS["deep"]))
    draw.text((82, 300), ACCOUNT, font=font(25), fill=hex_rgba(COLORS["muted"]))

    visual = rounded_image(source, (880, 495), 36)
    art.alpha_composite(visual, (100, 390))
    draw.rounded_rectangle((100, 390, 979, 884), radius=36, outline=hex_rgba(COLORS["white"]), width=5)

    draw.rounded_rectangle((84, 955, 996, 1360), radius=46, fill=hex_rgba(COLORS["white"], 244), outline=hex_rgba(COLORS["line"]), width=2)
    story_lines = ["作業は速い。", "でも、決める仕事は残る。", "AI時代のワークデザイン"]
    draw_centered_lines(draw, story_lines, 1038, 810, COLORS["ink"], line_gap=24)

    # Review placeholder. Instagram投稿時は、この位置へネイティブのリンクスタンプを置く。
    sticker_x1, sticker_y1, sticker_x2, sticker_y2 = 310, 1440, 770, 1540
    draw.rounded_rectangle((sticker_x1, sticker_y1, sticker_x2, sticker_y2), radius=50, fill=hex_rgba(COLORS["deep"]), outline=hex_rgba(COLORS["white"]), width=4)
    sticker_font = font(38, bold=True)
    sticker_box = draw.textbbox((0, 0), STORY_LINK_LABEL, font=sticker_font)
    sticker_w = sticker_box[2] - sticker_box[0]
    sticker_h = sticker_box[3] - sticker_box[1]
    draw.text(((WIDTH - sticker_w) // 2, sticker_y1 + (sticker_y2 - sticker_y1 - sticker_h) // 2 - sticker_box[1]), STORY_LINK_LABEL, font=sticker_font, fill=hex_rgba(COLORS["white"]))
    draw.text((WIDTH // 2 - 154, 1580), "リンクスタンプ配置位置", font=font(25), fill=hex_rgba(COLORS["muted"]))

    output = ROOT / "story-preview.png"
    Image.alpha_composite(background, art).convert("RGB").save(output, "PNG", optimize=True)
    return output


def inspect_video(
    video: Path,
    voice_timings: list[dict[str, object]],
    audio_measurements: dict[str, object],
) -> dict[str, object]:
    ffmpeg = locate_ffmpeg()
    result = subprocess.run([str(ffmpeg), "-hide_banner", "-i", str(video), "-f", "null", "NUL"], capture_output=True, text=True)
    details = result.stderr
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", details)
    duration = None
    if duration_match:
        duration = int(duration_match.group(1)) * 3600 + int(duration_match.group(2)) * 60 + float(duration_match.group(3))
    stream_line = next((line.strip() for line in details.splitlines() if "Video:" in line), "")
    audio_line = next((line.strip() for line in details.splitlines() if "Audio:" in line), "")
    detected = {
        "article_title": ARTICLE_TITLE,
        "reel_metadata": review_metadata(),
        "width": 1080 if "1080x1920" in stream_line else None,
        "height": 1920 if "1080x1920" in stream_line else None,
        "duration_seconds": duration,
        "fps": 30 if "30 fps" in stream_line else None,
        "codec": "h264" if "h264" in stream_line.lower() else None,
        "pixel_format": "yuv420p" if "yuv420p" in stream_line.lower() else None,
        "audio": "present" if audio_line else "absent",
        "audio_codec": "aac" if "aac" in audio_line.lower() else None,
        "audio_sample_rate_hz": 48000 if "48000 hz" in audio_line.lower() else None,
        "scene_count": len(BEATS),
        "scene_starts_seconds": scene_starts(),
        "duration_contract_seconds": TOTAL_SECONDS,
        "text_narration_mapping": [
            {
                "scene": index,
                "label": beat["label"],
                "text": beat["text"],
                "narration": beat["narration"],
                "words_aligned": spoken_words("".join(beat["text"])) == spoken_words(str(beat["narration"])),
            }
            for index, beat in enumerate(BEATS, start=1)
        ],
        "narration": {
            "language": "ja-JP",
            "voice_id": VOICE_ID,
            "voice_label": VOICE_LABEL,
            "rate": VOICE_RATE,
            "pitch": VOICE_PITCH,
            "target_loudness_lufs": -16,
            "beats": voice_timings,
        },
        "audio_measurements": audio_measurements,
        "background_music": {
            "file": "background-music.wav",
            "music_bed_file": "music-bed.wav",
            "ducked_file": "ducked-background-music.wav",
            "sample_rate_hz": 48000,
            "channels": 2,
            "tempo_bpm": 92,
            "music_ducking_db": MUSIC_DUCKING_DB,
            "music_input_gain": MUSIC_BED_GAIN,
            "source": "python_standard_library_synthesis",
            "rights_basis": MUSIC_RIGHTS_BASIS,
            "external_samples": False,
            "present": (ROOT / "background-music.wav").exists(),
        },
        "publication": {
            "status": "blocked_until_final_approval_and_verified_blog_url",
            "instagram_posted": False,
            "draft_created": False,
        },
        "file_bytes": video.stat().st_size,
        "stream_evidence": stream_line,
        "audio_evidence": audio_line,
    }
    detected["checks"] = {
        "portrait_1080x1920": detected["width"] == 1080 and detected["height"] == 1920,
        "duration_about_28_8_seconds": duration is not None and abs(duration - TOTAL_SECONDS) <= 0.08,
        "fps_30": detected["fps"] == 30,
        "codec_h264": detected["codec"] == "h264",
        "pixel_format_yuv420p": detected["pixel_format"] == "yuv420p",
        "audio_present": detected["audio"] == "present",
        "audio_codec_aac": detected["audio_codec"] == "aac",
        "audio_sample_rate_48000": detected["audio_sample_rate_hz"] == 48000,
        "six_scenes": len(BEATS) == 6,
        "max_three_lines": all(len(beat["text"]) <= 3 for beat in BEATS),
        "text_narration_aligned": all(
            spoken_words("".join(beat["text"])) == spoken_words(str(beat["narration"])) for beat in BEATS
        ),
        "narration_normal_speed": VOICE_RATE == "+0%" and all(timing["tempo_multiplier"] == 1.0 for timing in voice_timings),
        "background_music_present": (ROOT / "background-music.wav").exists(),
        "music_bed_present": (ROOT / "music-bed.wav").exists(),
        "ducked_music_present": (ROOT / "ducked-background-music.wav").exists(),
        "audio_measurements_pass": all(audio_measurements["checks"].values()),
        "publication_blocked": True,
    }
    return detected


def write_text_assets(qa: dict[str, object]) -> None:
    on_screen = "\n".join(
        f"{index + 1}. {beat['label']}\n   " + " / ".join(beat["text"])
        for index, beat in enumerate(BEATS)
    )
    voice_script = "\n".join(
        f"{index + 1}. {beat['narration']}（{float(beat['duration_seconds']):.1f}秒）"
        for index, beat in enumerate(BEATS)
    )
    sync_points = "、".join(f"{start:.1f}秒" for start in scene_starts())
    metadata_line = review_metadata_line()
    qa_record = {**qa, "article_title": ARTICLE_TITLE, "reel_metadata": review_metadata()}
    audio_qa = qa_record["audio_measurements"]
    audio_summary = (
        f"narration {audio_qa['narration_mean_dbfs']:.2f} dBFS / "
        f"music gain {audio_qa['music_input_gain_db']:.2f} dB / "
        f"ducked BGM {audio_qa['ducked_bgm_mean_dbfs']:.2f} dBFS / "
        f"measured ducking {audio_qa['measured_ducking_db']:.2f} dB / "
        f"voice lead {audio_qa['narration_over_ducked_bgm_db']:.2f} dB"
    )
    (ROOT / "narration.md").write_text(
        f"""# {ARTICLE_TITLE}｜女性ナレーション

## Reelメタデータ

{metadata_line}

- 声: {VOICE_LABEL}
- 言語: 日本語（ja-JP）
- 速度: {VOICE_RATE}
- ピッチ: {VOICE_PITCH}
- 目標音量: -16 LUFS
- 同期: {sync_points}
- BGM: background-music.wav（Python標準ライブラリで合成、92 BPM、ナレーション中は約6dBダッキング）
- 音声実測: {audio_summary}
- 権利根拠: `{audio_qa['rights_basis']}`

## 台本

{voice_script}

各文は画面切替と同時に始まり、速度変更なしで中央テキストを全文読み上げる。句読点と中黒だけを自然な読点として扱い、省略・言い換えはしない。
""",
        encoding="utf-8",
    )
    (ROOT / "captions.md").write_text(
        f"""# {ARTICLE_TITLE}｜リール投稿文

投稿先: `{ACCOUNT}`
Reelレビュー状態: {metadata_line}
状態: 最終承認待ち（Instagram未投稿）

## 画面内テキスト（6場面）

{on_screen}

## 女性ナレーション

{voice_script}

## キャプション

{CAPTION}

## ストーリー

{STORY_COPY}

- リンク先: {BLOG_URL}
- リンクラベル: `{STORY_LINK_LABEL}`
- 配置: 画面下部中央のセーフエリア

## ブランドコメント

{BRAND_COMMENT}
""",
        encoding="utf-8",
    )
    (ROOT / "story.md").write_text(
        f"""# {ARTICLE_TITLE}｜ストーリー投稿セット

Reelレビュー状態: {metadata_line}
状態: リール公開後の2回目承認待ち（Instagram未投稿）

## 本文

{STORY_COPY}

## リンクスタンプ

- URL: {BLOG_URL}
- ラベル: `{STORY_LINK_LABEL}`
- 配置: 画面下部中央のセーフエリア

## ブランドコメント

{BRAND_COMMENT}
""",
        encoding="utf-8",
    )
    (ROOT / "tone.md").write_text(
        f"""# トーンとデザインの根拠

確認日: 2026-08-06

- 投稿先はAI相談の公式Instagram `{ACCOUNT}`。Feed／Reels／Storiesを使用し、Threadsは使用しない。
- 公式プロフィールの公開文面は、事業、実践、プラグマティズムを率直に伝える調子だった。
- 公開グリッドは個人・事業の実写が混在し、AI相談として統一された最新ビジュアル体系は確認できなかった。
- そのためデザインは、AI相談公式サイトの最新Clear Sky Roseを基準にした。
- 既存のAI相談向けリール資産の読みやすい型を継承し、内容紹介を加えた約29秒／6場面へ更新した。
- 音声は `{VOICE_LABEL}`。親しみやすさと信頼感を保ち、通常速度で画面中央の全文を読む。
- BGMは外部音源やサンプルを使わずPython標準ライブラリだけで合成し、ナレーション中は約6dBダッキングする。
- FFmpeg `volumedetect` で生成済みナレーション、原BGM、入力ゲイン後bed、duck後BGMのナレーション区間RMSを実測する。今回の結果は {audio_summary}。
- 権利根拠は `{audio_qa['rights_basis']}`。閾値判定は `qa.json` と `posting-manifest.json` に同値で保存する。
- 難しいAI用語から入らず、「作るのは速いが決められない」という身近な悩みから始めた。
- ロボット、サイバー空間、別事業の配色・写真・ロゴは使っていない。
""",
        encoding="utf-8",
    )
    manifest = {
        "campaign": "2026-08-06-ai-work-design-future",
        "article_title": ARTICLE_TITLE,
        "reel_metadata": review_metadata(),
        "status": REVIEW_STATE,
        "publication_state": PUBLICATION_STATE,
        "account": ACCOUNT,
        "platform": "Instagram",
        "surfaces": ["Reels", "Stories"],
        "excluded_surfaces": ["Threads"],
        "draft_mode": False,
        "blog": {
            "url": BLOG_URL,
            "status": "planned_unverified_until_production",
        },
        "reel": {
            "title": ARTICLE_TITLE,
            "review_metadata": review_metadata(),
            "file": "reel.mp4",
            "cover": "cover.png",
            "duration_seconds": TOTAL_SECONDS,
            "beats": BEATS,
            "caption_file": "captions.md",
            "audio": {
                "file": "narration.m4a",
                "language": "ja-JP",
                "voice_id": VOICE_ID,
                "voice_label": VOICE_LABEL,
                "rate": VOICE_RATE,
                "script": [beat["narration"] for beat in BEATS],
                "speed_up": False,
                "background_music_file": "background-music.wav",
                "music_bed_file": "music-bed.wav",
                "ducked_background_music_file": "ducked-background-music.wav",
                "music_ducking_db": MUSIC_DUCKING_DB,
                "measured_qa": audio_qa,
            },
            "status": "blocked_until_final_approval_and_verified_blog_url",
        },
        "story": {
            "asset": "story-preview.png",
            "copy": STORY_COPY,
            "link": BLOG_URL,
            "link_label": STORY_LINK_LABEL,
            "placement": "bottom-center-safe-area",
            "status": "blocked_until_reel_is_public_and_second_approval",
        },
        "brand_comment": {
            "copy": BRAND_COMMENT,
            "status": "blocked_until_reel_is_public_and_second_approval",
        },
        "qa": qa_record,
    }
    (ROOT / "posting-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "qa.json").write_text(json.dumps(qa_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "pre-post-confirmation.md").write_text(
        f"""# {ARTICLE_TITLE}｜投稿直前確認

Reelレビュー状態: {metadata_line}
状態: 未承認・未投稿

- [ ] 完成動画、6つの画面文、キャプション、ストーリー、コメントをユーザーが最終承認した
- [ ] 本番ブログURL `{BLOG_URL}` がHTTP 200で表示できる
- [ ] Chrome上の投稿先が `{ACCOUNT}` と画面表示で確認できる
- [ ] リールの「シェア」直前に動画、表紙、キャプションを再確認した
- [ ] 女性ナレーションが6場面の中央テキスト全文と合い、音割れや不自然な切れがない
- [ ] BGMがナレーションを邪魔せず、無音部とナレーション部で自然に音量が変わる
- [ ] Instagram下書きを使わず、直接投稿する
- [ ] リール公開URLを取得した
- [ ] ストーリーとブランドコメントは、リール公開後に2回目の承認を得た
- [ ] Threadsへ投稿しない
""",
        encoding="utf-8",
    )
    (ROOT / "README.md").write_text(
        f"""# {ARTICLE_TITLE}｜Instagramリール

作成日: 2026-08-06
投稿先: `{ACCOUNT}`
Reelレビュー状態: {metadata_line}
状態: 最終承認待ち（未投稿）

## 内容

- `reel.mp4`: 1080×1920、約28.8秒、30fps、H.264、日本語女性ナレーション・オリジナルBGM付き
- `narration.m4a`: 6場面に同期した通常速度のナレーション音声
- `background-music.wav`: 48kHzステレオ、92 BPMの軽量な自動合成BGM
- `music-bed.wav`: 原BGMへ入力ゲインを適用したダッキング前の比較用音源
- `ducked-background-music.wav`: 生成済みナレーションをsidechainにした実際のダッキング後BGM
- `narration.md`: 声の設定、同期位置、読み上げ台本
- `voice/`: 場面ごとの音声原本
- `cover.png`: リール表紙
- `storyboard.png`: 6場面一覧
- `preview.gif`: 軽量プレビュー
- `story-preview.png`: ストーリー画像とリンクスタンプ配置見本
- `captions.md`: 画面文、キャプション、ストーリー、ブランドコメント
- `story.md`: リール公開後に使うストーリー一式
- `tone.md`: ブランド調査とデザイン根拠
- `posting-manifest.json`: 公開順序と承認状態
- `qa.json`: 動画仕様と実測音声dB、入力ゲイン、ダッキング量、声/BGM差、権利根拠、閾値合否の機械検証
- `source/`: 記事と共通の生成画像
- `frames/`: 動画の6場面

## 再生成

```powershell
.\\.venv\\Scripts\\python.exe media\\output\\myreel\\2026-08-06-ai-work-design-future\\build_reel.py
```

生成後も自動投稿はしない。ブログの本番URLを確認し、完成一式の最終承認を得てからInstagramへ直接投稿する。リール公開後、ストーリーとブランドコメントは2回目の承認後に投稿する。Threadsは使用しない。

音声QAはFFmpeg `volumedetect` で、生成済みナレーションと3段階のBGM（原音／gain後bed／duck後）を同じナレーション実音区間で測る。`music_input_gain_db` は原音からbedへの実測差、`measured_ducking_db` はbedからduck後への実測差、`narration_over_ducked_bgm_db` は声がduck後BGMを何dB上回るかを表す。今回の実測は {audio_summary}、権利根拠は `{audio_qa['rights_basis']}`。全閾値は `qa.json` の `audio_measurements.thresholds` と `checks` を正とする。
""",
        encoding="utf-8",
    )
    safe_caption = html.escape(CAPTION).replace("\n", "<br>")
    safe_story = html.escape(STORY_COPY).replace("\n", "<br>")
    safe_comment = html.escape(BRAND_COMMENT)
    (ROOT / "review.html").write_text(
        f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{ARTICLE_TITLE}｜リール確認</title>
<style>body{{margin:0;background:#f8fbff;color:#172033;font-family:'Yu Gothic UI','Meiryo',sans-serif}}main{{width:min(1080px,92vw);margin:40px auto 80px}}h1{{font-size:clamp(28px,5vw,52px)}}.note{{padding:16px 20px;border-left:6px solid #e88ea0;background:#fff0f3;border-radius:14px}}.grid{{display:grid;grid-template-columns:minmax(280px,430px) 1fr;gap:28px;align-items:start;margin-top:28px}}video,img{{max-width:100%;border-radius:20px;box-shadow:0 16px 40px rgba(62,88,184,.14)}}section{{padding:24px;background:#fff;border:1px solid #dce4f2;border-radius:18px;margin-bottom:18px;line-height:1.8}}pre{{white-space:pre-wrap;font:inherit}}@media(max-width:800px){{.grid{{grid-template-columns:1fr}}}}</style></head>
<body><main><h1>{ARTICLE_TITLE}｜リール確認</h1><p class="note">投稿先 {ACCOUNT}／Reelレビュー状態: {metadata_line}／状態: 最終承認待ち・未投稿</p><img src="storyboard.png" alt="6場面の一覧">
<div class="grid"><video controls muted playsinline poster="cover.png"><source src="reel.mp4" type="video/mp4"></video><div>
<section><h2>ストーリー見本</h2><img src="story-preview.png" alt="ストーリーとリンクスタンプの配置見本"></section>
<section><h2>キャプション</h2><p>{safe_caption}</p></section>
<section><h2>ストーリー</h2><p>{safe_story}</p><p><b>{STORY_LINK_LABEL}</b><br>{BLOG_URL}</p></section>
<section><h2>ブランドコメント</h2><p>{safe_comment}</p></section>
</div></div></main></body></html>""",
        encoding="utf-8",
    )


def copy_inputs() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for beat in BEATS:
        source = SITE_IMAGE_DIR / str(beat["image"])
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, SOURCE_DIR / source.name)


def publish_site_assets(video: Path, cover: Path) -> None:
    SITE_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, SITE_VIDEO_DIR / "blog-ai-work-design-future-20260806.mp4")
    shutil.copy2(cover, SITE_IMAGE_DIR / "blog-ai-work-design-reel-cover-20260806.png")


def main() -> None:
    copy_inputs()
    frames = [create_frame(index, beat) for index, beat in enumerate(BEATS)]
    video_only = run_ffmpeg(frames)
    raw_voice = asyncio.run(generate_voice_raw())
    normalized_voice, voice_timings = normalize_voice_clips(raw_voice)
    narration = concatenate_voice(normalized_voice)
    background_music = create_background_music()
    music_bed, ducked_music = create_music_mix_tracks(narration, background_music)
    audio_measurements = measure_audio_qa(
        narration,
        background_music,
        music_bed,
        ducked_music,
        voice_timings,
    )
    if not all(audio_measurements["checks"].values()):
        raise RuntimeError(f"Audio QA failed: {audio_measurements}")
    video = mix_voice(video_only, narration, ducked_music)
    cover = make_cover(frames)
    make_storyboard(frames)
    make_preview_gif(frames)
    make_story_preview()
    qa = inspect_video(video, voice_timings, audio_measurements)
    checks = qa["checks"]
    if not all(checks.values()):
        raise RuntimeError(f"Video QA failed: {checks}")
    write_text_assets(qa)
    publish_site_assets(video, cover)
    print(json.dumps({"video": str(video), "qa": qa}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
