import asyncio

from tqdm import tqdm
from tqdm.asyncio import tqdm as async_tqdm

from api_client import generate_conversation, generate_conversation_async
from config import *
from file_manager import load_json_file, load_processed_indices, save_processed_index, save_jsonl
from tokenizer import get_token_count, split_text_into_chunks


async def process_chunks_async(data_id, chunks):
    """
    Asynchronously process all chunks of a raw_text.
    If any chunk fails, return None, indicating the entire data_id is skipped.
    """
    results = []
    for chunk in chunks:
        content = chunk + "\n\n\n" + PROMPT

        try:
            # Call the asynchronous generation API
            generated_text = await generate_conversation_async(content)

            # Check the token count of the generated result
            generated_tokens = get_token_count(generated_text)
            if generated_tokens < MIN_GENERATED_TOKEN_LENGTH:
                print(f"Discarded chunk: generated text too short ({generated_tokens} tokens).")
                continue

            results.append(generated_text)
        except Exception as e:
            print(f"Error processing id {data_id}, chunk failed: {e}")
            # If any chunk fails, return None immediately
            return None

    return data_id, results


def process_chunks_sync(data_id, chunks):
    """
    Synchronously process all chunks of a raw_text.
    If any chunk fails, return None, indicating the entire data_id is skipped.
    """
    results = []
    for chunk in chunks:
        content = chunk + "\n\n\n" + PROMPT

        try:
            # Call the synchronous generation API
            generated_text = generate_conversation(content)

            # Check the token count of the generated result
            generated_tokens = get_token_count(generated_text)
            if generated_tokens < MIN_GENERATED_TOKEN_LENGTH:
                print(f"Discarded chunk: generated text too short ({generated_tokens} tokens).")
                continue

            results.append(generated_text)
        except Exception as e:
            print(f"Error processing id {data_id}, chunk failed: {e}")
            # If any chunk fails, return None immediately
            return None

    return data_id, results


async def save_results(save_queue):
    """
    Continuously retrieve generated results from the queue and save them to the file.
    """
    while True:
        item = await save_queue.get()
        if item is None:
            break  # Queue end signal
        index, results = item

        # Save the generated results
        for text in results:
            save_jsonl(OUTPUT_FILE_PATH, {"id": index, "text": text})

        # Update the processed indices
        save_processed_index(PROCESSED_INDICES_FILE, index)

        save_queue.task_done()


async def main_async():
    """
    Asynchronous main logic to support processing multiple raw_texts simultaneously.
    """
    # Load input data
    raw_text_col = load_json_file(INPUT_FILE_PATH, limit=DATA_ROW_LIMIT)

    # Load processed indices
    processed_indices = load_processed_indices(PROCESSED_INDICES_FILE)

    # Create a save queue
    save_queue = asyncio.Queue()

    # Start the save task
    save_task = asyncio.create_task(save_results(save_queue))

    # Limit the number of concurrent tasks
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async def limited_process_chunks_async(data_id, chunks):
        async with semaphore:
            return await process_chunks_async(data_id, chunks)

    # Create a list of tasks
    tasks = []
    for _, row in raw_text_col.iterrows():
        data_id, raw_text = row['id'], row['text']
        if data_id in processed_indices:
            continue

        chunks = split_text_into_chunks(raw_text, TOKEN_LIMIT)
        tasks.append(asyncio.create_task(limited_process_chunks_async(data_id, chunks)))

    # Use async_tqdm to display task progress
    for task in async_tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        result = await task
        if result is None:  # Skip saving if processing failed
            continue

        data_id, results = result
        # Put the result into the save queue
        await save_queue.put((data_id, results))

    # Wait for all saves to complete
    await save_queue.join()
    save_queue.put_nowait(None)  # Send end signal
    await save_task


def main_sync():
    """
    Synchronous main logic.
    """
    # Load input data
    raw_text_col = load_json_file(INPUT_FILE_PATH, limit=DATA_ROW_LIMIT)

    # Load processed indices
    processed_indices = load_processed_indices(PROCESSED_INDICES_FILE)

    # Process data synchronously and display progress
    for _, row in tqdm(raw_text_col.iterrows(), total=len(raw_text_col)):
        data_id, raw_text = row['id'], row['text']
        if data_id in processed_indices:
            continue

        chunks = split_text_into_chunks(raw_text, TOKEN_LIMIT)
        result = process_chunks_sync(data_id, chunks)
        if result is None:  # Skip saving if processing failed
            continue

        data_id, results = result

        # Save the generated results
        for text in results:
            save_jsonl(OUTPUT_FILE_PATH, {"id": data_id, "text": text})

        # Update the processed indices
        save_processed_index(PROCESSED_INDICES_FILE, data_id)


if __name__ == "__main__":
    if USE_ASYNC:
        asyncio.run(main_async())
    else:
        main_sync()
