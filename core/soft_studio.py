"""A small, progressively enhanced example of sharing work with AI.

This decorator owns only its section and two asset tags. It does not collect
input, call a service, or alter the site's existing content and destinations.
"""

from html import escape
from html.parser import HTMLParser
import re


STYLE = '<link id="soft-playground-style" rel="stylesheet" href="/design-system/studio/soft-playground.css?v=20260918">'
SCRIPT = '<script id="soft-playground-script" defer src="/design-system/studio/soft-playground.js?v=20260918"></script>'

SCENARIOS = (
    {
        "id": "announce", "label": "告知", "title": "伝えたいことを、届く言葉に。",
        "input": "催しの内容・日時・場所・参加条件をまとめたメモ。",
        "manual": "必要な情報を拾い、順番を決めて、案内文を一から書く。",
        "ai": "メモを整理し、見出しと案内文のたたき台をつくる。",
        "check": "日時・場所・料金が正しいか。参加する人が迷わないか。",
        "output_title": "案内文のたたき台",
        "output": ("親子で、つくる時間を。", "身近な材料で楽しむ、ものづくりの会。", "日時：○月○日　場所：○○会場", "対象・参加費・申込方法を確認してから公開。"),
    },
    {
        "id": "office", "label": "事務", "title": "ばらばらのメモを、次の一歩に。",
        "input": "個人情報を含めずに用意した、作業と締切のメモ。",
        "manual": "メモを読み返し、作業・担当・確認事項を表にまとめる。",
        "ai": "メモを作業ごとに分け、抜けている確認事項を洗い出す。",
        "check": "元のメモと合っているか。担当や締切を勝手に補っていないか。",
        "output_title": "確認リストのたたき台",
        "output": ("会場の予約 → 空き状況を確認", "案内文の作成 → 掲載内容を確認", "当日の準備 → 担当と締切を相談", "分からない項目は「要確認」のまま残す。"),
    },
    {
        "id": "website", "label": "サイト制作", "title": "頭の中のサービスを、小さなページに。",
        "input": "誰に、何を届けたいか。サービスの内容と相談方法のメモ。",
        "manual": "ページの構成を考え、見出しと本文を書いて並べる。",
        "ai": "メモから構成案を出し、見出しや説明文を一緒に整える。",
        "check": "内容や料金が正しいか。スマートフォンで読めて、相談先につながるか。",
        "output_title": "ページ構成のたたき台",
        "output": ("01　こんなお困りごとに", "02　できること・利用の流れ", "03　料金・相談方法", "公開する前に、内容とリンク先を確認。"),
    },
)


def _mode_html(item: dict, mode: str) -> str:
    is_ai = mode == "ai"
    heading = "AIと進めるなら" if is_ai else "手作業で進めるなら"
    working = "AIに任せること" if is_ai else "自分で進めること"
    output = "".join(f"<p>{escape(line)}</p>" for line in item["output"])
    return f'''<div class="soft-playground__example" data-sp-mode="{mode}">
      <h4 class="soft-playground__mode-title">{heading}</h4>
      <div class="soft-playground__workspace">
        <dl class="soft-playground__steps">
          <div><dt><span aria-hidden="true">01</span> 手元にあるもの</dt><dd>{escape(item["input"])}</dd></div>
          <div class="soft-playground__delegate"><dt><span aria-hidden="true">02</span> {working}</dt><dd>{escape(item[mode])}</dd></div>
          <div><dt><span aria-hidden="true">03</span> 人が確かめること</dt><dd>{escape(item["check"])}</dd></div>
        </dl>
        <div class="soft-playground__output">
          <p class="soft-playground__output-label">できあがりの例</p>
          <h5>{escape(item["output_title"])}</h5>
          <div class="soft-playground__paper">{output}</div>
          <p class="soft-playground__output-note">仕上げるのは、人の目と判断。</p>
        </div>
      </div>
    </div>'''


def playground_html() -> str:
    tabs = "".join(
        f'<button type="button" role="tab" id="studio-playground-tab-{item["id"]}" '
        f'aria-controls="studio-playground-panel-{item["id"]}" '
        f'aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}" '
        f'data-sp-tab="{item["id"]}">{item["label"]}</button>'
        for i, item in enumerate(SCENARIOS)
    )
    panels = "\n".join(
        f'<article class="soft-playground__panel" id="studio-playground-panel-{item["id"]}" data-sp-panel="{item["id"]}">'
        f'<h3>{escape(item["title"])}</h3>{_mode_html(item, "manual")}{_mode_html(item, "ai")}</article>'
        for item in SCENARIOS
    )
    return f'''<section id="studio-playground" class="soft-playground" aria-labelledby="studio-playground-title">
  <header class="soft-playground__intro">
    <div><p class="soft-playground__eyebrow">小さく試す、仕事の整え方</p>
      <h2 id="studio-playground-title">AIと、どこから一緒にやろう。</h2>
      <p class="soft-playground__lead">身近な仕事を選んで、任せることと、確かめることを見てみる。</p>
    </div>
    <svg class="soft-playground__doodle" width="124" height="112" viewBox="0 0 124 112" aria-hidden="true" focusable="false" fill="none">
      <path d="M19 77C7 61 16 26 41 17C67 7 104 24 108 51C113 82 85 103 54 99" fill="#e4e9dd"/>
      <path d="M35 31Q56 25 80 30L86 78Q62 87 40 79Z" fill="#fffdf5" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>
      <path d="M45 44L69 41M47 54L72 51M49 64L60 62M14 89Q34 68 46 91Q54 105 66 94M92 17L96 24M99 12L103 19M98 29L107 28" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
      <circle cx="89" cy="79" r="12" fill="#f0d2bb"/><path d="M84 79L88 83L95 75" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </header>
  <div class="soft-playground__controls" data-sp-controls hidden>
    <div class="soft-playground__tabs" role="tablist" aria-label="試してみる仕事">{tabs}</div>
    <fieldset class="soft-playground__modes"><legend>進め方を切り替える</legend>
      <label><input type="radio" name="studio-playground-mode" value="manual"><span>手作業で進める</span></label>
      <label><input type="radio" name="studio-playground-mode" value="ai" checked><span>AIと進める</span></label>
    </fieldset>
  </div>
  <div class="soft-playground__panels">{panels}</div>
  <p class="soft-playground__disclaimer">架空のサンプルです。ここではAIへの入力・送信・生成は行いません。</p>
  <p class="soft-playground__status" data-sp-status role="status" aria-live="polite" aria-atomic="true"></p>
</section>'''


class _SectionSpan(HTMLParser):
    def __init__(self, source: str, element_id: str):
        super().__init__(convert_charrefs=False)
        self.source, self.element_id = source, element_id
        self.lines = [0]
        for match in re.finditer("\n", source):
            self.lines.append(match.end())
        self.depth = 0
        self.start = self.target_depth = None
        self.span = None

    def source_offset(self) -> int:
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag == "section":
            self.depth += 1
            if self.start is None and self.span is None and dict(attrs).get("id") == self.element_id:
                self.start, self.target_depth = self.source_offset(), self.depth

    def handle_endtag(self, tag):
        if tag == "section":
            if self.start is not None and self.depth == self.target_depth:
                self.span = (self.start, self.source.index(">", self.source_offset()) + 1)
                self.start = None
            self.depth -= 1


def _section_span(text: str, element_id: str):
    parser = _SectionSpan(text, element_id)
    parser.feed(text)
    return parser.span


def _asset(text: str, tag: str, element_id: str, markup: str, closing: str) -> str:
    pattern = rf'<{tag}\b[^>]*\bid=([\"\x27]){element_id}\1[^>]*>'
    if tag == "script":
        pattern += r"\s*</script\s*>"
    # The surrounding theme also refreshes its tags on every pass. Relocate
    # our owned tag after those tags instead of retaining a stale position.
    text = re.sub(pattern, "", text, flags=re.I)
    end = re.search(rf"</{closing}\s*>", text, flags=re.I)
    if not end:
        raise ValueError(f"Soft playground requires a closing {closing} tag")
    return re.sub(rf"\s*</{closing}\s*>", lambda _: markup + f"\n</{closing}>", text, count=1, flags=re.I)


def decorate_soft_playground(text: str) -> str:
    """Insert the owned playground after AI news, without reserializing the page."""
    existing = _section_span(text, "studio-playground")
    if existing:
        text = text[:existing[0]] + playground_html() + text[existing[1]:]
    else:
        news = _section_span(text, "ai-news")
        if not news:
            raise ValueError("Soft playground requires the homepage ai-news section")
        text = text[:news[1]] + "\n" + playground_html() + "\n" + text[news[1]:]
    text = _asset(text, "link", "soft-playground-style", STYLE, "head")
    return _asset(text, "script", "soft-playground-script", SCRIPT, "body")
