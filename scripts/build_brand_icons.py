"""Generate the AI相談 favicon and iPhone/PWA icon family.

The mark combines a speech bubble (consultation) with a custom-drawn "AI"
monogram. The letterforms are paths/shapes rather than font glyphs so the
result stays consistent across build environments.
"""

from __future__ import annotations

from pathlib import Path
import shutil

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "site" / "static"
VERSION = "20260725"

INK = "#172033"
INK_DEEP = "#0F1626"
BLUE = "#5367D9"
VIOLET = "#7A67D8"
WHITE = "#FFFFFF"


def _scale_point(point: tuple[float, float], scale: float) -> tuple[int, int]:
    return (round(point[0] * scale), round(point[1] * scale))


def _draw_logo(size: int, *, rounded_outer: bool) -> Image.Image:
    supersample = 8 if size <= 48 else 4
    canvas_size = size * supersample
    scale = canvas_size / 512
    image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    radius = round(112 * scale) if rounded_outer else 0
    draw.rounded_rectangle(
        (0, 0, canvas_size, canvas_size),
        radius=radius,
        fill=INK,
    )

    # A restrained diagonal panel adds depth without weakening the silhouette.
    draw.polygon(
        [
            _scale_point((286, 0), scale),
            _scale_point((512, 0), scale),
            _scale_point((512, 512), scale),
            _scale_point((406, 512), scale),
        ],
        fill=INK_DEEP,
    )

    # Consultation speech bubble.
    bubble = [
        _scale_point((120, 104), scale),
        _scale_point((392, 104), scale),
        _scale_point((424, 136), scale),
        _scale_point((424, 316), scale),
        _scale_point((392, 348), scale),
        _scale_point((298, 348), scale),
        _scale_point((219, 414), scale),
        _scale_point((219, 348), scale),
        _scale_point((120, 348), scale),
        _scale_point((88, 316), scale),
        _scale_point((88, 136), scale),
    ]
    draw.polygon(bubble, fill=WHITE)
    draw.rounded_rectangle(
        (
            round(88 * scale),
            round(104 * scale),
            round(424 * scale),
            round(348 * scale),
        ),
        radius=round(32 * scale),
        fill=WHITE,
    )

    # Custom A, including a transparent counter.
    draw.polygon(
        [
            _scale_point((130, 300), scale),
            _scale_point((190, 156), scale),
            _scale_point((232, 156), scale),
            _scale_point((292, 300), scale),
            _scale_point((247, 300), scale),
            _scale_point((236, 273), scale),
            _scale_point((184, 273), scale),
            _scale_point((174, 300), scale),
        ],
        fill=BLUE,
    )
    draw.polygon(
        [
            _scale_point((197, 237), scale),
            _scale_point((223, 237), scale),
            _scale_point((210, 197), scale),
        ],
        fill=WHITE,
    )

    # Custom I. Rounded ends keep it distinct at 16px.
    draw.rounded_rectangle(
        (
            round(310 * scale),
            round(156 * scale),
            round(356 * scale),
            round(300 * scale),
        ),
        radius=round(9 * scale),
        fill=VIOLET,
    )

    return image.resize((size, size), Image.Resampling.LANCZOS)


def _save_png(path: Path, size: int, *, rounded_outer: bool, rgb: bool = False) -> None:
    image = _draw_logo(size, rounded_outer=rounded_outer)
    if rgb:
        background = Image.new("RGB", image.size, INK)
        background.paste(image, mask=image.getchannel("A"))
        image = background
    image.save(path, format="PNG", optimize=True)


def _write_svg(path: Path, *, rounded_outer: bool) -> None:
    radius = ' rx="112"' if rounded_outer else ""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-labelledby="title desc">
  <title id="title">AI相談</title>
  <desc id="desc">相談を表す吹き出しとAIの文字を組み合わせたロゴ</desc>
  <rect width="512" height="512"{radius} fill="{INK}"/>
  <path d="M286 0H512V512H406Z" fill="{INK_DEEP}"/>
  <path d="M120 104H392Q424 104 424 136V316Q424 348 392 348H298L219 414V348H120Q88 348 88 316V136Q88 104 120 104Z" fill="{WHITE}"/>
  <path fill="{BLUE}" fill-rule="evenodd" d="M130 300L190 156H232L292 300H247L236 273H184L174 300H130ZM197 237H223L210 197L197 237Z"/>
  <rect x="310" y="156" width="46" height="144" rx="9" fill="{VIOLET}"/>
</svg>
"""
    path.write_text(svg, encoding="utf-8", newline="\n")


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)

    _write_svg(STATIC / "favicon.svg", rounded_outer=True)
    _write_svg(STATIC / "apple-touch-icon.svg", rounded_outer=False)
    shutil.copyfile(STATIC / "favicon.svg", STATIC / f"favicon-{VERSION}.svg")

    for name, size in (
        ("favicon-16x16.png", 16),
        ("favicon-16.png", 16),
        ("icon-16x16.png", 16),
        ("favicon-32x32.png", 32),
        ("favicon-32.png", 32),
        ("favicon.png", 32),
        ("icon-32x32.png", 32),
    ):
        _save_png(STATIC / name, size, rounded_outer=True)

    for name, size in (
        ("apple-touch-icon.png", 180),
        ("icon-192.png", 192),
        ("icon-512.png", 512),
    ):
        _save_png(STATIC / name, size, rounded_outer=False, rgb=True)

    shutil.copyfile(
        STATIC / "apple-touch-icon.png",
        STATIC / f"apple-touch-icon-{VERSION}.png",
    )
    shutil.copyfile(
        STATIC / "favicon-32x32.png",
        STATIC / f"favicon-{VERSION}-32x32.png",
    )
    shutil.copyfile(
        STATIC / "favicon-16x16.png",
        STATIC / f"favicon-{VERSION}-16x16.png",
    )
    shutil.copyfile(STATIC / "icon-192.png", STATIC / f"icon-{VERSION}-192.png")
    shutil.copyfile(STATIC / "icon-512.png", STATIC / f"icon-{VERSION}-512.png")

    ico_source = _draw_logo(256, rounded_outer=True)
    ico_source.save(
        STATIC / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (256, 256)],
    )
    shutil.copyfile(STATIC / "favicon.ico", STATIC / f"favicon-{VERSION}.ico")

    print(f"Generated AI相談 brand icons in {STATIC}")


if __name__ == "__main__":
    main()
