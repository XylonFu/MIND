# import re
#
# import requests
#
# from config import API_KEY, TOKENIZER_URL

import tiktoken


def split_text_into_chunks(text, token_limit, model="gpt-4o"):
    """
    Split the text into multiple chunks, ensuring that the number of tokens in each chunk
    does not exceed the specified limit while preserving the original text format.
    """
    # Initialize the encoder
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(text)

    # Directly split tokens into chunks
    chunks = [tokens[i:i + token_limit] for i in range(0, len(tokens), token_limit)]

    # Decode all chunks only at the end
    return [encoder.decode(chunk) for chunk in chunks]


def get_token_count(text, model="gpt-4o"):
    """
    Get the token count for the given text.
    """
    # Initialize the encoder
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(text)
    return len(tokens)

# def get_token_count(text, model):
#     """
#     调用 ZhipuAI Tokenizer API 获取文本的 token 数量。
#     如果文本长度超过2048字符，将其分割成多个片段分别处理。
#     """
#     headers = {
#         "Authorization": API_KEY,
#         "Content-Type": "application/json"
#     }
#     max_chunk_size = 2048  # 最大字符数
#     total_tokens = 0
#
#     # 将文本分割成不超过2048字符的片段
#     chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
#
#     for chunk in chunks:
#         payload = {
#             "model": model,
#             "messages": [{"role": "user", "content": chunk}]
#         }
#         response = requests.post(TOKENIZER_URL, headers=headers, json=payload)
#         response_data = response.json()
#
#         # 检查 'usage' 和 'prompt_tokens' 字段是否存在
#         if "usage" in response_data and "prompt_tokens" in response_data["usage"]:
#             total_tokens += response_data["usage"]["prompt_tokens"]
#         else:
#             raise KeyError(f"Unexpected response structure: {response_data}")
#
#     return total_tokens


# def split_text_into_chunks(text, max_tokens, model, avg_chars_per_token=1.8):
#     """
#     将文本按 token 限制切分为多个子块，保留原始文本结构，减少 API 请求次数。
#     """
#     chunks = []
#
#     # 首先检查整个文本的 token 数量
#     total_token_count = get_token_count(text, model)
#     if total_token_count <= max_tokens:
#         # 如果总 token 数量小于等于限制，直接返回整个文本作为一个 chunk
#         return [text]
#
#     text_length = len(text)
#     start = 0
#
#     while start < text_length:
#         # 找到所有换行符的位置，包括开始和结束位置
#         positions = [match.start() + 1 for match in re.finditer('\n', text[start:])]
#         positions = [start] + [start + pos for pos in positions] + [text_length]
#
#         # 初始化二分查找的边界
#         low = 0
#         high = len(positions) - 1
#         best_pos = start
#
#         # 二分查找最佳切分点（使用估计的 token 数）
#         while low <= high:
#             mid = (low + high) // 2
#             end = positions[mid]
#             substring = text[start:end]
#             estimated_token_count = len(substring) / avg_chars_per_token
#
#             if estimated_token_count <= max_tokens:
#                 best_pos = end  # 更新最佳位置
#                 low = mid + 1
#             else:
#                 high = mid - 1
#
#         # 在找到的最佳位置处获取实际的 token 数量
#         substring = text[start:best_pos]
#         actual_token_count = get_token_count(substring, model)
#
#         # 如果实际的 token 数超过限制，向前调整切分点
#         if actual_token_count > max_tokens:
#             # 向前移动切分点，直到满足条件
#             while actual_token_count > max_tokens and best_pos > start:
#                 # 找到上一个可能的切分点
#                 best_pos_index = positions.index(best_pos)
#                 if best_pos_index > 0:
#                     best_pos = positions[best_pos_index - 1]
#                 else:
#                     # 无法再向前调整
#                     break
#
#                 substring = text[start:best_pos]
#                 actual_token_count = get_token_count(substring, model)
#
#             if best_pos == start:
#                 # 如果无法找到合适的切分点，强制切分固定长度的字符
#                 approx_end = start + int(max_tokens * avg_chars_per_token)
#                 end = min(approx_end, text_length)
#                 substring = text[start:end]
#                 actual_token_count = get_token_count(substring, model)
#
#                 # 如果仍然超过限制，则逐字符减少
#                 while actual_token_count > max_tokens and end > start:
#                     end -= 1
#                     substring = text[start:end]
#                     actual_token_count = get_token_count(substring, model)
#
#                 if start == end:
#                     raise ValueError("无法切分文本，因为单个字符的 token 数量超过限制。")
#
#                 best_pos = end
#
#         # 添加当前块到结果列表
#         chunk = text[start:best_pos]
#         chunks.append(chunk)
#
#         # 更新起始位置
#         start = best_pos
#
#     return chunks
