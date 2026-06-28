"""赛博意境 — AI 艺术卡片 """

STYLE_PROMPTS = {
    "水墨": "用中国水墨画般的意境写一段诗意文字。留白、含蓄、有余韵。像《诗经》遇见王维。20-40字。",
    "赛博朋克": "用霓虹灯下的数字诗人风格写一段文字。故障美学、电子荒原、数据洪流。20-40字。",
    "极简": "用最少的字说最深的话。俳句般的克制，像村上春树的短句。15-30字。",
    "复古": "用民国书信的口吻写一段文字。泛黄信纸、旧时光、温柔的克制。20-40字。",
}

STYLE_COLORS = {
    "水墨": {"bg": "linear-gradient(135deg, #f5f0e8 0%, #e8ddd0 50%, #d5cfc0 100%)",
             "text": "#3d3226", "accent": "#8b7355", "font": "KaiTi, STKaiti, serif"},
    "赛博朋克": {"bg": "linear-gradient(135deg, #0a0a2e 0%, #1a0a3e 50%, #0a1a2e 100%)",
                "text": "#00ffcc", "accent": "#ff00ff", "font": "Consolas, monospace"},
    "极简": {"bg": "linear-gradient(135deg, #ffffff 0%, #f8f8f8 50%, #f0f0f0 100%)",
             "text": "#222222", "accent": "#666666", "font": "sans-serif"},
    "复古": {"bg": "linear-gradient(135deg, #fdf5e6 0%, #f5e6d3 50%, #eedcc8 100%)",
             "text": "#5c4033", "accent": "#8b6914", "font": "Georgia, serif"},
}

CARD_PROMPT = """你是一个诗意AI，擅长用文字创造意境。

用户输入了："{keyword}"

请为「{style}」风格生成一张艺术卡片的内容。用JSON格式输出：

{{
  "title": "卡片标题（4-8字，要有意境）",
  "text": "{style_detail}",
  "footer": "一句签名（5-10字）",
  "emotion": "这张卡片传递的情绪（一个词）"
}}

只输出JSON，不要其他内容。"""

AGENT_CONFIG = {
    "name": "意境",
    "emoji": "🎨",
    "color": "#8b5cf6",
}
