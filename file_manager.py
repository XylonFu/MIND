import json

import pandas as pd


def load_json_file(file_path, limit=None):
    # 从文件中加载 JSON 数据并转换为 Pandas DataFrame
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    df = pd.DataFrame(data)

    if limit:
        try:
            # 尝试按 level 和 type 两列均匀采样
            sampled_df = (
                df.groupby(['level', 'type'])
                .apply(lambda x: x.sample(n=min(len(x), limit // len(df['level'].unique()) // len(df['type'].unique())),
                                          random_state=42))
                .reset_index(drop=True)
            )
            # 如果采样结果小于限制数量，则抛出异常切换到仅按 level 采样
            if len(sampled_df) < limit:
                raise ValueError(
                    "Insufficient samples for even sampling across 'level' and 'type'. Switching to 'level' only.")
        except Exception:
            try:
                # 按 level 列均匀采样
                sampled_df = (
                    df.groupby('level')
                    .apply(lambda x: x.sample(n=min(len(x), limit // len(df['level'].unique())), random_state=42))
                    .reset_index(drop=True)
                )
                # 如果按 level 采样结果仍小于限制数量，则抛出异常切换到随机采样
                if len(sampled_df) < limit:
                    raise ValueError(
                        "Insufficient samples for even sampling across 'level'. Falling back to random sampling.")
            except Exception:
                # 最终回退：在整个数据集中随机采样
                sampled_df = df.sample(n=limit, random_state=42)
    else:
        sampled_df = df

    # 将 'problem' 和 'solution' 列合并为 'text' 列
    sampled_df['text'] = sampled_df.apply(
        lambda row: f"Problem:\n{row['problem']}\n\nSolution:\n{row['solution']}", axis=1
    )

    # 返回包含 'id' 和 'text' 的 DataFrame
    return sampled_df[['id', 'text']]


def load_parquet_file(file_path, limit=None):
    """
    加载 parquet 文件，并返回包含 'id' 和 'text' 的 DataFrame。
    如果文件中没有 'id' 列，则为其生成唯一的 'id' 列。
    """
    # 读取 parquet 文件
    df = pd.read_parquet(file_path)

    # 检查是否存在 'id' 列，如果没有则生成
    if 'id' not in df.columns:
        df['id'] = range(1, len(df) + 1)

    # 根据 limit 截取数据
    if limit:
        df = df[:limit]

    # 返回包含 'id' 和 'text' 的 DataFrame
    return df[['id', 'text']]


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
