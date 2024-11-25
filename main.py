from tqdm import tqdm

from api_client import generate_conversation
from config import *
from file_manager import load_parquet_file, load_processed_indices, save_processed_index, save_jsonl
from tokenizer import get_token_count, split_text_into_chunks

# 加载输入数据
raw_text_col = load_parquet_file(INPUT_FILE_PATH, limit=10)

# 加载已处理的索引
processed_indices = load_processed_indices(PROCESSED_INDICES_FILE)

# 处理数据并实时写入输出
for index, raw_text in tqdm(enumerate(raw_text_col), total=len(raw_text_col)):
    if index in processed_indices:
        continue  # 跳过已处理的行

    # 切分文本为子块
    chunks = split_text_into_chunks(raw_text, TOKEN_LIMIT)

    try:
        for chunk in chunks:
            # 准备内容
            content = chunk + "\n\n\n" + PROMPT

            # 调用生成 API
            generated_text = generate_conversation(content)

            # 检查生成结果 token 数
            generated_tokens = get_token_count(generated_text)
            if generated_tokens < MIN_GENERATED_TOKEN_LENGTH:
                print(f"Discarded chunk: generated text too short ({generated_tokens} tokens).")
                continue  # 丢弃长度不足的结果

            # 保存生成结果
            save_jsonl(OUTPUT_FILE_PATH, {"id": index, "text": generated_text})

        # 更新已处理索引
        save_processed_index(PROCESSED_INDICES_FILE, index)

    except Exception as e:
        print(f"Error processing index {index}: {e}")
