"""DeepSeek API 客户端封装"""

from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE, MAX_TOKENS

_client = None


def get_client() -> OpenAI:
    """获取或创建 DeepSeek 客户端（兼容 OpenAI SDK）"""
    global _client
    if _client is None:
        # 运行时读取 config，支持动态设置 API key
        import config
        _client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
    return _client


def reset_client():
    """重置客户端（API key 变更后调用）"""
    global _client
    _client = None


def chat(messages: list[dict], temperature: float = TEMPERATURE) -> str:
    """发送聊天请求，返回文本回复

    Args:
        messages: OpenAI 格式的消息列表
        temperature: 温度参数

    Returns:
        模型回复文本
    """
    client = get_client()
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content


def check_api_key() -> bool:
    """检查 API key 是否已配置"""
    return bool(DEEPSEEK_API_KEY)
