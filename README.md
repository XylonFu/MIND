# MIND Synthetic Data Generator

This repository contains an implementation of the synthetic data generation process described in the paper [MIND: Math Informed Synthetic Dialogues for Pretraining LLMs](https://arxiv.org/pdf/2410.12881). The code focuses on generating high-quality math-informed synthetic dialogues for continued pretraining LLMs, aligning with the principles and methodology highlighted in the paper.

## Features

- **Conversation Generation**: Converts raw mathematical contexts into structured, multi-turn conversations.
- **Token-Based Splitting**: Splits large texts into manageable chunks to optimize input for language models.
- **Dynamic Filtering**: Ensures the generated conversations meet token and quality thresholds.
- **Continuous Preprocessing**: Efficiently processes raw data, tracks progress, and supports resuming interrupted tasks.

## File Overview

### 1. `api_client.py`
Handles the interaction with the ZhipuAI model API to generate synthetic conversations. 

Key Function:
- `generate_conversation(content)`: Generates a structured dialogue based on the provided content and predefined prompts.

### 2. `config.py`
Centralized configuration for the project, including API keys, file paths, model settings, and prompts.

Highlights:
- **Model Parameters**: Configurable token limits, temperature, and top-p settings.
- **Prompt Template**: Ensures consistency in conversation generation styles.

### 3. `file_manager.py`
Manages data I/O operations for handling input and output files in various formats.

Key Functions:
- `load_parquet_file(file_path)`: Reads raw text data from a parquet file.
- `save_jsonl(file_path, data)`: Appends generated data to a JSONL file.

### 4. `main.py`
Main script for orchestrating the data generation workflow, including:
- Loading raw text data.
- Splitting and processing text chunks.
- Generating conversations using the API.
- Saving results and updating progress.

### 5. `tokenizer.py`
Tokenizes and splits text for efficient processing with language models.

Key Functions:
- `split_text_into_chunks(text, token_limit)`: Splits text into chunks based on token limits.
- `get_token_count(text)`: Calculates the token count for a given text.

## Prerequisites

1. **Environment Setup**: Install the required Python libraries using `pip install -r requirements.txt`.
2. **API Key**: Add your API key to the `.env` file in the following format:
   ```plaintext
   API_KEY=your_api_key_here
   ```

## How to Use

1. **Configure Settings**:
   - Update the `config.py` file with your preferred settings, including file paths and model parameters.
   - Prepare your raw data in parquet format and set the path in `INPUT_FILE_PATH`.

2. **Run the Main Script**:
   Execute the `main.py` file to start generating synthetic dialogues:
   ```bash
   python main.py
   ```

3. **Monitor Progress**:
   - Processed indices are logged to prevent redundant processing.
   - Generated data is saved incrementally in the specified JSONL file.

4. **Output**:
   - The generated dialogues are saved in the JSONL format, adhering to the MIND structure.

## Example

```json
{
  "id": 1,
  "text": "Teacher: The problem asks us to calculate how many numbers can be formed using the digits 2, 3, 5, 6, and 7...\nStudent: Why can the digits repeat?..."
}
```

## Customization

- **Adjust Prompts**: Modify the `PROMPT` variable in `config.py` to experiment with different conversational styles.
- **Model Configuration**: Update `MODEL_NAME` and token limits to use other pre-trained models.

## References

- Paper: [MIND: Math Informed Synthetic Dialogues for Pretraining LLMs](https://arxiv.org/pdf/2410.12881)
- Dataset: OpenWebMath (OWM)
- Model: ZhipuAI LLMs

## License

This code is provided under the MIT License. See the `LICENSE` file for more details.

---

Feel free to explore and adapt this repository to generate high-quality synthetic data for pretraining mathematical reasoning in LLMs!
