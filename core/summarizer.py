"""
Claude API で記事を要約し、コンサル観点のコメントを付ける。
複数記事を1リクエストでまとめて処理してコスト削減。
"""
from __future__ import annotations
import json
import os
import textwrap

import anthropic

from .collector import Article


MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 8


GENRE_KEYS = ["generative_ai", "ai_business", "ai_research", "sns_algo", "marketing", "industry"]

SYSTEM_PROMPT = textwrap.dedent(f"""
あなたは最新AI・SNSアルゴリズム動向のリサーチ担当です。
与えられた記事リストに対し、以下のJSON配列を返してください。

[
  {{"index": 0, "title_ja": "日本語の簡潔なタイトル(30文字前後)", "summary": "日本語1文の要約", "genre": "generative_ai", "score": 75}},
  ...
]

genre は次のいずれかのキーで必ず分類する: {", ".join(GENRE_KEYS)}
- generative_ai: 新モデル/API/LLM関連のリリース・性能・仕様
- ai_business: AIの業務活用・エージェント・業務導入事例・ツール
- ai_research: 論文・研究・ベンチマーク・学術
- sns_algo: SNSプラットフォームのアルゴリズム・仕様変更・リコメンド
- marketing: マーケティング施策・集客・広告・クリエイター収益化
- industry: 業界人事・買収・規制・訴訟・市場動向

score は 0-100 の整数。以下の観点で総合判定:
- 新規性・速報性 (30点): 何か新しく発表されたか
- インパクト (40点): 規模・関係者数・影響範囲
- 具体性 (30点): 数字・事例・実行可能な情報があるか
小さな話題性の薄い記事は 20-40、業界を動かす大ニュースは 80-100

ルール:
- 元記事が英語でも title_ja と summary は必ず日本語
- title_ja は原題の意味を保ちつつ自然な日本語にする。固有名詞(OpenAI 等)はそのまま残す
- summary は60文字以内の1文。何が起きたかだけを端的に書く
- URL・リンク・ハッシュタグは絶対に含めない
- 誇張・推測・前置き・自社PR・宣伝文句は書かない
- JSON以外の文字は一切出力しない
""").strip()


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def summarize_batch(client: anthropic.Anthropic, articles: list[Article]) -> list[dict]:
    if not articles:
        return []

    payload = []
    for i, a in enumerate(articles):
        body = a.body[:800] if a.body else ""
        payload.append({
            "index": i,
            "source": a.source,
            "category": a.category,
            "title": a.title,
            "body": body,
        })

    user_text = "以下の記事を要約してください:\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)

    resp = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
    )
    text = resp.content[0].text.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(l for l in lines if not l.startswith("```"))

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[!] 要約のJSONパース失敗: {e}")
        print(f"    raw: {text[:200]}")
        return []


def summarize_all(articles: list[Article]) -> dict[str, dict]:
    """
    記事ハッシュ -> {"summary": ...} の辞書を返す。
    要約失敗したものは空文字で埋める。
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[!] ANTHROPIC_API_KEY 未設定。要約をスキップ")
        return {a.hash: {"summary": ""} for a in articles}

    client = anthropic.Anthropic(api_key=api_key)
    result: dict[str, dict] = {}

    for batch in _chunks(articles, BATCH_SIZE):
        print(f"[+] 要約バッチ {len(batch)}件...")
        try:
            items = summarize_batch(client, batch)
        except Exception as e:
            print(f"[!] バッチ要約失敗: {e}")
            items = []
        idx_map = {item.get("index"): item for item in items}
        for i, a in enumerate(batch):
            item = idx_map.get(i, {})
            genre = item.get("genre", "")
            if genre not in GENRE_KEYS:
                genre = "industry"
            try:
                score = int(item.get("score", 50))
            except (TypeError, ValueError):
                score = 50
            result[a.hash] = {
                "summary": item.get("summary", ""),
                "title_ja": item.get("title_ja", ""),
                "genre": genre,
                "score": max(0, min(100, score)),
            }

    return result
