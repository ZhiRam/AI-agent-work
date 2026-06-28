"""赛博意境 — 古典文学风格"""

STYLES = {
    "唐诗气象": {
        "bg": "#faf8f3",
        "card_bg": "linear-gradient(175deg, #fcfaf5 0%, #f5f0e0 40%, #ede4cc 100%)",
        "text": "#4a3728",
        "accent": "#c4956a",
        "muted": "#a09080",
        "font_title": "'Noto Serif SC', 'STKaiti', 'KaiTi', serif",
        "font_body": "'Noto Serif SC', 'STKaiti', 'KaiTi', serif",
        "seal_color": "#c04030",
        "prompt": """引用或化用与「{keyword}」相关的唐诗（李白、杜甫、王维、白居易等）。
先写一句最贴切的唐诗原文（标注作者和诗名），再用白话写一句简短的意境解读。
整体风格：盛唐气象，雄浑或空灵，有天地苍茫之感。""",
        "decor": "ink",
    },
    "宋词余韵": {
        "bg": "#f8f5fa",
        "card_bg": "linear-gradient(175deg, #faf8fc 0%, #f0ebf5 40%, #e8e0f0 100%)",
        "text": "#3d2e5c",
        "accent": "#8b6fae",
        "muted": "#9b8baa",
        "font_title": "'Noto Serif SC', 'STKaiti', serif",
        "font_body": "'Noto Serif SC', 'STKaiti', serif",
        "seal_color": "#7b5ea7",
        "prompt": """引用或化用与「{keyword}」相关的宋词（苏轼、李清照、辛弃疾、柳永等）。
先写一句最贴切的宋词原文（标注作者和词牌名），再用白话写一句简短的意境解读。
整体风格：婉约或豪放，有词的韵律感和细腻情感。""",
        "decor": "ink",
    },
    "古文雅意": {
        "bg": "#fdfcf8",
        "card_bg": "linear-gradient(175deg, #fefdfa 0%, #f8f5ed 40%, #f0ecd8 100%)",
        "text": "#3c3028",
        "accent": "#8b7355",
        "muted": "#b0a590",
        "font_title": "'Noto Serif SC', 'STKaiti', 'KaiTi', serif",
        "font_body": "'Noto Serif SC', 'Georgia', serif",
        "seal_color": "#6b4f3a",
        "prompt": """引用或化用与「{keyword}」相关的经典古文（归有光、苏轼、韩愈、柳宗元、张岱、沈复等）。
先写一段最贴切的古文原文（标注作者和篇名），再用白话写一句简短的意境解读。
整体风格：文人士大夫气，简淡深远，有金石之气。""",
        "decor": "retro",
    },
    "散文光阴": {
        "bg": "#fdfaf5",
        "card_bg": "linear-gradient(175deg, #fefdfa 0%, #faf6ee 40%, #f5edd8 100%)",
        "text": "#4a3525",
        "accent": "#c49560",
        "muted": "#b0a088",
        "font_title": "'Noto Serif SC', 'Georgia', serif",
        "font_body": "'Noto Serif SC', 'Georgia', serif",
        "seal_color": "#8b5e3c",
        "prompt": """引用或化用与「{keyword}」相关的近现代散文名句（朱自清、汪曾祺、余光中、沈从文、张爱玲等）。
先写一段最贴切的散文原文或化用（标注作者），再用白话写一句简短的意境解读。
整体风格：细腻、温柔、有人间烟火气。""",
        "decor": "retro",
    },
}

CARD_PROMPT = """你是一个精通中国古典文学和现代散文的学者。

用户输入了关键词：「{keyword}」

{style_guide}

请严格用JSON格式输出（不要markdown包裹，不要多余文字）：
{{"quote":"引用的原文名句","source":"作者 · 作品名","paraphrase":"白话意境解读，15-25字","emotion":"2-4字情绪词"}}"""
