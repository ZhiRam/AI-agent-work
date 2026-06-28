"""配置管理"""

import os

# DeepSeek API 配置（优先级：环境变量 > Streamlit secrets）
_api_key = os.getenv("DEEPSEEK_API_KEY", "")
if not _api_key:
    try:
        import streamlit as st
        _api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    except Exception:
        pass
DEEPSEEK_API_KEY = _api_key
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 对话参数
TEMPERATURE = 0.9
MAX_TOKENS = 512

# 记忆参数
SHORT_TERM_SIZE = 20       # 短期记忆条数
LONG_TERM_MAX = 50         # 长期记忆最大条数
CONTEXT_ROUNDS = 5         # 每次注入上下文的最近对话轮数
