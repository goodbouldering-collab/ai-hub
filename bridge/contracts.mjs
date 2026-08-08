const string = (description) => ({ type: "string", description });
const stringArray = (description) => ({ type: "array", items: { type: "string" }, description });

export const BLOG_TOPIC_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["stage", "candidates"],
  properties: {
    stage: { const: "topics" },
    candidates: {
      type: "array",
      minItems: 6,
      maxItems: 8,
      items: {
        type: "object",
        additionalProperties: false,
        required: ["id", "title", "estimatedBuzzReason", "audience", "problem", "businessFit", "angle", "nextAction", "sources", "reuse"],
        properties: {
          id: string("候補ID"),
          title: string("国内トピック候補"),
          estimatedBuzzReason: string("新しさ40%、独立情報源35%、実用影響25%で見た相対評価"),
          audience: string("誰に向けるか"),
          problem: string("身近な悩み"),
          businessFit: string("この事業が扱う理由"),
          angle: string("記事の切り口"),
          nextAction: string("読後の行動"),
          sources: {
            type: "array",
            minItems: 2,
            items: {
              type: "object",
              additionalProperties: false,
              required: ["title", "url", "publisher", "date", "signal"],
              properties: { title: string("出典名"), url: string("URL"), publisher: string("発行元"), date: string("公開または更新日"), signal: string("注目の根拠") },
            },
          },
          reuse: { type: "object", required: ["blog", "sns", "note", "youtube"], properties: { blog: string("ブログ"), sns: string("SNS"), note: string("note"), youtube: string("YouTube") }, additionalProperties: false },
        },
      },
    },
  },
};

export const BLOG_TITLE_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["stage", "recommendedId", "titles"],
  properties: {
    stage: { const: "titles" },
    recommendedId: string("推奨案ID"),
    titles: {
      type: "array",
      minItems: 3,
      maxItems: 3,
      items: {
        type: "object",
        additionalProperties: false,
        required: ["id", "title", "editorialAngle", "audience", "problem", "benefit", "cta", "searchIntent", "keywords", "localRelevance", "researchAngle", "businessReason"],
        properties: {
          id: string("タイトル案ID"), title: string("仮SEOタイトル"), editorialAngle: string("編集ロジック"), audience: string("対象読者"),
          problem: string("解決する悩み"), benefit: string("顧客の変化"), cta: string("読後の行動"), searchIntent: string("検索意図"),
          keywords: stringArray("主要キーワード"), localRelevance: string("地域との関係"), researchAngle: string("調査観点"), businessReason: string("この事業が書く理由"),
        },
      },
    },
  },
};

export const BLOG_H2_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["stage", "recommendedId", "groups"],
  properties: {
    stage: { const: "h2" },
    recommendedId: string("推奨グループID"),
    groups: {
      type: "array",
      minItems: 3,
      maxItems: 3,
      items: {
        type: "object",
        additionalProperties: false,
        required: ["id", "editorialFlow", "headings"],
        properties: {
          id: string("H2グループID"), editorialFlow: string("構成の流れ"),
          headings: { type: "array", minItems: 3, maxItems: 5, items: { type: "object", additionalProperties: false, required: ["heading", "purpose"], properties: { heading: string("H2"), purpose: string("この章で伝えること") } } },
        },
      },
    },
  },
};

export const BLOG_REVIEW_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["stage", "finalTitle", "titleRevisionReason", "introduction", "sections", "conclusion", "cta", "faq", "sources", "factCheckItems", "heroImage"],
  properties: {
    stage: { const: "review" }, finalTitle: string("本文完成後に再検討した最終タイトル"), titleRevisionReason: string("変更理由"), introduction: string("導入"),
    sections: { type: "array", minItems: 3, maxItems: 5, items: { type: "object", additionalProperties: false, required: ["heading", "body", "image"], properties: { heading: string("H2"), body: string("本文"), image: { type: "object", additionalProperties: false, required: ["sourceType", "prompt", "alt", "caption"], properties: { sourceType: { enum: ["field-photo", "owned-screenshot", "generated-fallback"] }, prompt: string("編集可能な画像指示"), alt: string("代替文"), caption: string("説明文") } } } } },
    conclusion: string("まとめ"), cta: string("一つの現実的な行動"), faq: { type: "array", items: { type: "object", additionalProperties: false, required: ["question", "answer"], properties: { question: string("質問"), answer: string("回答") } } },
    sources: { type: "array", items: { type: "object", additionalProperties: false, required: ["title", "url", "claim"], properties: { title: string("出典"), url: string("URL"), claim: string("裏付ける内容") } } }, factCheckItems: stringArray("未確認事項"),
    heroImage: { type: "object", additionalProperties: false, required: ["sourceType", "prompt", "alt", "caption"], properties: { sourceType: { enum: ["field-photo", "owned-screenshot", "generated-fallback"] }, prompt: string("最終タイトルに合わせた画像指示"), alt: string("代替文"), caption: string("説明文") } },
  },
};

export const BLOG_HTML_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["stage", "html", "cmsPayload", "draftStatus", "draftCapability"],
  properties: {
    stage: { const: "html" }, html: string("editor専用属性や認証情報を含まない完全HTML"), cmsPayload: { type: "object" },
    draftStatus: { enum: ["not-saved", "draft"] }, draftCapability: string("下書き保存の可否と不足条件"), cmsDraftId: { type: ["string", "null"] }, privatePreviewUrl: { type: ["string", "null"] },
  },
};

export const REEL_SET_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["stage", "account", "finalUrl", "videoPlan", "textBeats", "caption", "storyText", "shopComment", "factCheckItems"],
  properties: {
    stage: { const: "reel-set" }, account: string("確認済み投稿先"), finalUrl: string("確認済み最終URL"), videoPlan: string("全画面9:16動画構成"),
    textBeats: { type: "array", minItems: 5, maxItems: 5, items: string("3行以内の中央配置テキスト") }, caption: string("読みやすいキャプション。最終行にURL"),
    storyText: string("1〜2行のストーリーズ短文"), shopComment: string("1〜3文の店舗コメント"), factCheckItems: stringArray("未確認事項"),
  },
};

export const REEL_PUBLISH_REVIEW_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["stage", "account", "publishedReelUrl", "storyText", "shopComment", "requiresFinalApproval"],
  properties: {
    stage: { const: "reel-publish-review" }, account: string("公開先"), publishedReelUrl: string("公開済みREEL URL"), storyText: string("共有直前の文面"), shopComment: string("投稿直前のコメント"), requiresFinalApproval: { const: true },
  },
};

export const STAGE_SCHEMAS = {
  topics: BLOG_TOPIC_SCHEMA,
  titles: BLOG_TITLE_SCHEMA,
  h2: BLOG_H2_SCHEMA,
  review: BLOG_REVIEW_SCHEMA,
  html: BLOG_HTML_SCHEMA,
  "reel-set": REEL_SET_SCHEMA,
  "reel-publish-review": REEL_PUBLISH_REVIEW_SCHEMA,
};

export const NEXT_STAGES = {
  topics: ["titles"], titles: ["h2"], h2: ["review"], review: ["html"], html: [],
  "reel-set": ["reel-publish-review"], "reel-publish-review": ["reel-final"], "reel-final": [],
};
