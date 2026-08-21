"""Static pages for AI相談's AIアプリサイト self-build course.

The pages start with a familiar work problem, show what the learner can build,
and use one Square booking destination for the individual course and advice.
"""

from __future__ import annotations

import html
import json
from typing import Final


SITE_BROWSER_TITLE: Final = "AI相談｜一歩踏み出す人のAI講習・実践支援【彦根・滋賀】"


SERVICE_PAGES: Final[dict[str, dict[str, object]]] = {
    "ai-app-site": {
        "name": "AIアプリサイト自作講習・相談",
        "question": "AIアプリサイトを、自分で作れるように。",
        "lead": "作りたいものを相談し、AIへの頼み方、変更の確認、修正、安全な公開まで一緒に進めます。相談だけで終わらず、自分で作って直せる状態を目指す120分です。",
        "price": "11000",
        "price_label": "11,000円 / 120分",
    },
    "ai-estimate": {
        "name": "AI見積もり",
        "label": "見積もり → 自動作成",
        "question": "見積書を毎回30分かけて作っていませんか？",
        "lead": "お客様の入力をもとに金額を計算し、見積書PDFとメールまでつなげる小さなサイトを自分で作ります。",
        "flow": ("入力", "自動計算", "見積PDF", "メール送信"),
        "outcome": "計算・転記・送付の往復を減らし、確認に時間を使えるようにします。",
        "price": "11000",
        "price_label": "自作講習・相談 11,000円 / 120分",
    },
    "ai-inquiry": {
        "name": "AI問い合わせ",
        "label": "問い合わせ → AI回答",
        "question": "同じ質問への返信に、毎日時間を取られていませんか？",
        "lead": "よくある質問、商品、サービス情報を整理し、答えられることと人へ渡すことを分けるサイトを自分で作ります。",
        "flow": ("質問を受ける", "情報を確認", "AIが回答案", "人へ引き継ぐ"),
        "outcome": "返信を速くしながら、例外や大事な相談は人が判断できる流れにします。",
        "price": "11000",
        "price_label": "自作講習・相談 11,000円 / 120分",
    },
    "ai-reservation": {
        "name": "AI予約受付",
        "label": "予約 → 自動受付",
        "question": "予約の確認、返信、台帳更新を何度もしていませんか？",
        "lead": "予約フォーム、通知、顧客メモをつなぎ、受付後に必要な確認だけが残る流れを自分で作ります。",
        "flow": ("予約入力", "空きを確認", "自動通知", "顧客メモ"),
        "outcome": "予約の取りこぼしを減らし、来店・支援・授業の準備に時間を戻します。",
        "price": "11000",
        "price_label": "自作講習・相談 11,000円 / 120分",
    },
    "ai-shift": {
        "name": "AIシフト",
        "label": "シフト → 自動作成",
        "question": "希望を集めて、条件を見ながらシフトを組むのが重くなっていませんか？",
        "lead": "希望日、必要人数、役割、守る条件を整理し、たたき台を早く作れるサイトを自分で作ります。",
        "flow": ("希望を集める", "条件を確認", "案を作る", "人が確定"),
        "outcome": "公平さや現場事情の判断は残し、組み始める前の作業を短くします。",
        "price": "11000",
        "price_label": "自作講習・相談 11,000円 / 120分",
    },
    "ai-blog": {
        "name": "AIブログ",
        "label": "ブログ → AI下書き",
        "question": "伝えたいことはあるのに、記事やSNSの文章まで手が回っていませんか？",
        "lead": "会議メモ、写真、キーワードから記事の下書きとSNS用の短文を作り、最後は人が整えるサイトを自分で作ります。",
        "flow": ("素材を集める", "下書きを作る", "人が確認", "SNSへ再編集"),
        "outcome": "発信を止めにくくし、現場で得た学びを事業の資産として残します。",
        "price": "11000",
        "price_label": "自作講習・相談 11,000円 / 120分",
    },
}

SOLUTION_ORDER: Final[tuple[str, ...]] = (
    "ai-estimate",
    "ai-inquiry",
    "ai-reservation",
    "ai-shift",
    "ai-blog",
)

SELFBUILD_STEPS: Final[tuple[tuple[str, str, str, str], ...]] = (
    ("STEP 1", "相談して絞る", "目的", "誰のどの悩みを解決するか、一機能まで絞る"),
    ("STEP 2", "AIへ頼んで作る", "実装", "目的、完成形、守る条件を伝え、小さく動かす"),
    ("STEP 3", "自分で確かめて直す", "確認・修正", "差分、画面、リンク、入力、エラーを確認する"),
    ("STEP 4", "公開して手順を残す", "本番・再利用", "PC・スマホと本番URLを確認し、次の修正を残す"),
)


APP_SITE_CSS: Final = r"""
:root {
  --app-ink: #10243c;
  --app-muted: #52647a;
  --app-blue: #1c5fbd;
  --app-teal: #007b74;
  --app-pale: #edf5ff;
  --app-line: #c9d9ea;
  --app-white: #ffffff;
  --app-shadow: 0 18px 46px rgba(21, 58, 100, .13);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
.app-site-page { margin: 0; background: #f8fbff; color: var(--app-ink); font-family: Inter, "Noto Sans JP", sans-serif; }
.app-site-page main { display: block; }
.app-site-shell { width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
.app-site-main { padding: 98px 0 72px; overflow: hidden; }
.app-site-eyebrow { margin: 0 0 12px; color: var(--app-blue); font-size: 12px; font-weight: 900; letter-spacing: .12em; }
.app-site-page h1, .app-site-page h2, .app-site-page h3, .app-site-page p { overflow-wrap: anywhere; }
.app-site-page h1 { margin: 0; max-width: 760px; font-size: clamp(35px, 5.2vw, 68px); line-height: 1.16; letter-spacing: -.04em; }
.app-site-page h1 span { display: block; color: var(--app-blue); font-size: clamp(16px, 2vw, 22px); letter-spacing: .01em; }
.app-site-page h2 { margin: 0; font-size: clamp(28px, 4vw, 46px); line-height: 1.25; letter-spacing: -.025em; }
.app-site-page h3 { margin: 0; font-size: 20px; line-height: 1.4; }
.app-site-page p { color: var(--app-muted); line-height: 1.85; }
.app-site-page a { color: inherit; }
.app-site-hero { position: relative; overflow: hidden; padding: 64px 0 52px; background: linear-gradient(135deg, #eaf4ff 0%, #f8fcff 48%, #e7f8f4 100%); border-bottom: 1px solid var(--app-line); }
.app-site-hero::before { position: absolute; inset: auto -8% -120px auto; width: 330px; height: 330px; border-radius: 50%; background: rgba(33, 120, 206, .13); content: ""; filter: blur(1px); }
.app-site-hero__grid { position: relative; display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(320px, .95fr); gap: 44px; align-items: center; }
.app-site-hero__lead { margin: 24px 0 0; max-width: 690px; font-size: clamp(16px, 1.65vw, 19px); }
.app-site-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 26px; }
.app-site-button { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; padding: 12px 18px; border: 1px solid var(--app-blue); border-radius: 12px; background: var(--app-blue); color: #fff !important; font-size: 15px; font-weight: 900; line-height: 1.3; text-align: center; text-decoration: none; box-shadow: 0 8px 20px rgba(28, 95, 189, .22); }
.app-site-button:hover, .app-site-button:focus-visible { transform: translateY(-1px); background: #124b98; }
.app-site-button--secondary { background: #fff; color: var(--app-blue) !important; box-shadow: none; }
.app-site-button--secondary:hover, .app-site-button--secondary:focus-visible { background: #edf5ff; }
.app-site-trust { display: flex; flex-wrap: wrap; gap: 8px 15px; margin: 20px 0 0; padding: 0; list-style: none; color: var(--app-muted); font-size: 13px; font-weight: 800; }
.app-site-trust li::before { margin-right: 6px; color: var(--app-teal); content: "✓"; }
.app-site-screen { position: relative; min-height: 418px; padding: 16px; border: 1px solid #b9cee5; border-radius: 24px; background: #fff; box-shadow: var(--app-shadow); transform: rotate(1deg); }
.app-site-screen__bar { display: flex; align-items: center; gap: 6px; padding: 0 0 13px; border-bottom: 1px solid #dce8f4; }
.app-site-screen__bar i { width: 9px; height: 9px; border-radius: 50%; background: #a7bdd3; }
.app-site-screen__bar strong { margin-left: 6px; color: var(--app-muted); font-size: 11px; letter-spacing: .08em; }
.app-site-screen__main { margin-top: 16px; padding: 18px; border-radius: 16px; background: linear-gradient(145deg, #f1f7ff, #f7fffc); }
.app-site-screen__main small { display: block; color: var(--app-teal); font-size: 10px; font-weight: 900; letter-spacing: .12em; }
.app-site-screen__main b { display: block; margin-top: 9px; font-size: clamp(25px, 3vw, 36px); line-height: 1.25; letter-spacing: -.04em; }
.app-site-screen__main p { margin: 10px 0 0; font-size: 13px; line-height: 1.65; }
.app-site-screen__cards { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; margin-top: 14px; }
.app-site-screen__card { min-width: 0; padding: 11px; border: 1px solid #d5e3f0; border-radius: 12px; background: #fff; }
.app-site-screen__card b { display: block; font-size: 13px; }
.app-site-screen__card span { display: block; margin-top: 4px; color: var(--app-teal); font-size: 11px; font-weight: 800; }
.app-site-section { padding: 78px 0; }
.app-site-section--soft { background: #edf6ff; }
.app-site-section--white { background: #fff; }
.app-site-section__head { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, .68fr); gap: 32px; align-items: end; }
.app-site-section__head p { margin: 0; }
.app-site-section__lead { max-width: 680px; margin: 16px 0 0; font-size: 16px; }
.app-solution-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-top: 32px; }
.app-solution-card { display: flex; min-width: 0; min-height: 214px; flex-direction: column; padding: 18px; border: 1px solid var(--app-line); border-radius: 16px; background: #fff; text-decoration: none; transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
.app-solution-card:hover, .app-solution-card:focus-visible { border-color: var(--app-blue); box-shadow: 0 12px 30px rgba(28, 95, 189, .13); transform: translateY(-3px); }
.app-solution-card__mark { display: inline-flex; width: 32px; height: 32px; align-items: center; justify-content: center; border-radius: 10px; background: #e4f0ff; color: var(--app-blue); font-size: 12px; font-weight: 950; }
.app-solution-card h3 { margin-top: 14px; font-size: 17px; }
.app-solution-card p { margin: 7px 0 0; font-size: 13px; line-height: 1.65; }
.app-solution-card small { margin-top: auto; padding-top: 14px; color: var(--app-blue); font-size: 12px; font-weight: 900; }
.app-product-steps { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 32px 0 0; }
.app-product-step { min-width: 0; padding: 17px 14px; border: 1px solid var(--app-line); border-radius: 14px; background: #fff; }
.app-product-step small { display: block; color: var(--app-blue); font-size: 10px; font-weight: 900; letter-spacing: .08em; }
.app-product-step h3 { margin-top: 8px; font-size: 16px; }
.app-product-step strong { display: block; margin-top: 12px; color: var(--app-teal); font-size: 15px; }
.app-product-step p { margin: 8px 0 0; font-size: 12px; line-height: 1.65; }
.app-flow { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 15px; margin-top: 32px; }
.app-flow article { position: relative; min-width: 0; padding: 20px; border-left: 3px solid var(--app-teal); border-radius: 0 14px 14px 0; background: #fff; }
.app-flow b { display: block; color: var(--app-blue); font-size: 12px; letter-spacing: .08em; }
.app-flow h3 { margin-top: 10px; font-size: 18px; }
.app-flow p { margin: 7px 0 0; font-size: 13px; }
.app-case { display: grid; grid-template-columns: minmax(0, 1fr) minmax(280px, .85fr); gap: 28px; margin-top: 32px; padding: 26px; border-radius: 18px; background: #10243c; color: #fff; }
.app-case p { color: #dce9f7; }
.app-case__numbers { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 9px; align-content: start; }
.app-case__numbers div { min-width: 0; padding: 15px 10px; border-radius: 12px; background: rgba(255,255,255,.1); text-align: center; }
.app-case__numbers small { display: block; color: #b8d2ec; font-size: 10px; font-weight: 800; }
.app-case__numbers strong { display: block; margin-top: 7px; color: #fff; font-size: 21px; overflow-wrap: anywhere; }
.app-free-sheet { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 22px; align-items: center; margin-top: 30px; padding: 24px; border: 1px solid #b8d8d2; border-radius: 18px; background: #f2fbf8; }
.app-free-sheet h3 { color: var(--app-teal); }
.app-free-sheet p { margin: 8px 0 0; }
.app-faq { max-width: 880px; margin: 30px auto 0; }
.app-faq details { border-bottom: 1px solid var(--app-line); padding: 17px 0; }
.app-faq summary { cursor: pointer; color: var(--app-ink); font-weight: 900; line-height: 1.55; }
.app-faq p { margin: 10px 0 0; font-size: 14px; }
.app-cta-band { padding: 68px 0; background: linear-gradient(120deg, #0f3156, #126d72); color: #fff; }
.app-cta-band p { color: #d9f0ef; }
.app-cta-band .app-site-button { border-color: #fff; background: #fff; color: #0f3156 !important; box-shadow: none; }
.app-cta-band .app-site-button:hover, .app-cta-band .app-site-button:focus-visible { background: #e7fbfa; }
.app-site-footer { padding: 26px 0 42px; background: #0b1c31; color: #dce9f7; }
.app-site-footer a { color: #fff; font-weight: 800; }
.app-site-footer p { margin: 8px 0 0; color: #b9cce0; font-size: 12px; }
.app-solution-hero { padding: 52px 0 42px; background: linear-gradient(140deg, #eaf4ff, #f8fcff 58%, #e7f8f4); border-bottom: 1px solid var(--app-line); }
.app-solution-hero__grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, .72fr); gap: 30px; align-items: center; }
.app-flow-line { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); overflow: hidden; border: 1px solid var(--app-line); border-radius: 16px; background: #fff; }
.app-flow-line div { position: relative; min-width: 0; padding: 18px 14px; text-align: center; }
.app-flow-line div + div::before { position: absolute; top: 50%; left: -6px; color: var(--app-blue); content: "→"; font-weight: 900; transform: translateY(-50%); }
.app-flow-line small { display: block; color: var(--app-muted); font-size: 11px; }
.app-flow-line strong { display: block; margin-top: 6px; font-size: 15px; }
.app-solution-outcome { padding: 22px; border-radius: 15px; background: #fff; box-shadow: var(--app-shadow); }
.app-solution-outcome small { color: var(--app-teal); font-weight: 900; letter-spacing: .08em; }
.app-solution-outcome p { margin: 8px 0 0; }
.app-page-note { margin: 22px 0 0; color: var(--app-muted); font-size: 12px; }
.app-site-page :where(a, button, summary):focus-visible { outline: 3px solid #ffb703; outline-offset: 3px; }
@media (max-width: 1000px) {
  .app-solution-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .app-product-steps { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .app-site-shell { width: min(100% - 28px, 560px); }
  .app-site-main { padding-top: 76px; }
  .app-site-hero { padding: 38px 0; }
  .app-site-hero__grid, .app-site-section__head, .app-case, .app-free-sheet, .app-solution-hero__grid { grid-template-columns: 1fr; gap: 22px; }
  .app-site-hero h1 { font-size: clamp(34px, 10vw, 48px); }
  .app-site-screen { min-height: auto; transform: none; }
  .app-site-section { padding: 54px 0; }
  .app-solution-grid, .app-product-steps, .app-flow { grid-template-columns: 1fr; }
  .app-solution-card { min-height: 0; }
  .app-product-step { padding: 16px; }
  .app-case__numbers { grid-template-columns: 1fr 1fr 1fr; }
  .app-free-sheet .app-site-button { width: 100%; }
  .app-flow-line { grid-template-columns: 1fr; }
  .app-flow-line div + div::before { top: -11px; left: 50%; transform: translateX(-50%) rotate(90deg); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
}
"""


def _safe(value: object) -> str:
    return html.escape(str(value), quote=True)


def _page_head(
    page: dict[str, object],
    site_url: str,
    favicon_html: str,
    shared_header_css: str,
    selfbuild_book_url: str,
) -> str:
    base_url = site_url.rstrip("/")
    slug = str(page["slug"])
    canonical_url = f"{base_url}/{slug}/"
    name = str(page["name"])
    description = str(page["lead"])
    schema = {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": name,
        "description": description,
        "inLanguage": "ja",
        "url": canonical_url,
        "areaServed": {"@type": "AdministrativeArea", "name": "滋賀県"},
        "provider": {"@type": "Organization", "name": "AI相談", "url": base_url},
        "offers": {
            "@type": "Offer",
            "price": str(page["price"]),
            "priceCurrency": "JPY",
            "availability": "https://schema.org/InStock",
            "url": selfbuild_book_url,
        },
    }
    return "".join(
        (
            "<!doctype html><html lang='ja'><head><meta charset='utf-8'>",
            favicon_html,
            "<meta name='viewport' content='width=device-width,initial-scale=1'>",
            "<meta name='theme-color' content='#0f3156'>",
            f"<title>{_safe(SITE_BROWSER_TITLE)}</title>",
            f"<meta name='description' content='{_safe(description)}'>",
            f"<link rel='canonical' href='{_safe(canonical_url)}'>",
            "<meta property='og:type' content='website'>",
            "<meta property='og:locale' content='ja_JP'>",
            "<meta property='og:site_name' content='AI相談'>",
            f"<meta property='og:title' content='{_safe(name)}｜AI相談'>",
            f"<meta property='og:description' content='{_safe(description)}'>",
            f"<meta property='og:url' content='{_safe(canonical_url)}'>",
            "<meta name='twitter:card' content='summary_large_image'>",
            "<link rel='preconnect' href='https://fonts.googleapis.com'>",
            "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>",
            "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Noto+Sans+JP:wght@400;500;600;700;800;900&display=swap'>",
            f"<style>{shared_header_css}{APP_SITE_CSS}</style>",
            f"<script type='application/ld+json'>{json.dumps(schema, ensure_ascii=False)}</script>",
            "</head><body class='app-site-page'>",
        )
    )


def _booking_button(selfbuild_book_url: str, label: str = "自作講習・相談を予約する") -> str:
    return (
        f"<a class='app-site-button' href='{_safe(selfbuild_book_url)}' "
        f"target='_blank' rel='noopener'>{_safe(label)} <span aria-hidden='true'>→</span></a>"
    )


def _service_visual() -> str:
    cards = (
        ("見積もり", "自動作成"),
        ("予約", "自動受付"),
        ("問い合わせ", "AI回答"),
        ("ブログ", "AI下書き"),
        ("シフト", "自動作成"),
        ("報告書", "PDF生成"),
    )
    card_html = "".join(
        f"<div class='app-site-screen__card'><b>{_safe(name)}</b><span>→ {_safe(result)}</span></div>"
        for name, result in cards
    )
    return (
        "<aside class='app-site-screen' aria-label='AIアプリサイトで楽になる仕事の例'>"
        "<div class='app-site-screen__bar'><i></i><i></i><i></i><strong>AI APP SITE</strong></div>"
        "<div class='app-site-screen__main'><small>相談しながら自分で作る</small>"
        "<b>AIアプリサイトを、<br>自分の仕事の道具に。</b>"
        "<p>AIへ頼み、人が確認し、自分で直して公開します。</p></div>"
        f"<div class='app-site-screen__cards'>{card_html}</div></aside>"
    )


def _solution_cards() -> str:
    cards: list[str] = []
    for index, slug in enumerate(SOLUTION_ORDER, start=1):
        page = SERVICE_PAGES[slug]
        cards.append(
            f"<a class='app-solution-card' href='/{_safe(slug)}/'>"
            f"<span class='app-solution-card__mark'>{index:02d}</span>"
            f"<h3>{_safe(page['name'])}</h3>"
            f"<p>{_safe(page['label'])}</p>"
            "<small>できることを見る →</small></a>"
        )
    return "<div class='app-solution-grid'>" + "".join(cards) + "</div>"


def _selfbuild_steps() -> str:
    items = "".join(
        "<article class='app-product-step'>"
        f"<small>{_safe(step)}</small><h3>{_safe(name)}</h3>"
        f"<strong>{_safe(price)}</strong><p>{_safe(summary)}</p></article>"
        for step, name, price, summary in SELFBUILD_STEPS
    )
    return "<div class='app-product-steps' aria-label='AIアプリサイトを自作する4つの手順'>" + items + "</div>"


def _main_page(
    page: dict[str, object],
    nav_html: str,
    selfbuild_book_url: str,
) -> str:
    return "".join(
        (
            "<a class='skip-link' href='#ai-app-site-main'>本文へ移動</a>",
            nav_html,
            "<main id='ai-app-site-main'>",
            "<section class='app-site-hero'><div class='app-site-shell app-site-hero__grid'>",
            "<div><p class='app-site-eyebrow'>AI APP SITE · SELF BUILD</p>",
            "<h1>AIアプリサイトを、<br>自分で作れるように。</h1>",
            f"<p class='app-site-hero__lead'>{_safe(page['lead'])}</p>",
            "<div class='app-site-actions'>",
            _booking_button(selfbuild_book_url, "AIアプリサイト自作講習・相談を予約する"),
            "<a class='app-site-button app-site-button--secondary' href='#services'>自作できる例を見る</a></div>",
            "<ul class='app-site-trust'><li>120分・11,000円</li><li>個別対応</li><li>対面・オンライン</li></ul></div>",
            _service_visual(),
            "</div></section>",
            "<section class='app-site-section app-site-section--white' id='services'><div class='app-site-shell'>",
            "<div class='app-site-section__head'><div><p class='app-site-eyebrow'>WHAT YOU CAN BUILD</p>"
            "<h2>専門用語より先に、<br>減らしたい手作業から始めます。</h2></div>"
            "<p>見積もり、返信、予約、集計、発信から最初の一つを選びます。完成品を渡すだけでなく、作る途中の判断も一緒に確認します。</p></div>",
            _solution_cards(),
            "</div></section>",
            "<section class='app-site-section app-site-section--soft'><div class='app-site-shell'>",
            "<p class='app-site-eyebrow'>120 MINUTES</p><h2>相談 → 小さく作る → 自分で直す → 公開する</h2>"
            "<p class='app-site-section__lead'>個別講習・相談は120分11,000円です。作りたいものを一つに絞り、AIへの依頼、確認、修正、安全な公開を同じ題材で通します。</p>",
            _selfbuild_steps(),
            "</div></section>",
            "<section class='app-site-section app-site-section--white'><div class='app-site-shell'>",
            "<p class='app-site-eyebrow'>WHAT YOU TAKE HOME</p><h2>完成だけでなく、次に自分で直せる手順を残します。</h2>"
            "<div class='app-flow'><article><b>01 / PLAN</b><h3>短い仕様</h3><p>誰が何に使うか、完成形と守る条件を一枚にします。</p></article>"
            "<article><b>02 / PROMPT</b><h3>AIへの依頼文</h3><p>同じ進め方を次回も使えるように、目的と確認項目を残します。</p></article>"
            "<article><b>03 / CHECK</b><h3>公開前チェック</h3><p>画面、リンク、入力、エラー、秘密情報の確認手順を残します。</p></article>"
            "<article><b>04 / NEXT</b><h3>次の修正</h3><p>今回できたことと、次に足す一機能を分けて記録します。</p></article></div>",
            "<div class='app-case'><div><p class='app-site-eyebrow'>THE GOAL</p><h3>自分で確認し、直し、公開できる。</h3>"
            "<p>AIに全部任せるのではなく、AIが変えた場所と本番の結果を自分で確かめられる状態を目指します。</p></div>"
            "<div class='app-case__numbers' aria-label='講習で身につける三つの力'><div><small>PLAN</small><strong>頼める</strong></div><div><small>CHECK</small><strong>直せる</strong></div><div><small>SHIP</small><strong>公開できる</strong></div></div></div>",
            "</div></section>",
            "<section class='app-site-section app-site-section--soft'><div class='app-site-shell'>",
            "<p class='app-site-eyebrow'>BRING YOUR PROJECT</p><h2>作りたいものが曖昧でも大丈夫です。</h2>"
            "<p class='app-site-section__lead'>普段使っているExcel、紙、LINE、予約表、既存サイトを見ながら、120分で完成を目指せる一機能へ絞ります。</p>"
            "<div class='app-free-sheet'><div><h3>用意するのは、たった3つです。</h3><p>減らしたい作業／今の手順が分かる資料・URL／WindowsまたはMacのPC。専門用語や完成した仕様書は不要です。</p></div>"
            "<div class='app-site-actions'><a class='app-site-button app-site-button--secondary' href='/lectures/2026-08-ai-app-site-consult-sheet.html'>準備シートを見る</a>"
            + _booking_button(selfbuild_book_url, "自作講習・相談の日程を見る")
            + "</div></div></div></section>",
            "<section class='app-site-section app-site-section--white'><div class='app-site-shell'><p class='app-site-eyebrow'>FAQ</p><h2>よくある質問</h2><div class='app-faq'>"
            "<details><summary>AIやコードが初めてでも参加できますか？</summary><p>参加できます。専門用語からではなく、減らしたい作業と今の手順から始めます。</p></details>"
            "<details><summary>120分でどこまでできますか？</summary><p>一機能に絞り、相談、作成、確認、修正、公開までを目指します。外部連携や認証など規模が大きい場合は、動く試作と次の手順まで進めます。</p></details>"
            "<details><summary>何を持っていけばよいですか？</summary><p>PC、作りたいものや直したいページ、今の手順が分かる資料・URLをお持ちください。秘密情報は講習用資料へ入れません。</p></details>"
            "<details><summary>一人で続けるのが不安です。</summary><p>次の修正と確認手順まで残します。複数業務を継続して仕組み化する場合は、6ヶ月伴走も選べます。</p></details>"
            "</div></div></section></main>",
            "<section class='app-cta-band'><div class='app-site-shell'><p class='app-site-eyebrow'>BUILD ONE THING</p><h2>相談だけで終わらず、<br>自分で作って直せるように。</h2><p>最初の一機能を、120分の個別講習・相談で一緒に動かします。</p>",
            _booking_button(selfbuild_book_url, "AIアプリサイト自作講習・相談を予約する"),
            "</div></section>",
            _footer(),
        )
    )


def _solution_page(
    page: dict[str, object],
    nav_html: str,
    selfbuild_book_url: str,
) -> str:
    flow = tuple(page["flow"])
    flow_html = "".join(
        f"<div><small>STEP {index:02d}</small><strong>{_safe(label)}</strong></div>"
        for index, label in enumerate(flow, start=1)
    )
    related = "".join(
        f"<a class='app-solution-card' href='/{_safe(slug)}/'><span class='app-solution-card__mark'>{index:02d}</span>"
        f"<h3>{_safe(SERVICE_PAGES[slug]['name'])}</h3><p>{_safe(SERVICE_PAGES[slug]['label'])}</p>"
        "<small>できることを見る →</small></a>"
        for index, slug in enumerate((item for item in SOLUTION_ORDER if item != page["slug"]), start=1)
    )
    return "".join(
        (
            "<a class='skip-link' href='#solution-main'>本文へ移動</a>",
            nav_html,
            "<main id='solution-main' class='app-site-main'>",
            "<section class='app-solution-hero'><div class='app-site-shell app-solution-hero__grid'><div>",
            "<p class='app-site-eyebrow'>AI APP SITE · SELF BUILD</p>",
            f"<h1><span>{_safe(page['name'])}</span>{_safe(page['question'])}</h1>",
            f"<p class='app-site-hero__lead'>{_safe(page['lead'])}</p>",
            "<div class='app-site-actions'>",
            _booking_button(selfbuild_book_url, "このAIアプリサイトを自作する"),
            "<a class='app-site-button app-site-button--secondary' href='/ai-app-site/'>自作講習・相談の全体を見る</a></div></div>",
            "<aside class='app-solution-outcome'><small>目指すこと</small>"
            f"<h3>{_safe(page['label'])}</h3><p>{_safe(page['outcome'])}</p>"
            f"<p><b>{_safe(page['price_label'])}</b>で、一機能の相談から公開まで進めます。</p></aside>",
            "</div></section>",
            "<section class='app-site-section app-site-section--white'><div class='app-site-shell'><p class='app-site-eyebrow'>WORKFLOW</p>"
            "<h2>今の流れを、確認しやすい形へ。</h2><p class='app-site-section__lead'>人の判断をなくすのではなく、入力・転記・確認待ちを減らし、大事な例外は人へ渡せるようにします。</p>"
            f"<div class='app-flow-line' aria-label='{_safe(page['name'])}の基本フロー'>{flow_html}</div>"
            "</div></section>",
            "<section class='app-site-section app-site-section--soft'><div class='app-site-shell'><p class='app-site-eyebrow'>120 MINUTES</p>"
            "<h2>相談しながら作り、自分で確かめて公開します。</h2>"
            "<div class='app-flow'><article><b>01</b><h3>今の資料を見る</h3><p>使っているExcel、紙、フォーム、URLをそのまま確認します。</p></article>"
            "<article><b>02</b><h3>困る場面を決める</h3><p>毎月、毎週、毎回どこで時間が止まるかを一つ選びます。</p></article>"
            "<article><b>03</b><h3>小さく試す範囲を決める</h3><p>人が確認する場所を残し、最初に作る一機能を決めます。</p></article>"
            "<article><b>04</b><h3>公開して手順を残す</h3><p>PC・スマホと本番URLを確認し、次に直す場所を残します。</p></article></div>"
            "<div class='app-site-actions'>" + _booking_button(selfbuild_book_url, "自作講習・相談の日程を見る") + "</div></div></section>",
            "<section class='app-site-section app-site-section--white'><div class='app-site-shell'><p class='app-site-eyebrow'>OTHER OPTIONS</p>"
            "<h2>ほかに、どの仕事をAI化しますか？</h2><div class='app-solution-grid'>" + related + "</div></div></section>",
            "</main>",
            "<section class='app-cta-band'><div class='app-site-shell'><p class='app-site-eyebrow'>BUILD ONE THING</p><h2>一つの作業から、<br>自分のAIアプリサイトへ。</h2>"
            "<p>AIが初めてでも、PCと今の資料を持ってくるだけで大丈夫です。</p>" + _booking_button(selfbuild_book_url, "自作講習・相談を予約する") + "</div></section>",
            _footer(),
        )
    )


def _footer() -> str:
    return (
        "<footer class='app-site-footer'><div class='app-site-shell'><a href='/'>AI相談トップへ戻る</a>"
        "<p>AI相談｜彦根・滋賀のAI講習、業務改善、AIアプリサイト</p></div></footer></body></html>"
    )


def render_ai_app_site_page(
    slug: str,
    site_url: str,
    nav_html: str,
    favicon_html: str,
    shared_header_css: str,
    selfbuild_book_url: str,
) -> str:
    """Render one customer-facing AIアプリサイト page."""
    if slug not in SERVICE_PAGES:
        raise ValueError(f"Unknown AI app site route: {slug}")
    page = {**SERVICE_PAGES[slug], "slug": slug}
    document = _page_head(page, site_url, favicon_html, shared_header_css, selfbuild_book_url)
    if slug == "ai-app-site":
        return document + _main_page(page, nav_html, selfbuild_book_url)
    return document + _solution_page(page, nav_html, selfbuild_book_url)


def render_all_ai_app_site_pages(
    site_url: str,
    nav_html: str,
    favicon_html: str,
    shared_header_css: str,
    selfbuild_book_url: str,
) -> dict[str, str]:
    """Render the flagship page and all solution-specific landing pages."""
    return {
        slug: render_ai_app_site_page(
            slug,
            site_url,
            nav_html,
            favicon_html,
            shared_header_css,
            selfbuild_book_url,
        )
        for slug in SERVICE_PAGES
    }
