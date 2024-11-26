import os

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 接口配置
API_KEY = os.getenv("API_KEY")
TOKENIZER_URL = "https://open.bigmodel.cn/api/paas/v4/tokenizer"

# 文件配置
INPUT_FILE_PATH = "data/MATH.json"
PROCESSED_INDICES_FILE = "data/processed_indices.txt"
OUTPUT_FILE_PATH = "data/MIND-MATH-1.jsonl"

# 数据配置
DATA_ROW_LIMIT = 3000

# 模型配置
MODEL_NAME = "glm-4-flash"
MAX_TOKENS = 4096
TEMPERATURE = 1.0
TOP_P = 0.9
PROMPT = (
    "Convert the context above as a multi-turn discussions between a teacher and a student. "
    "The teacher starts from the basics and guides the student step-by-step to learn and solve the problem. "
    "Make sure that their discussions strictly adhere to the context above and remains faithful to information in the context."
)

# 词元配置
TOKEN_LIMIT = 8096
MIN_GENERATED_TOKEN_LENGTH = 0

# 异步配置
USE_ASYNC = True
MAX_CONCURRENT_TASKS = 100
ASYNC_CHECK_INTERVAL = 10
ASYNC_MAX_RETRIES = 60
