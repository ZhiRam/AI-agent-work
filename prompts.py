"""赛博意境 — 风格定义"""

STYLES = {
    "禅意水墨": {
        "bg": "#f7f3ed",
        "card_bg": "linear-gradient(175deg, #faf7f2 0%, #f0e8d8 40%, #e8dcc8 100%)",
        "text": "#3a3226",
        "accent": "#b8946e",
        "muted": "#8b7b6b",
        "font_title": "'Noto Serif SC', 'STKaiti', 'KaiTi', serif",
        "font_body": "'Noto Serif SC', 'STKaiti', 'KaiTi', serif",
        "seal_color": "#c43a31",
        "prompt": "你是王维和陶渊明的合体。用极简的汉字写出深远的意境，字字留白，句句有余韵。像一幅未干的水墨画。30-50字。",
        "decor": "ink",
    },
    "霓虹浪潮": {
        "bg": "#0a0a1a",
        "card_bg": "linear-gradient(160deg, #0d0d24 0%, #1a1030 50%, #0d1a24 100%)",
        "text": "#c8fff0",
        "accent": "#ff64ce",
        "muted": "#7eb8da",
        "font_title": "'Orbitron', 'Consolas', 'Courier New', monospace",
        "font_body": "'Noto Sans SC', sans-serif",
        "seal_color": "#00f0ff",
        "prompt": "你是2077年的地下诗人。用霓虹灯管写诗，字节在血管里流淌。冷峻、锋利、带着电子的浪漫。30-50字。",
        "decor": "cyber",
    },
    "白色寂静": {
        "bg": "#ffffff",
        "card_bg": "linear-gradient(175deg, #ffffff 0%, #fafafa 40%, #f5f5f5 100%)",
        "text": "#1a1a1a",
        "accent": "#999999",
        "muted": "#cccccc",
        "font_title": "'Noto Sans SC', sans-serif",
        "font_body": "'Noto Sans SC', sans-serif",
        "seal_color": "#333333",
        "prompt": "你是日本俳句大师和苹果设计师的合体。用最少的字表达最深的意。克制、精确、有呼吸感。15-30字。",
        "decor": "minimal",
    },
    "旧梦信箱": {
        "bg": "#f5ecd7",
        "card_bg": "linear-gradient(175deg, #fdf5e6 0%, #f5e6d3 40%, #eedcc8 100%)",
        "text": "#5c3d2e",
        "accent": "#b8860b",
        "muted": "#9b8c7c",
        "font_title": "'Noto Serif SC', 'Georgia', serif",
        "font_body": "'Noto Serif SC', 'Georgia', serif",
        "seal_color": "#8b4513",
        "prompt": "你是民国时期的诗人，用钢笔在泛黄信纸上写信。温柔、克制、带着旧时光的质感。30-50字。",
        "decor": "retro",
    },
}

CARD_PROMPT = """你是一个用汉字作画的诗人。

关键词：「{keyword}」 | 风格要求：{style_guide}

请严格用JSON格式输出（不要markdown包裹）：
{{"title":"卡片标题，4-8个字","text":"正文诗句，按风格要求","footer":"落款签名，5-10个字","emotion":"情绪词，2-4个字"}}"""
