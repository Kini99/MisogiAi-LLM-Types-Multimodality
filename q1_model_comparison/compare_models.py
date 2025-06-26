import argparse
import os
from dotenv import load_dotenv
load_dotenv()
import openai
from openai import OpenAI
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import sys
from huggingface_hub import login
# Placeholder imports for API clients (to be implemented)
# import openai
# from google.generativeai import GenerativeModel
# from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_INFO = {
    'openai': {
        'base': {
            'name': 'davinci-002',
            'desc': 'OpenAI Base model (~6.7B). No instruction tuning.'
        },
        'instruct': {
            'name': 'gpt-4o',
            'desc': 'OpenAI Instruct model (Multimodal). Strong instruction following.'
        },
        'finetuned': {
            'name': 'ft:gpt-3.5-turbo-1106:*',
            'desc': 'OpenAI Fine-tuned model (20B+). Custom fine-tuning.'
        }
    },
    'gemini': {
        'base': {
            'name': 'gemini-1.5-pro',
            'desc': 'Gemini-1.5-Pro Base (Mixture-of-Experts). Underlying reasoning model, system prompt off.'
        },
        'instruct': {
            'name': 'gemini-1.5-pro',
            'desc': 'Gemini-1.5-Pro Instruct (~300B MoE). State-of-the-art instruction-following.'
        }
    },
    'huggingface': {
        'base': {
            'name': 'meta-llama/Llama-2-7b-hf',
            'desc': 'Meta Llama-2 7B Base. No instruction tuning.'
        },
        'instruct': {
            'name': 'mistralai/Mistral-7B-Instruct-v0.1',
            'desc': 'Mistral-7B Instruct. Instruction-tuned.'
        },
        'finetuned': {
            'name': 'ehartford/dolphin-2.2.1-mistral-7b',
            'desc': 'Dolphin 2.2.1 Mistral-7B. Fine-tuned.'
        }
    }
}

def parse_args():
    parser = argparse.ArgumentParser(description='Compare LLM model types across providers.')
    parser.add_argument('--query', type=str, required=True, help='User input query for the model.')
    parser.add_argument('--provider', type=str, choices=['openai', 'gemini', 'huggingface'], required=True, help='Model provider.')
    parser.add_argument('--type', type=str, choices=['base', 'instruct', 'finetuned'], required=True, help='Model type.')
    parser.add_argument('--visualize', action='store_true', help='Visualize token usage and context window.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')
    return parser.parse_args()

def get_model_info(provider, model_type):
    return MODEL_INFO.get(provider, {}).get(model_type, None)

def get_latest_finetune():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    jobs = client.fine_tuning.jobs.list(limit=20)
    for job in jobs.data:
        if job.status == "succeeded" and job.fine_tuned_model:
            return job.fine_tuned_model
    return None


def call_openai(model_type, query, debug=False):
    api_key = os.getenv('OPENAI_API_KEY')
    if debug:
        print(f"[DEBUG] OPENAI_API_KEY: {api_key}")
    if not api_key:
        raise ValueError('OPENAI_API_KEY not set in environment.')

    client = OpenAI(api_key=api_key)
    
    if model_type == 'finetuned':
        real_ft = get_latest_finetune()
        if not real_ft:
            raise ValueError("No completed fine-tune found for 'finetuned' model type.")
        model = real_ft
    else:
        model = model_map[model_type]

    model_map = {
        'base': 'davinci-002',
        'instruct': 'gpt-4o',
        'finetuned': real_ft,
    }
    model = model_map[model_type]

    chat_models = {'gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'ft:gpt-3.5-turbo-1106:*'}

    if model in chat_models:
        messages = (
            [{"role": "user", "content": query}]
            if model_type == 'base'
            else [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        )
        resp = client.chat.completions.create(model=model, messages=messages, max_tokens=512)
        text = resp.choices[0].message.content.strip()
        usage = resp.usage
        total = getattr(usage, 'total_tokens', None)

        return text, {
            'tokens_used': total if total is not None else 'N/A',
            'context_window': 128_000 if model.startswith('gpt-4o') else 16_384
        }

    else:
        resp = client.completions.create(model=model, prompt=query, max_tokens=512)
        text = resp.choices[0].text.strip()
        usage = resp.usage
        total = getattr(usage, 'total_tokens', None)

        return text, {
            'tokens_used': total if total is not None else 'N/A',
            'context_window': 4_096
        }

def call_gemini(model_type, query, debug=False):
    api_key = os.getenv('GEMINI_API_KEY')
    if debug:
        print(f"[DEBUG] GEMINI_API_KEY: {api_key}")
    if not api_key:
        raise ValueError('GEMINI_API_KEY not set in environment.')
    genai.configure(api_key=api_key)
    model = 'gemini-1.5-pro'
    gen_model = genai.GenerativeModel(model)
    response = gen_model.generate_content(query)
    tokens_used = getattr(response, 'usage_metadata', {}).get('total_tokens', 'N/A')
    context_window = 1048576  # 1M tokens for Gemini 1.5 Pro
    return response.text, {'tokens_used': tokens_used, 'context_window': context_window}

def call_huggingface(model_type, query, debug=False):
    model_map = {
        'base': 'meta-llama/Llama-2-7b-hf',
        'instruct': 'mistralai/Mistral-7B-Instruct-v0.1',
        'finetuned': 'ehartford/dolphin-2.2.1-mistral-7b'
    }
    model_id = model_map[model_type]
    if debug:
        print(f"[DEBUG] Loading Hugging Face model: {model_id}")
    login(token=os.getenv("HF_TOKEN"))
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
    pipe = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)
    prompt = query
    output = pipe(prompt, max_new_tokens=512, do_sample=True, temperature=0.7, top_p=0.95)
    text = output[0]['generated_text']
    tokens_used = len(tokenizer.encode(prompt)) + len(tokenizer.encode(text))
    context_windows = {
        'meta-llama/Llama-2-7b-hf': 4096,
        'mistralai/Mistral-7B-Instruct-v0.1': 8192,
        'ehartford/dolphin-2.2.1-mistral-7b': 16384
    }
    context_window = context_windows.get(model_id, 'N/A')
    return text, {'tokens_used': tokens_used, 'context_window': context_window}

def call_model_api(provider, model_type, query, debug=False):
    try:
        if provider == 'openai':
            return call_openai(model_type, query, debug=debug)
        elif provider == 'gemini':
            return call_gemini(model_type, query, debug=debug)
        elif provider == 'huggingface':
            return call_huggingface(model_type, query, debug=debug)
        else:
            raise ValueError(f'Unknown provider: {provider}')
    except Exception as e:
        print(f"[ERROR] Exception in call_model_api: {e}", file=sys.stderr)
        raise

def main():
    args = parse_args()
    debug = getattr(args, 'debug', False)
    if debug:
        print(f"[DEBUG] ENV: {dict(os.environ)}")
    model_info = get_model_info(args.provider, args.type)
    if not model_info:
        print('Model type not available for this provider.')
        return
    print(f"\n[Model: {model_info['name']}]\n{model_info['desc']}\n")
    try:
        response, usage = call_model_api(args.provider, args.type, args.query, debug=debug)
        print(f"Response:\n{response}\n")
        if args.visualize:
            print(f"[Token Usage: {usage['tokens_used']}, Context Window: {usage['context_window']}]\n")
        print(f"Summary: {model_info['desc']}")
    except Exception as e:
        print(f"[ERROR] Exception in main: {e}", file=sys.stderr)

if __name__ == '__main__':
    main() 