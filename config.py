import os

from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# API configuration
API_KEY = os.getenv("API_KEY")
TOKENIZER_URL = "https://open.bigmodel.cn/api/paas/v4/tokenizer"

# File configuration
INPUT_FILE_PATH = "data/MATH.json"
PROCESSED_INDICES_FILE = "data/processed_indices.txt"
OUTPUT_FILE_PATH = "data/MIND-MATH-2.jsonl"

# Data configuration
DATA_ROW_LIMIT = 3000

# Model configuration
MODEL_NAME = "glm-4-flash"
MAX_TOKENS = 4096
TEMPERATURE = 1.0
TOP_P = 0.9
PROMPT = (
    "Convert the context above as a multi-turn discussions between a teacher and a student. "
    "The teacher starts from the basics and guides the student step-by-step to learn and solve the problem. "
    "Make sure that their discussions strictly adhere to the context above and remains faithful to information in the context."
)

# Token configuration
TOKEN_LIMIT = 8096
MIN_GENERATED_TOKEN_LENGTH = 0

# Asynchronous configuration
USE_ASYNC = True
MAX_CONCURRENT_TASKS = 100
ASYNC_CHECK_INTERVAL = 10
ASYNC_MAX_RETRIES = 60
