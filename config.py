import os

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# API 配置
API_KEY = os.getenv("API_KEY")
TOKENIZER_URL = "https://open.bigmodel.cn/api/paas/v4/tokenizer"

# 文件路径配置
INPUT_FILE_PATH = "data/train-00000-of-00114.parquet"
PROCESSED_INDICES_FILE = "data/processed_indices.txt"
OUTPUT_FILE_PATH = "data/MIND-OWM-00000-of-00114.jsonl"

# 模型配置
MODEL_NAME = "glm-4-flash"
MAX_TOKENS = 4096
TEMPERATURE = 1.0
TOP_P = 0.9
PROMPT = (
    "Convert the context above as a multi-turn discussions between a teacher and a student. "
    "The student has questions about the context and the teacher solves each of them step-by-step. "
    "Make sure that their discussions strictly adhere to the context above and remains faithful to information in the context. "
    "Please DONOT add any new information/reference other than the context."
)

# Token 配置
TOKEN_LIMIT = 500
MIN_GENERATED_TOKEN_LENGTH = 50
