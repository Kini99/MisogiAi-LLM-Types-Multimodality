# Model Comparison CLI Tool

This command-line tool helps you compare Base, Instruct, and Fine-tuned models from OpenAI, Gemini (Google), and Hugging Face.

## Setup

1. Clone the repository and navigate to the `q1_model_comparison` folder.
2. Install Python 3.8+ and required packages (see below).
3. Copy `example.env` to `.env` and fill in your API keys.

```
cp .example.env .env
```

4. Install dependencies (e.g., `openai`, `google-generativeai`, `transformers`, `python-dotenv`).

```
pip install openai google-generativeai transformers python-dotenv
```

## Usage

Run the script with your query, provider, and model type:

```
python compare_models.py --query "What is the capital of France?" --provider openai --type instruct
```

Options:
- `--query`: The prompt to send to the model.
- `--provider`: `openai`, `gemini`, or `huggingface`.
- `--type`: `base`, `instruct`, or `finetuned` (not all types available for all providers).
- `--visualize`: (Optional) Show token usage and context window.

## Example

```
python compare_models.py --query "Explain quantum entanglement." --provider gemini --type instruct --visualize
```

## Notes
- You must provide your own API keys in the `.env` file.
- See `comparisons.md` for example outputs and commentary. 