# MIND Synthetic Data Generator

This repository provides an implementation for generating synthetic math-informed dialogues inspired by the methodology described in the following paper:

> Syeda Nahida Akter, Shrimai Prabhumoye, John Kamalu, Sanjeev Satheesh, Eric Nyberg, Mostofa Patwary, Mohammad Shoeybi, Bryan Catanzaro.  
> **MIND: Math Informed syNthetic Dialogues for Pretraining LLMs**  
> *arXiv preprint arXiv:2410.12881, 2024*  
> [Link to Paper](https://arxiv.org/pdf/2410.12881)

This codebase is designed to help users preprocess raw math problems and their solutions into multi-turn teacher-student dialogues suitable for continued pretraining of large language models (LLMs). By emulating the approach described in the MIND paper, this repository supports crafting natural, step-by-step tutoring conversations that guide a student through understanding and solving mathematical problems.

## Key Features

- **MIND-Inspired Dialogue Generation**: Converts raw mathematical context (problems and solutions) into multi-turn, structured dialogues where a virtual "teacher" systematically guides a "student" to reason through math problems.
- **Token-Based Text Splitting**: Automatically splits lengthy problem descriptions and solutions into manageable chunks based on a token limit, ensuring compliance with LLM constraints.
- **Asynchronous & Synchronous Processing**: Supports both synchronous and asynchronous processing of texts for efficient scaling.
- **Dynamic Quality Filtering**: Skips over outputs that do not meet minimum quality or length thresholds, helping maintain high-quality dialogue data.
- **Resumable Processing**: Tracks processed indices, allowing the generation process to resume from where it left off without reprocessing previously completed items.

## Repository Structure

- **`api_client.py`**:  
  Handles the interaction with the ZhipuAI LLM API.  
  - `generate_conversation` and `generate_conversation_async` functions invoke the language model to produce dialogues from a given text prompt.

- **`config.py`**:  
  Centralizes all configuration parameters, including API keys, model and tokenization parameters, file paths, and prompt templates.

- **`file_manager.py`**:  
  Manages data input/output.  
  - `load_json_file` and `load_parquet_file` handle loading of input data.  
  - `save_jsonl` appends generated dialogues to a `.jsonl` output file.  
  - Utilities like `load_processed_indices` and `save_processed_index` help maintain resumability.

- **`main.py`**:  
  Orchestrates the entire data generation pipeline.  
  - Loads raw problem data.  
  - Splits texts into token-limited chunks.  
  - Calls the LLM to generate teacher-student dialogues.  
  - Saves generated dialogues to the output JSONL file and records processed indices.

- **`tokenizer.py`**:  
  Provides tokenization utilities using `tiktoken`.  
  - `split_text_into_chunks` divides long texts into manageable segments.  
  - `get_token_count` measures token length to ensure quality and token-limit compliance.

## Getting Started

### 1. Environment Setup

1. **Install Dependencies**:  
   Make sure you have Python 3.9+ installed.  
   Install dependencies by running:  
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Configuration**:  
   Create a `.env` file in the project root and specify your API key:  
   ```plaintext
   API_KEY=your_api_key_here
   ```

   The code uses this key to authenticate calls to the ZhipuAI model.

### 2. Data Preparation

- **Input File**:  
  Place your input math data (problems and solutions) in `data/MATH.json` or configure another file path in `config.py`.
  
- **Data Format**:  
  The input JSON should contain fields like `id`, `problem`, `solution`, `level`, and `type` (if applicable). The code will sample data according to the specified limits and distributions.

### 3. Configuration

Open `config.py` to adjust:
- **Model Settings**:  
  - `MODEL_NAME`, `MAX_TOKENS`, `TEMPERATURE`, `TOP_P`  
- **Prompt Template**:  
  Adjust `PROMPT` to control the style of the generated dialogues.
- **File Paths**:  
  Modify `INPUT_FILE_PATH`, `OUTPUT_FILE_PATH`, `PROCESSED_INDICES_FILE` as needed.

### 4. Running the Pipeline

**Asynchronous Mode (default)**:
```bash
python main.py
```

**Synchronous Mode** (set `USE_ASYNC = False` in `config.py`):
```bash
python main.py
```

As the script runs, it will:
- Load and sample data from `MATH.json`.
- Generate multi-turn dialogues based on the prompt and context.
- Split long content into manageable chunks and handle them individually.
- Save dialogues to `MIND-MATH-2.jsonl`.
- Record processed items in `processed_indices.txt`.

You can monitor the progress via a command-line progress bar.

### 5. Output

The output file (`.jsonl`) will contain entries like:
```json
{"id": 123, "text": "Teacher: Let's start with the basics of this problem... \nStudent: I see, so we first consider..."}
```

Each `id` corresponds to the input problem’s identifier, and `text` is the generated teacher-student dialogue.

## Customization

- **Prompt Engineering**:  
  Experiment with the `PROMPT` in `config.py` to produce different tutoring styles or question-and-answer formats.
- **Chunk Size & Token Limits**:  
  Adjust `TOKEN_LIMIT` in `config.py` to control how text is divided, influencing reasoning depth and complexity.
- **Sampling Strategies**:  
  In `file_manager.py`, the code attempts stratified sampling by `level` and `type`. Adjust these strategies as needed.

## Reference

This implementation is based on the MIND approach introduced in the paper:

> **MIND: Math Informed syNthetic Dialogues for Pretraining LLMs (2024)**  
> *Syeda Nahida Akter, Shrimai Prabhumoye, John Kamalu, Sanjeev Satheesh, Eric Nyberg, Mostofa Patwary, Mohammad Shoeybi, Bryan Catanzaro*  
> [arXiv:2410.12881](https://arxiv.org/pdf/2410.12881)

The MIND methodology inspires turning static math problems into dynamic, instructive dialogues that closely align with real tutoring sessions, potentially enhancing the LLM’s mathematical reasoning and explanatory abilities.

## License

This code is released under the MIT License. See the `LICENSE` file for details.

---

By following these instructions and adapting the provided pipeline, you can generate math-informed synthetic dialogues that serve as valuable pretraining data for LLMs, replicating and extending the insights from the MIND approach.