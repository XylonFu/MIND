import asyncio

from tqdm import tqdm
from tqdm.asyncio import tqdm as async_tqdm

from api_client import generate_conversation, generate_conversation_async
from config import *
from file_manager import load_parquet_file, load_processed_indices, save_processed_index, save_jsonl
from tokenizer import get_token_count, split_text_into_chunks


async def process_chunks_async(index, chunks):
    """
    异步处理一个 raw_text 的所有 chunks。
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
            print(f"Error processing index {index}, chunk failed: {e}")

    return index, results


def process_chunks_sync(index, chunks):
    """
    同步处理一个 raw_text 的所有 chunks。
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
            print(f"Error processing index {index}, chunk failed: {e}")

    return index, results


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
    raw_text_col = load_parquet_file(INPUT_FILE_PATH, limit=1000)

    # 加载已处理的索引
    processed_indices = load_processed_indices(PROCESSED_INDICES_FILE)

    # 创建保存队列
    save_queue = asyncio.Queue()

    # 启动保存任务
    save_task = asyncio.create_task(save_results(save_queue))

    # 限制并发任务数
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async def limited_process_chunks_async(index, chunks):
        async with semaphore:
            return await process_chunks_async(index, chunks)

    # 创建任务列表
    tasks = []
    for index, raw_text in enumerate(raw_text_col):
        if index in processed_indices:
            continue

        chunks = split_text_into_chunks(raw_text, TOKEN_LIMIT)
        tasks.append(asyncio.create_task(limited_process_chunks_async(index, chunks)))

    # 使用 async_tqdm 显示任务进度
    for task in async_tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        index, results = await task
        # 将结果放入保存队列
        await save_queue.put((index, results))

    # 等待所有保存完成
    await save_queue.join()
    save_queue.put_nowait(None)  # 发送结束信号
    await save_task


def main_sync():
    """
    同步处理主逻辑。
    """
    # 加载输入数据
    raw_text_col = load_parquet_file(INPUT_FILE_PATH, limit=1000)

    # 加载已处理的索引
    processed_indices = load_processed_indices(PROCESSED_INDICES_FILE)

    # 同步处理数据并显示进度
    for index, raw_text in tqdm(enumerate(raw_text_col), total=len(raw_text_col)):
        if index in processed_indices:
            continue

        chunks = split_text_into_chunks(raw_text, TOKEN_LIMIT)
        index, results = process_chunks_sync(index, chunks)

        # 保存生成结果
        for text in results:
            save_jsonl(OUTPUT_FILE_PATH, {"id": index, "text": text})

        # 更新已处理索引
        save_processed_index(PROCESSED_INDICES_FILE, index)


if __name__ == "__main__":
    if USE_ASYNC:
        asyncio.run(main_async())
    else:
        main_sync()
