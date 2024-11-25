from zhipuai import ZhipuAI

from config import API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, TOP_P

# 初始化 ZhipuAI 客户端
client = ZhipuAI(api_key=API_KEY)


def generate_conversation(content, model=MODEL_NAME, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, top_p=TOP_P):
    """
    调用 ZhipuAI 模型生成对话。
    """
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message.content
