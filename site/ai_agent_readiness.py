"""Static page renderer for the AI Agent Readiness Compass."""

from __future__ import annotations

import html
import json


SITE_BROWSER_TITLE = "AI相談｜一歩踏み出す人のAI講習・実践支援【彦根・滋賀】"


def _video_card(
    *,
    video_id: str,
    eyebrow: str,
    title: str,
    summary: str,
    level: str,
    watch_url: str | None = None,
) -> str:
    """Render a consent-first YouTube card without loading an iframe."""
    safe_id = html.escape(video_id, quote=True)
    safe_watch_url = html.escape(
        watch_url or f"https://www.youtube.com/watch?v={safe_id}",
        quote=True,
    )
    return (
        "<article class='video-card'>"
        f"<div class='video-card__visual' data-poster-id='{safe_id}' aria-hidden='true'>"
        "<span class='video-card__play'>▶</span>"
        f"<span class='video-card__level'>{html.escape(level)}</span>"
        "</div>"
        "<div class='video-card__body'>"
        f"<p class='eyebrow'>{html.escape(eyebrow)}</p>"
        f"<h3>{html.escape(title)}</h3>"
        f"<p>{html.escape(summary)}</p>"
        "<div class='video-card__actions'>"
        f"<button class='button button--video' type='button' data-video-consent data-video-id='{safe_id}'>"
        "同意してこの場で再生</button>"
        f"<a class='text-link' href='{safe_watch_url}' target='_blank' rel='noopener noreferrer'>YouTubeで見る</a>"
        "</div>"
        f"<div class='video-player-slot' data-video-player='{safe_id}' aria-live='polite'></div>"
        "</div>"
        "</article>"
    )


def render_ai_agent_readiness_page(
    site_url: str,
    nav_html: str,
    favicon_html: str,
    shared_header_css: str,
) -> str:
    """Return the standalone, progressively enhanced assessment page."""
    base_url = site_url.rstrip("/")
    canonical_url = f"{base_url}/ai-agent-readiness/"
    description = (
        "たった10問・約3分で、AI実践力を100点・5段階で確認し、いまの実力と次に整えることがわかる無料診断です。"
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "AI Agent Readiness Compass",
        "alternateName": "AI実践力診断",
        "applicationCategory": "EducationalApplication",
        "operatingSystem": "Any",
        "inLanguage": "ja",
        "isAccessibleForFree": True,
        "url": canonical_url,
        "description": description,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "publisher": {"@type": "Organization", "name": "AI相談", "url": base_url},
    }

    videos = "".join(
        [
            _video_card(
                video_id="2gtWv3iib8M",
                eyebrow="未来を読む｜ユーザー指定",
                title="AI業界の急変を、仕事と社会の視点で考える",
                summary=(
                    "知能の一般化、AIの二面性、モデル切替、成果物の持ち運び、事業価値、動画・物理AIを考える入口。"
                    "個別の主張や予測を、正答や閾値には使いません。一次資料と照らして見ます。"
                ),
                level="全レベル",
                watch_url="https://www.youtube.com/watch?v=2gtWv3iib8M&list=PLOI7QjtBx9_yavYb1jZZwQXgEa2HALAKQ",
            ),
            _video_card(
                video_id="K6KX41tLH2s",
                eyebrow="日本語解説｜Human on the Loop",
                title="AIを全操作する人から、仕組みを監督する人へ",
                summary=(
                    "安野貴博氏の公開解説から、人がAIの全操作を抱えず、目的・承認・結果を監督する考え方を学びます。"
                    "二次解説として扱い、安全や運用の基準は一次資料でも確かめます。"
                ),
                level="Level 1–3",
            ),
            _video_card(
                video_id="px7XlbYgk7I",
                eyebrow="OpenAI公式｜Codex",
                title="Getting started with Codex",
                summary=(
                    "導入、リポジトリでの作業、依頼の書き方、AGENTS.md、CLI・IDE、MCPまでを公式の流れで確認。"
                    "診断のコード・システム領域を伸ばしたい人向けです。"
                ),
                level="Level 3–5",
            ),
            _video_card(
                video_id="OhI005_aJkA",
                eyebrow="Microsoft公式｜AI Agents",
                title="AIエージェントを体系で学ぶ",
                summary=(
                    "エージェントの基本概念から設計・運用までを、講座形式で整理したい人の学習入口。"
                    "製品固有の操作より、全体像をつかむ目的で選定しています。"
                ),
                level="Level 2–4",
            ),
            _video_card(
                video_id="LRSSjGwsuv0",
                eyebrow="日本語の人気解説｜PIVOT",
                title="AIエージェントを仕事のチームとして捉える",
                summary=(
                    "Claude Codeを題材に、AIへ仕事を任せる感覚を日本語でつかむ入門。"
                    "Codexとの製品差より、仕事の分解、確認、成果物を残す考え方に注目します。"
                ),
                level="Level 1–3",
            ),
        ]
    )

    return "".join(
        [
            "<!doctype html><html lang='ja'><head><meta charset='utf-8'>",
            favicon_html,
            "<meta name='viewport' content='width=device-width,initial-scale=1'>",
            "<meta name='theme-color' content='#172033'>",
            f"<title>{html.escape(SITE_BROWSER_TITLE)}</title>",
            f"<meta name='description' content='{html.escape(description, quote=True)}'>",
            f"<link rel='canonical' href='{html.escape(canonical_url, quote=True)}'>",
            "<meta property='og:type' content='website'>",
            "<meta property='og:locale' content='ja_JP'>",
            "<meta property='og:site_name' content='AI相談'>",
            "<meta property='og:title' content='AI Agent Readiness Compass｜AI実践力診断'>",
            f"<meta property='og:description' content='{html.escape(description, quote=True)}'>",
            f"<meta property='og:url' content='{html.escape(canonical_url, quote=True)}'>",
            "<meta name='twitter:card' content='summary'>",
            "<link rel='preconnect' href='https://fonts.googleapis.com'>",
            "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>",
            "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Noto+Sans+JP:wght@400;500;600;700;900&display=swap'>",
            "<link rel='stylesheet' href='/ai-agent-readiness/styles.css'>",
            f"<style>{shared_header_css}</style>",
            f"<script type='application/ld+json'>{json.dumps(schema, ensure_ascii=False)}</script>",
            "</head><body class='readiness-page'>",
            "<a class='skip-link' href='#assessment-app'>診断へ移動</a>",
            nav_html,
            "<main>",
            "<section class='readiness-hero' aria-labelledby='readiness-title'>",
            "<div class='readiness-shell readiness-hero__grid'>",
            "<div class='readiness-hero__copy'>",
            "<p class='eyebrow'>FREE SELF-ASSESSMENT · たった10問・約3分</p>",
            "<h1 id='readiness-title'><span>AI Agent Readiness Compass</span>AI実践力診断</h1>",
            "<p class='readiness-hero__lead'>あなたはAIに聞く人か、任せて確かめる人か。</p>",
            "<p>たった10問・約3分で、いまの実力と次に整えることを100点・5段階で可視化。"
            "答えるたびに、任せる・確かめる・残すための基準がわかります。</p>",
            "<div class='readiness-hero__facts' aria-label='診断の特徴'>",
            "<span><b>10問</b> 実際の行動で回答</span>",
            "<span><b>100点</b> 5領域を見える化</span>",
            "<span><b>5段階</b> 次に整えることへ接続</span>",
            "</div>",
            "<a class='button button--primary' href='#assessment-app'>いまのAI実践力を測る</a>",
            "<p class='privacy-note'>回答はこのブラウザ内だけで計算し、サーバーへ送信しません。個人情報の入力も不要です。</p>",
            "</div>",
            "<aside class='readiness-hero__compass' aria-label='5段階の到達イメージ'>",
            "<p class='eyebrow'>YOUR NEXT POSITION</p>",
            "<ol><li><b>01</b><span>Explorer<small>AIの入口を見つける</small></span></li>"
            "<li><b>02</b><span>Guided AI User<small>対話で仕事を整える</small></span></li>"
            "<li><b>03</b><span>Workflow Builder<small>仕事の型にする</small></span></li>"
            "<li><b>04</b><span>Agent Operator<small>任せて検証する</small></span></li>"
            "<li><b>05</b><span>Agent Orchestrator<small>複数AIと仕組みを率いる</small></span></li></ol>",
            "</aside></div></section>",
            "<section class='readiness-section readiness-section--assessment'>",
            "<div class='readiness-shell'>",
            "<div id='assessment-app' class='assessment-card' aria-labelledby='assessment-heading'>",
            "<div id='assessment-intro' class='assessment-intro'>",
            "<p class='eyebrow'>START FROM EVIDENCE</p>",
            "<h2 id='assessment-heading'>知識ではなく、直近90日の行動で答えてください</h2>",
            "<p>10問は、答える前に「仕事でAIを使い続ける基準」を短く学べる構成です。"
            "「知っている」より「試した・確認した・残した」を重く採点します。</p>",
            "<ul class='assessment-rules'><li>迷ったら、低い方の選択肢を選ぶ</li>"
            "<li>仕事・地域活動・学習の、どの場面を思い浮かべてもよい</li>"
            "<li>高得点でも検証や安全管理が弱い場合は、到達レベルを調整する</li></ul>",
            "<button id='start-assessment' class='button button--primary' type='button'>10問・約3分の診断を始める</button>",
            "</div>",
            "<form id='assessment-form' class='assessment-form' hidden>",
            "<div class='assessment-progress'>",
            "<span id='progress-label'>質問 1 / 10</span>",
            "<progress id='assessment-progress' max='10' value='0'>0 / 10</progress>",
            "</div>",
            "<p id='assessment-status' class='sr-only' aria-live='polite'></p>",
            "<fieldset id='question-fieldset'>",
            "<legend><span id='question-number'>Question 01</span><strong id='question-prompt'>質問を読み込んでいます</strong></legend>",
            "<p id='question-context' class='question-context'></p>",
            "<aside id='question-learning' class='question-learning' aria-label='この問いで身につく基準'>"
            "<span>この問いで身につく基準</span><p id='question-learning-text'></p></aside>",
            "<div id='answer-options' class='answer-options'></div>",
            "</fieldset>",
            "<div class='assessment-navigation'>",
            "<button id='previous-question' class='button button--secondary' type='button'>戻る</button>",
            "<button id='next-question' class='button button--primary' type='button'>次へ</button>",
            "</div></form>",
            "<section id='result-panel' class='result-panel' hidden aria-labelledby='result-heading'>",
            "<p class='eyebrow'>YOUR READINESS MAP</p>",
            "<h2 id='result-heading'>診断結果</h2>",
            "<div class='result-hero'><p><strong id='result-score'>0</strong><span>/ 100点</span></p>"
            "<div><p id='result-level'></p><p id='result-summary'></p></div></div>",
            "<div id='safety-gate' class='safety-gate' aria-live='polite'></div>",
            "<div class='result-grid'><section><h3>5領域の現在地</h3><div id='dimension-scores'></div></section>"
            "<section><h3>続けて伸ばす5指標</h3><p>未来予測ではありません。同じ回答を別の観点で再集計した学習指標で、100点への追加点ではありません。</p>"
            "<div id='future-scores'></div></section></div>",
            "<section class='next-steps'><h3>次の90日</h3><div id='next-steps'></div></section>",
            "<section id='course-recommendation' class='course-recommendation' aria-label='AI相談の任意の学習サポート'>"
            "<p>AI相談が提供する自社サービスです。これは弱点別の個別処方ではなく、レベル別の標準案です。"
            "購入は任意で、上の90日行動は無料でも実践できます。"
            "点数だけで受講の必要性を判断するものではありません。</p></section>",
            "<div class='result-actions'><button id='copy-result' class='button button--primary' type='button'>相談メモをコピー</button>"
            "<button id='print-result' class='button button--secondary' type='button'>結果を印刷</button>"
            "<button id='restart-assessment' class='text-button' type='button'>もう一度診断する</button></div>",
            "<p id='copy-status' class='copy-status' aria-live='polite'></p>",
            "</section>",
            "<noscript><p class='noscript-notice'>この診断にはJavaScriptが必要です。"
            "JavaScriptを有効にするか、AI相談の無料相談で現在地を一緒に整理してください。</p></noscript>",
            "</div></div></section>",
            "<section class='readiness-section readiness-section--mindset' aria-labelledby='mindset-title'>",
            "<div class='readiness-shell split-layout'><div>",
            "<p class='eyebrow'>MORE TIME, BETTER WORK</p><h2 id='mindset-title'>AIは、人を減らすためでなく、人が考える時間を増やすために使う</h2>",
            "<p>測るのは操作の速さだけではありません。単純作業を短くし、確認できる成果物を残し、"
            "利用者への説明や創造、対話に時間を戻せたかを見ます。</p>",
            "<p>ILOの雇用研究も、生成AIの影響は仕事全体の置き換えより、仕事内容の変容として現れる可能性が高いと整理しています。"
            "だからこそ、人の判断、承認、責任を残した使い方を学びます。</p></div>",
            "<div class='mindset-points'><article><b>TIME</b><h3>時間をつくる</h3><p>繰り返し作業を減らし、相談・支援・挑戦へ時間を戻す。</p></article>"
            "<article><b>QUALITY</b><h3>質を上げる</h3><p>成功条件と確認手順を持ち、速さと正確さを両立する。</p></article>"
            "<article><b>FREEDOM</b><h3>選択肢を増やす</h3><p>成果物と手順を持ち運べる形で残し、特定のAIだけに依存しない。</p></article></div>",
            "</div></section>",
            "<section class='readiness-section' id='video-library' aria-labelledby='video-title'>",
            "<div class='readiness-shell'><div class='section-heading'><p class='eyebrow'>CURATED VIDEO PATH</p>"
            "<h2 id='video-title'>人気動画を、あなたの次の一歩に並べ替えました</h2>"
            "<p>公開動画とユーザー指定動画を2026-08-13に確認。再生数は変動するため順位表示はせず、"
            "公式性、わかりやすさ、実務へのつながりで選びました。人気は正確性を保証しません。</p></div>",
            "<p class='video-consent-note'>ページ表示時にはYouTubeを読み込みません。"
            "「同意してこの場で再生」を押した動画だけ、YouTubeのプライバシー強化モードで読み込みます。通常リンクも利用できます。</p>",
            f"<div class='video-grid'>{videos}</div>",
            "</div></section>",
            "<section class='readiness-section readiness-section--sources' id='sources' aria-labelledby='sources-title'>",
            "<div class='readiness-shell'><div class='section-heading'><p class='eyebrow'>EVIDENCE & LIMITS</p>"
            "<h2 id='sources-title'>専門家が確認できる根拠と、診断の限界</h2>"
            "<p>国際的なAIリテラシー、リスク管理、エージェント設計、雇用変容の一次資料を参考に、成人の実務向けへ独自再構成しました。</p></div>",
            "<div class='source-grid'>",
            "<a href='https://www.oecd.org/en/publications/empowering-learners-for-the-age-of-ai_65cd27d4-en.html' target='_blank' rel='noopener noreferrer'><b>OECD / European Commission</b><span>AI Literacy Framework</span></a>",
            "<a href='https://www.unesco.org/en/articles/ai-competency-framework-students' target='_blank' rel='noopener noreferrer'><b>UNESCO</b><span>AI Competency Framework</span></a>",
            "<a href='https://www.nist.gov/itl/ai-risk-management-framework' target='_blank' rel='noopener noreferrer'><b>NIST</b><span>AI Risk Management Framework</span></a>",
            "<a href='https://www.anthropic.com/engineering/building-effective-agents' target='_blank' rel='noopener noreferrer'><b>Anthropic</b><span>Building Effective Agents</span></a>",
            "<a href='https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/' target='_blank' rel='noopener noreferrer'><b>OpenAI</b><span>A practical guide to building agents</span></a>",
            "<a href='https://www.ilo.org/resource/news/one-four-jobs-risk-being-transformed-genai-new-ilo%E2%80%93nask-global-index-shows' target='_blank' rel='noopener noreferrer'><b>ILO</b><span>Generative AI and jobs</span></a>",
            "</div>",
            "<div class='assessment-limit'><h3>この診断で証明できないこと</h3>"
            "<p>これは学習用セルフチェックです。心理検査、資格認定、採用・適職判定、法令適合証明、"
            "就職・昇進・収入・成果の保証ではありません。自己申告を含むため、実務力は成果物と第三者レビューでも確認してください。</p>"
            "<p>10問は各0・2・4・5点で答え、合計を2倍して100点に換算します。5領域は各2問です。"
            "実際に表示される合計は偶数です。レベルごとの実回答の範囲は、0〜24 / 26〜44 / 46〜64 / 66〜84 / 86〜100点です。"
            "レベル境界と安全ゲートは学習導線のための独自基準です。統計的に標準化された基準ではありません。"
            "参考機関による認定もありません。</p>"
            "<p>「今後のAI指標」は未来予測ではありません。技術や社会の変化に備えるための学習目標です。"
            "動画や対談は視野を広げる教材です。個別の主張や予測を、正答や閾値には使いません。"
            "一次資料と照合できる論点だけを学習項目へ反映しています。</p></div>",
            "</div></section>",
            "<section class='readiness-cta'><div class='readiness-shell'><p class='eyebrow'>BRING YOUR SCORE</p>"
            "<h2>点数より、次に何を一緒に作るか。</h2>"
            "<p>診断結果の相談メモを持って、止まっている仕事、重い事務、苦手な告知を整理できます。</p>"
            "<a class='button button--light' href='/#packages'>AI相談の講習・相談を見る</a></div></section>",
            "</main>",
            "<footer class='readiness-footer'><div class='readiness-shell'><a href='/'>AI相談トップへ戻る</a>"
            "<p>© AI相談 · AI Agent Readiness Compass</p></div></footer>",
            "<script type='module' src='/ai-agent-readiness/app.mjs'></script>",
            "</body></html>",
        ]
    )
