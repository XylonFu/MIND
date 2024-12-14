import json

import pandas as pd


def load_json_file(file_path, limit=None):
    # Load JSON data from a file and convert it to a Pandas DataFrame
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    df = pd.DataFrame(data)

    if limit:
        try:
            # Attempt to sample evenly across 'level' and 'type' columns
            sampled_df = (
                df.groupby(['level', 'type'])
                .apply(lambda x: x.sample(n=min(len(x), limit // len(df['level'].unique()) // len(df['type'].unique())),
                                          random_state=42))
                .reset_index(drop=True)
            )
            # If the sampled result is less than the limit, raise an exception to switch to sampling by 'level' only
            if len(sampled_df) < limit:
                raise ValueError(
                    "Insufficient samples for even sampling across 'level' and 'type'. Switching to 'level' only.")
        except Exception:
            try:
                # Sample evenly by the 'level' column
                sampled_df = (
                    df.groupby('level')
                    .apply(lambda x: x.sample(n=min(len(x), limit // len(df['level'].unique())), random_state=42))
                    .reset_index(drop=True)
                )
                # If sampling by 'level' still results in less than the limit, raise an exception to switch to random sampling
                if len(sampled_df) < limit:
                    raise ValueError(
                        "Insufficient samples for even sampling across 'level'. Falling back to random sampling.")
            except Exception:
                # Final fallback: Random sampling across the entire dataset
                sampled_df = df.sample(n=limit, random_state=42)
    else:
        sampled_df = df

    # Combine the 'problem' and 'solution' columns into a single 'text' column
    sampled_df['text'] = sampled_df.apply(
        lambda row: f"Problem:\n{row['problem']}\n\nSolution:\n{row['solution']}", axis=1
    )

    # Return a DataFrame containing only the 'id' and 'text' columns
    return sampled_df[['id', 'text']]


def load_parquet_file(file_path, limit=None):
    """
    Load a parquet file and return a DataFrame containing 'id' and 'text'.
    If the 'id' column is missing, generate a unique 'id' column.
    """
    # Read the parquet file
    df = pd.read_parquet(file_path)

    # Check if the 'id' column exists; if not, generate it
    if 'id' not in df.columns:
        df['id'] = range(1, len(df) + 1)

    # Truncate the data based on the limit
    if limit:
        df = df[:limit]

    # Return a DataFrame containing only the 'id' and 'text' columns
    return df[['id', 'text']]


def load_processed_indices(file_path):
    """
    Load the processed indices file.
    """
    try:
        with open(file_path, "r") as file:
            return set(map(int, file.read().splitlines()))
    except FileNotFoundError:
        return set()


def save_processed_index(file_path, index):
    """
    Save a processed index.
    """
    with open(file_path, "a") as file:
        file.write(f"{index}\n")


def save_jsonl(file_path, data):
    """
    Append data to a JSONL file.
    """
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
