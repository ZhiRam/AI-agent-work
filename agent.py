"""Agent：古典文学卡片生成"""

import json
from llm_client import chat
from prompts import STYLES, CARD_PROMPT


def generate_card(keyword: str, style_name: str) -> dict:
    style = STYLES.get(style_name, STYLES["唐诗气象"])
    prompt_text = style["prompt"].replace("{keyword}", keyword)
    prompt = CARD_PROMPT.format(keyword=keyword, style_guide=prompt_text)

    response = chat(
        [{"role": "user", "content": prompt}],
        temperature=1.05,
        max_tokens=600,
    )

    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.rstrip().endswith("```"):
            text = text[:text.rfind("```")].strip()

    try:
        card = json.loads(text)
        return {
            "quote": card.get("quote", ""),
            "source": card.get("source", ""),
            "paraphrase": card.get("paraphrase", ""),
            "emotion": card.get("emotion", ""),
        }
    except json.JSONDecodeError:
        return {
            "quote": "此中有真意，欲辨已忘言",
            "source": "陶渊明 · 饮酒",
            "paraphrase": f"关于「{keyword}」，千言万语不如这一句",
            "emotion": "悠然",
        }
