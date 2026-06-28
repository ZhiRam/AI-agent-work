"""Agent：诗意卡片生成"""

import json
from llm_client import chat
from prompts import STYLES, CARD_PROMPT


def generate_card(keyword: str, style_name: str) -> dict:
    """生成一张艺术卡片"""
    style = STYLES.get(style_name, STYLES["白色寂静"])
    prompt = CARD_PROMPT.format(keyword=keyword, style_guide=style["prompt"])

    response = chat(
        [{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=400,
    )

    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "title": keyword,
            "text": response[:100],
            "footer": "— 意境 —",
            "emotion": "诗意",
        }
