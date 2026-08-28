"""Static renderer for the public SEO and LLMO diagnosis page."""

from __future__ import annotations

import html
import json


SITE_BROWSER_TITLE = "AI相談｜一歩踏み出す人のAI講習・実践支援【彦根・滋賀】"


def render_seo_llmo_diagnosis_page(
    site_url: str,
    nav_html: str,
    favicon_html: str,
    shared_header_css: str,
) -> str:
    """Return the standalone, progressively enhanced public diagnosis page."""
    base_url = site_url.rstrip("/")
    canonical_url = f"{base_url}/seo-llmo-diagnosis/"
    description = (
        "公開URLを入れて約1分。検索とAIに伝わる土台を100点・4領域で確認し、"
        "優先して直す項目がわかる無料のSEO・LLMO診断です。"
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "SEO・LLMO診断",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Any",
        "inLanguage": "ja",
        "isAccessibleForFree": True,
        "url": canonical_url,
        "description": description,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "publisher": {"@type": "Organization", "name": "AI相談", "url": base_url},
    }

    return "".join(
        [
            "<!doctype html><html lang='ja'><head><meta charset='utf-8'>",
            favicon_html,
            "<meta name='viewport' content='width=device-width,initial-scale=1'>",
            "<meta name='theme-color' content='#f7f9fc'>",
            f"<title>{html.escape(SITE_BROWSER_TITLE)}</title>",
            f"<meta name='description' content='{html.escape(description, quote=True)}'>",
            f"<link rel='canonical' href='{html.escape(canonical_url, quote=True)}'>",
            "<meta property='og:type' content='website'>",
            "<meta property='og:locale' content='ja_JP'>",
            "<meta property='og:site_name' content='AI相談'>",
            "<meta property='og:title' content='SEO・LLMO診断｜検索とAIに伝わる土台を確認'>",
            f"<meta property='og:description' content='{html.escape(description, quote=True)}'>",
            f"<meta property='og:url' content='{html.escape(canonical_url, quote=True)}'>",
            "<meta name='twitter:card' content='summary'>",
            "<link rel='preconnect' href='https://fonts.googleapis.com'>",
            "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>",
            "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Noto+Sans+JP:wght@400;500;600;700;800;900&display=swap'>",
            "<link rel='stylesheet' href='/seo-llmo-diagnosis/styles.css'>",
            f"<style>{shared_header_css}</style>",
            f"<script type='application/ld+json'>{json.dumps(schema, ensure_ascii=False)}</script>",
            "</head><body class='seo-diagnosis-page'>",
            "<a class='skip-link' href='#seo-audit-form'>診断フォームへ移動</a>",
            nav_html,
            "<main data-audit-endpoint='/api/seo-llmo-audit' data-relay-endpoint='/api/admin/command-center/relay'>",
            "<section class='audit-start' aria-labelledby='audit-title'><div class='audit-shell audit-start__inner'>",
            "<header class='audit-start__head'>",
            "<p class='audit-eyebrow'>URLを入れて約1分</p>",
            "<h1 id='audit-title'>あなたのサイト診断</h1>",
            "<p>公開URLを入れるだけ。まず直す場所をすぐに整理します。</p>",
            "</header>",
            "<div class='audit-form-card'>",
            "<form id='seo-audit-form'>",
            "<label class='audit-field audit-field--url' for='audit-url'><span>公開URL <b>必須</b></span>"
            "<input id='audit-url' name='url' type='url' inputmode='url' autocomplete='url' placeholder='https://example.com/' required maxlength='2048'></label>",
            "<details class='audit-context-details'>",
            "<summary>精度を上げる情報（任意）</summary>",
            "<div class='audit-context-grid'>",
            "<label class='audit-field' for='audit-audience'><span>主に誰へ届けたいですか</span>"
            "<input id='audit-audience' name='audience' type='text' maxlength='160' placeholder='例：彦根の小規模事業者'></label>",
            "<label class='audit-field' for='audit-problem'><span>その人の悩みは何ですか</span>"
            "<input id='audit-problem' name='problem' type='text' maxlength='240' placeholder='例：告知と事務に時間がかかる'></label>",
            "<label class='audit-field' for='audit-action'><span>ページで促したい行動</span>"
            "<input id='audit-action' name='desiredAction' type='text' maxlength='160' placeholder='例：相談予約、申込、来店'></label>",
            "<label class='audit-check'><input name='isLocalBusiness' type='checkbox' value='true'>"
            "<span><b>地域・店舗型の事業です</b><small>所在地、対応地域、連絡先も確認します</small></span></label>",
            "</div>",
            "<p class='audit-privacy'>無料の公開診断では入力内容を継続保存しません。管理者がCodex深掘りを実行した場合のみ、"
            "診断内容を保護された中継キューへ一時保存します。個人情報や管理画面のURLは入力しないでください。</p>",
            "</details>",
            "<button id='run-audit' class='audit-button audit-button--primary' type='submit'><span>無料で診断する</span><b aria-hidden='true'>→</b></button>",
            "<p id='audit-form-status' class='audit-status' role='status' aria-live='polite'></p>",
            "</form></div></div></section>",
            "<section id='audit-results' class='audit-results' hidden aria-labelledby='audit-result-title' aria-live='polite'><div class='audit-shell'>",
            "<div class='audit-section-head audit-section-head--result'><p class='audit-eyebrow'>YOUR READINESS REPORT</p>"
            "<h2 id='audit-result-title' tabindex='-1'>SEO・LLMO診断結果</h2><p id='audit-result-summary'>結果を整理しています。</p></div>",
            "<div class='audit-score-panel'><div class='audit-score-ring' id='audit-score-ring'><strong id='audit-score'>0</strong><span>/ 100</span></div>"
            "<div><p id='audit-level' class='audit-level'></p><p>点数より、下の「優先して直すこと」から一つ進めてください。</p>"
            "<div class='audit-result-actions'><button id='copy-audit-result' class='audit-button audit-button--primary' type='button'>結果をコピー</button>"
            "<button id='print-audit-result' class='audit-button audit-button--secondary' type='button'>印刷する</button></div>"
            "<p id='audit-copy-status' class='audit-status' role='status'></p></div></div>",
            "<div id='audit-categories' class='audit-categories'></div>",
            "<section class='audit-priorities' aria-labelledby='priorities-title'><div class='audit-subhead'><span>まずここから</span><h3 id='priorities-title'>優先して直すこと</h3></div>"
            "<div id='audit-priority-list'></div></section>",
            "<details class='audit-evidence'><summary>確認した項目と証拠をすべて見る</summary><div id='audit-check-list'></div></details>",
            "<aside class='codex-owner' aria-labelledby='codex-owner-title'>",
            "<div class='codex-owner__copy'><p class='audit-eyebrow'>OWNER TOOL · READ ONLY</p><h3 id='codex-owner-title'>管理者向け：Codexで改善計画を深掘り</h3>"
            "<p>公開診断の証拠を、専用Skillで「なぜ問題か・どこから直すか」へ整理します。"
            "管理者ログインと、このPCのbridge接続が必要です。App Server自体は公開しません。</p></div>",
            "<div class='codex-owner__actions'><button id='run-codex-diagnosis' class='audit-button audit-button--dark' type='button'>Codexで深掘りする</button>"
            "<a href='/admin/command-center/studio'>接続画面を開く</a></div>",
            "<div id='codex-diagnosis-status' class='codex-status' role='status' aria-live='polite'></div>",
            "<div id='codex-diagnosis-result' class='codex-result' hidden></div>",
            "</aside>",
            "<p class='audit-result-limit'>この点数は公開HTMLから確認できる準備度です。検索順位やAI回答への掲載を保証するものではありません。"
            "JavaScript描画後の内容、Search Console、アクセス解析、競合、実際の問い合わせは別途確認が必要です。</p>",
            "</div></section>",
            "<div id='audit-explanations' class='post-diagnosis-content' hidden>",
            "<section class='audit-process' aria-labelledby='process-title'><div class='audit-shell'>",
            "<div class='audit-section-head'><p class='audit-eyebrow'>診断結果の見方</p>"
            "<h2 id='process-title'>あなたのサイトは、検索とAIに正しく伝わっていますか？</h2>"
            "<p>順位の裏技ではなく、伝わる土台を4つに分けて確認しています。</p></div>",
            "<div class='audit-process__grid'>",
            "<article><span>01</span><h3>発見・クロール</h3><p>到達、noindex、robots、sitemap、canonical、OAI-SearchBotを確認。</p></article>",
            "<article><span>02</span><h3>内容の明確さ</h3><p>title、説明文、H1、見出し、本文、画像alt、構造化データを確認。</p></article>",
            "<article><span>03</span><h3>信頼・主体</h3><p>運営者、著者、所在地、連絡先、実績、OrganizationやPersonを確認。</p></article>",
            "<article><span>04</span><h3>行動・計測</h3><p>相談・申込へのCTA、料金、スマホ対応、OGP、アクセス解析を確認。</p></article>",
            "</div></div></section>",
            "<section class='audit-evidence-section' aria-labelledby='evidence-title'><div class='audit-shell audit-evidence-section__grid'>",
            "<div><p class='audit-eyebrow'>EVIDENCE, NOT HYPE</p><h2 id='evidence-title'>LLMOだけの近道は作りません</h2>"
            "<p>GoogleはAI検索にも通常のSEOの基礎が重要だと案内し、AI専用の特別なSchemaやファイルを必須としていません。"
            "この診断も、まず人に役立つ内容、クロール、明確な主体、見える内容と一致する構造化データを確認します。</p>"
            "<p>OpenAIでは、検索表示に関わる <b>OAI-SearchBot</b> と学習用の <b>GPTBot</b> を分けて制御できます。"
            "AI専用ファイルを必須点にはしません。</p></div>",
            "<div class='audit-source-list'>",
            "<a href='https://developers.google.com/search/docs/essentials' target='_blank' rel='noopener noreferrer'><b>Google Search Essentials</b><span>役立つ内容と検索の技術的な基礎</span></a>",
            "<a href='https://developers.google.com/search/docs/appearance/ai-features' target='_blank' rel='noopener noreferrer'><b>Google: AI features and your website</b><span>AI検索にも通常のSEOの基礎を適用</span></a>",
            "<a href='https://developers.google.com/search/docs/fundamentals/ai-optimization-guide' target='_blank' rel='noopener noreferrer'><b>Google AI optimization guide</b><span>特別なAI最適化の近道に依存しない</span></a>",
            "<a href='https://help.openai.com/en/articles/12627856-publishers-and-developers-faq' target='_blank' rel='noopener noreferrer'><b>OpenAI Publishers FAQ</b><span>OAI-SearchBotとGPTBotの役割</span></a>",
            "</div></div></section>",
            "<section class='audit-final-cta'><div class='audit-shell'><div><p class='audit-eyebrow'>ONE FIX AT A TIME</p>"
            "<h2>全部直すより、問い合わせにつながる一つから。</h2><p>診断結果をコピーして、AI相談へ持ち込めます。地域・教育・福祉の現場に合わせて優先順位を一緒に整理します。</p></div>"
            "<a class='audit-button audit-button--light' href='/#packages'>AI相談の講習・相談を見る</a></div></section>",
            "</div>",
            "</main>",
            "<footer class='audit-footer'><div class='audit-shell'><a href='/'>AI相談トップへ戻る</a><p>© AI相談 · SEO・LLMO診断</p></div></footer>",
            "<script type='module' src='/seo-llmo-diagnosis/app.mjs'></script>",
            "</body></html>",
        ]
    )
