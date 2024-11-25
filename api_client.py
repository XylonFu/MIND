import asyncio

from zhipuai import ZhipuAI

from config import API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, TOP_P, ASYNC_CHECK_INTERVAL, ASYNC_MAX_RETRIES

# 初始化 ZhipuAI 客户端
client = ZhipuAI(api_key=API_KEY)


def generate_conversation(content, model=MODEL_NAME, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, top_p=TOP_P):
    """
    调用 ZhipuAI 模型生成对话（同步方式）。
    """
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message.content


async def generate_conversation_async(content, model=MODEL_NAME, max_tokens=MAX_TOKENS, temperature=TEMPERATURE,
                                      top_p=TOP_P):
    """
    调用 ZhipuAI 模型生成对话（异步方式）。
    """
    response = await asyncio.to_thread(
        client.chat.asyncCompletions.create,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        messages=[{"role": "user", "content": content}],
    )

    task_id = response.id
    task_status = ""
    retries = 0

    # 查询任务结果
    while task_status != "SUCCESS" and task_status != "FAILED" and retries < ASYNC_MAX_RETRIES:
        result_response = await asyncio.to_thread(
            client.chat.asyncCompletions.retrieve_completion_result,
            id=task_id,
        )
        task_status = result_response.task_status

        if task_status == "SUCCESS":
            return result_response.choices[0].message.content

        await asyncio.sleep(ASYNC_CHECK_INTERVAL)
        retries += 1

    raise Exception(f"Async task failed or timed out (task_id: {task_id}, status: {task_status})")
