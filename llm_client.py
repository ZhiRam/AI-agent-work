"""API 客户端封装"""

import base64
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, VISION_MODEL, TEMPERATURE, MAX_TOKENS

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
            timeout=60.0,  # 60秒超时
        )
    return _client


def reset_client():
    """重置客户端（API key 变更后调用）"""
    global _client
    _client = None


def chat(messages: list[dict], temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> str:
    """发送聊天请求，返回文本回复

    Args:
        messages: OpenAI 格式的消息列表
        temperature: 温度参数
        max_tokens: 最大输出 token 数

    Returns:
        模型回复文本
    """
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=45.0,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ API 调用失败：{str(e)}"


def chat_vision(text_prompt: str, image_base64_list: list[str], temperature: float = 0.7) -> str:
    """发送图片给视觉模型，返回文本分析

    Args:
        text_prompt: 文字提示
        image_base64_list: base64 编码的图片列表
        temperature: 温度参数

    Returns:
        模型回复文本
    """
    client = get_client()

    # 构建 content 数组：[text, image1, image2, ...]
    content = [{"type": "text", "text": text_prompt}]
    for img_b64 in image_base64_list:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img_b64}"},
        })

    messages = [{"role": "user", "content": content}]
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
            timeout=90.0,  # 视觉模型较慢，90秒超时
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 视觉模型调用失败：{str(e)}"


def check_api_key() -> bool:
    """检查 API key 是否已配置（运行时读取，支持动态更新）"""
    import config
    return bool(config.DEEPSEEK_API_KEY)
