"""Refresh homepage artwork and shorten course cards without changing their content."""
from pathlib import Path
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = "/design-system/studio/images/editorial-20261011/"
ART = {
    "soft-hero": ("hero", "相談者と制作者が、資料から案内と予約ページを一緒に作るイラスト"),
    "soft-agent": ("agent", "お店の人が商品写真から案内を作るイラスト"),
    "soft-personal": ("personal", "相談者と講師が、取り組む課題を一つ選ぶイラスト"),
    "soft-code": ("code", "制作者がコードと予約フォームを見比べ、スマートフォンで確かめるイラスト"),
    "soft-support": ("support", "小さなチームが仕事の手順と進み具合を一緒に整えるイラスト"),
    "soft-salon": ("salon", "参加者がオンラインで話しながら作ったものを見せ合うイラスト"),
    "soft-site": ("site", "お店の人と制作者がホームページと予約画面を組み立てるイラスト"),
    "lesson-agent": ("agent", "商品写真から案内を作る手順を学ぶイラスト"),
    "lesson-practice": ("practice", "メモから今日取り組む小さな計画を作るイラスト"),
    "lesson-rag": ("rag", "資料の根拠を探し、AIの回答と照らし合わせるイラスト"),
    "lesson-site": ("site", "ホームページと予約画面の作り方を学ぶイラスト"),
    "lesson-salon": ("salon", "オンラインで作品や工夫を共有するイラスト"),
    "lesson-climbing": ("climbing", "クライミングの動きや歴史を伝える資料を作るイラスト"),
    "lesson-coding": ("code", "コードと実際の画面を見比べて学ぶイラスト"),
    "soft-prepare": ("personal", "相談者と講師が持ち寄った課題を一つ選ぶイラスト"),
    "soft-bring": ("personal", "相談者と講師が持ち寄った課題を一つ選ぶイラスト"),
    "soft-try": ("site", "お店の案内と予約画面を一緒に試作するイラスト"),
    "soft-keep": ("practice", "作った手順を日々の小さな計画に残すイラスト"),
}


def replace_home_art(document):
    def replace(match):
        tag = BeautifulSoup(match[0], "html.parser").img
        src = tag.get("src", "").split("?", 1)[0]
        if not src.startswith("/design-system/studio/images/"):
            return match[0]
        key = Path(src).stem
        if key not in ART:
            return match[0]
        asset, description = ART[key]
        tag["src"] = IMAGE_ROOT + asset + ".webp"
        tag["alt"] = description
        tag["width"], tag["height"] = "1536", "1024"
        tag["decoding"] = "async"
        return str(tag)
    return re.sub(r"<img\b[^>]*>", replace, document, flags=re.S | re.I)


def compact_courses(document):
    def replace(match):
        soup = BeautifulSoup(match[0], "html.parser")
        card = soup.article
        if card.get("data-editorial-course") == "20261011":
            return match[0]
        image = card.select_one(":scope > .compact-course-visual")
        body = card.select_one(":scope > .studio-course-body")
        role = card.select_one(":scope > .offer-role-row")
        if image is None or body is None:
            raise ValueError("Course card is missing its image or body")
        heading = body.select_one(":scope > .compact-course-heading")
        meta = body.select_one(":scope > .compact-course-meta")
        if heading is None or meta is None:
            raise ValueError("Course card is missing its name or price")
        lead = soup.new_tag("div", attrs={"class": "editorial-course-lead"})
        if role is not None:
            lead.append(role.extract())
        lead.append(heading.extract())
        lead.append(meta.extract())
        image.insert_after(lead)
        card["data-editorial-course"] = "20261011"
        return str(card)
    return re.sub(
        r'<article\b[^>]*class=["\'][^"\']*\bcompact-course-card\b[^"\']*["\'][^>]*>.*?</article>',
        replace, document, flags=re.S,
    )


def apply_editorial_home(document, css=None):
    document = compact_courses(replace_home_art(document))
    css = css if css is not None else (ROOT / "site/templates/ai-news/editorial-home.css").read_text(encoding="utf-8")
    style = '<style id="editorial-home-style">' + css + "</style>"
    pattern = r'<style\b[^>]*id=["\']editorial-home-style["\'][^>]*>.*?</style>'
    document = re.sub(pattern, "", document, flags=re.S)
    if document.count("</head>") != 1:
        raise ValueError("Expected one document head")
    return document.replace("</head>", style + "</head>")
