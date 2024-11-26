import asyncio

from tqdm import tqdm
from tqdm.asyncio import tqdm as async_tqdm

from api_client import generate_conversation, generate_conversation_async
from config import *
from file_manager import load_json_file, load_processed_indices, save_processed_index, save_jsonl
from tokenizer import get_token_count, split_text_into_chunks


async def process_chunks_async(data_id, chunks):
    """
    异步处理一个 raw_text 的所有 chunks。
    如果任何一个 chunk 处理失败，则返回 None，表示放弃整个 data_id。
    """
    results = []
    for chunk in chunks:
        content = chunk + "\n\n\n" + PROMPT

        try:
            # 调用异步生成 API
            generated_text = await generate_conversation_async(content)

            # 检查生成结果 token 数
            generated_tokens = get_token_count(generated_text)
            if generated_tokens < MIN_GENERATED_TOKEN_LENGTH:
                print(f"Discarded chunk: generated text too short ({generated_tokens} tokens).")
                continue

            results.append(generated_text)
        except Exception as e:
            print(f"Error processing id {data_id}, chunk failed: {e}")
            # 如果任何一个 chunk 失败，直接返回 None
            return None

    return data_id, results


def process_chunks_sync(data_id, chunks):
    """
    同步处理一个 raw_text 的所有 chunks。
    如果任何一个 chunk 处理失败，则返回 None，表示放弃整个 data_id。
    """
    results = []
    for chunk in chunks:
        content = chunk + "\n\n\n" + PROMPT

        try:
            # 调用同步生成 API
            generated_text = generate_conversation(content)

            # 检查生成结果 token 数
            generated_tokens = get_token_count(generated_text)
            if generated_tokens < MIN_GENERATED_TOKEN_LENGTH:
                print(f"Discarded chunk: generated text too short ({generated_tokens} tokens).")
                continue

            results.append(generated_text)
        except Exception as e:
            print(f"Error processing id {data_id}, chunk failed: {e}")
            # 如果任何一个 chunk 失败，直接返回 None
            return None

    return data_id, results


async def save_results(save_queue):
    """
    持续从队列中获取生成结果，并保存到文件。
    """
    while True:
        item = await save_queue.get()
        if item is None:
            break  # 队列结束信号
        index, results = item

        # 保存生成结果
        for text in results:
            save_jsonl(OUTPUT_FILE_PATH, {"id": index, "text": text})

        # 更新已处理索引
        save_processed_index(PROCESSED_INDICES_FILE, index)

        save_queue.task_done()


async def main_async():
    """
    异步处理主逻辑，支持同时处理多个 raw_text。
    """
    # 加载输入数据
    raw_text_col = load_json_file(INPUT_FILE_PATH, limit=DATA_ROW_LIMIT)

    # 加载已处理的索引
    processed_indices = load_processed_indices(PROCESSED_INDICES_FILE)

    # 创建保存队列
    save_queue = asyncio.Queue()

    # 启动保存任务
    save_task = asyncio.create_task(save_results(save_queue))

    # 限制并发任务数
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async def limited_process_chunks_async(data_id, chunks):
        async with semaphore:
            return await process_chunks_async(data_id, chunks)

    # 创建任务列表
    tasks = []
    for _, row in raw_text_col.iterrows():
        data_id, raw_text = row['id'], row['text']
        if data_id in processed_indices:
            continue

        chunks = split_text_into_chunks(raw_text, TOKEN_LIMIT)
        tasks.append(asyncio.create_task(limited_process_chunks_async(data_id, chunks)))

    # 使用 async_tqdm 显示任务进度
    for task in async_tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        result = await task
        if result is None:  # 如果处理失败，则跳过保存
            continue

        data_id, results = result
        # 将结果放入保存队列
        await save_queue.put((data_id, results))

    # 等待所有保存完成
    await save_queue.join()
    save_queue.put_nowait(None)  # 发送结束信号
    await save_task


def main_sync():
    """
    同步处理主逻辑。
    """
    # 加载输入数据
    raw_text_col = load_json_file(INPUT_FILE_PATH, limit=DATA_ROW_LIMIT)

    # 加载已处理的索引
    processed_indices = load_processed_indices(PROCESSED_INDICES_FILE)

    # 同步处理数据并显示进度
    for _, row in tqdm(raw_text_col.iterrows(), total=len(raw_text_col)):
        data_id, raw_text = row['id'], row['text']
        if data_id in processed_indices:
            continue

        chunks = split_text_into_chunks(raw_text, TOKEN_LIMIT)
        result = process_chunks_sync(data_id, chunks)
        if result is None:  # 如果处理失败，则跳过保存
            continue

        data_id, results = result

        # 保存生成结果
        for text in results:
            save_jsonl(OUTPUT_FILE_PATH, {"id": data_id, "text": text})

        # 更新已处理索引
        save_processed_index(PROCESSED_INDICES_FILE, data_id)


if __name__ == "__main__":
    if USE_ASYNC:
        asyncio.run(main_async())
    else:
        main_sync()
