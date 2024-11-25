import json

import pandas as pd


def load_parquet_file(file_path, limit=None):
    """
    加载 parquet 文件并返回文本列。
    """
    df = pd.read_parquet(file_path)
    return df["text"][:limit]


def load_processed_indices(file_path):
    """
    加载已处理的索引文件。
    """
    try:
        with open(file_path, "r") as file:
            return set(map(int, file.read().splitlines()))
    except FileNotFoundError:
        return set()


def save_processed_index(file_path, index):
    """
    保存已处理的索引。
    """
    with open(file_path, "a") as file:
        file.write(f"{index}\n")


def save_jsonl(file_path, data):
    """
    将数据追加写入 JSONL 文件。
    """
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
