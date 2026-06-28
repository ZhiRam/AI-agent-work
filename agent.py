"""Agent：诗意卡片生成"""

import json
from llm_client import chat
from prompts import CARD_PROMPT, STYLE_PROMPTS


def generate_card(keyword: str, style: str) -> dict:
    """生成一张艺术卡片

    Returns:
        {"title": str, "text": str, "footer": str, "emotion": str}
    """
    style_detail = STYLE_PROMPTS.get(style, STYLE_PROMPTS["极简"])
    prompt = CARD_PROMPT.format(keyword=keyword, style=style, style_detail=style_detail)

    response = chat(
        [{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=512,
    )

    # 解析 JSON
    try:
        # 清理可能的 markdown 包裹
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]
        card = json.loads(text)
        return card
    except json.JSONDecodeError:
        # 容错：手动提取
        return {
            "title": keyword,
            "text": response[:100],
            "footer": "— 意境卡片 —",
            "emotion": "诗意",
        }
