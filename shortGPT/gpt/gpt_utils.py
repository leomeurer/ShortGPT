import json
import os
import re
from time import sleep, time

import openai
import tiktoken
import yaml

from shortGPT.config.api_db import ApiKeyManager

# Configuração dos providers LLM
LLM_PROVIDERS = {
    "groq": {
        "api_key_name": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "priority": 1  # Maior prioridade (mais rápido e barato)
    },
    "gemini": {
        "api_key_name": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.0-flash-lite-preview-02-05",
        "priority": 2
    },
    "openai": {
        "api_key_name": "OPENAI_API_KEY",
        "base_url": None,  # Usa URL padrão do OpenAI
        "model": "gpt-4o-mini",
        "priority": 3
    }
}

def num_tokens_from_messages(texts, model="gpt-4o-mini"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-4o-mini":  # note: future models may deviate from this
        if isinstance(texts, str):
            texts = [texts]
        score = 0
        for text in texts:
            score += 4 + len(encoding.encode(text))
        return score
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information""")


def extract_biggest_json(string):
    json_regex = r"\{(?:[^{}]|(?R))*\}"
    json_objects = re.findall(json_regex, string)
    if json_objects:
        return max(json_objects, key=len)
    return None


def get_first_number(string):
    pattern = r'\b(0|[1-9]|10)\b'
    match = re.search(pattern, string)
    if match:
        return int(match.group())
    else:
        return None


def load_yaml_file(file_path: str) -> dict:
    """Reads and returns the contents of a YAML file as dictionary"""
    return yaml.safe_load(open_file(file_path))


def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data

from pathlib import Path

def load_local_yaml_prompt(file_path):
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    json_template = load_yaml_file(str(_absolute_path))
    return json_template['chat_prompt'], json_template['system_prompt']


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
from openai import OpenAI

def llm_completion(chat_prompt="", system="", temp=0.7, max_tokens=2000, remove_nl=True, conversation=None):
    # Selecionar provider baseado em disponibilidade e prioridade
    selected_provider = None
    client = None
    model = None
    api_provider = None
    
    # Ordenar providers por prioridade
    sorted_providers = sorted(LLM_PROVIDERS.items(), key=lambda x: x[1]["priority"])
    
    for provider_name, config in sorted_providers:
        api_key = ApiKeyManager.get_api_key(config["api_key_name"])
        if api_key:
            # Configurar cliente OpenAI com as configurações do provider
            if config["base_url"]:
                client = OpenAI(
                    api_key=api_key,
                    base_url=config["base_url"]
                )
            else:
                # OpenAI usa URL padrão
                client = OpenAI(api_key=api_key)
            
            model = config["model"]
            api_provider = provider_name.capitalize()
            print(f"Using {api_provider} API with model: {model}")
            break
    
    if not client:
        available = ", ".join([f"{name.upper()}_API_KEY" for name in LLM_PROVIDERS.keys()])
        raise Exception(f"No API Key found for LLM request. Please configure one of: {available}")
    
    max_retry = 5
    retry = 0
    error = ""
    
    for i in range(max_retry):
        try:
            if conversation:
                messages = conversation
            else:
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": chat_prompt}
                ]
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temp,
                timeout=30
                )
            text = response.choices[0].message.content.strip()
            if remove_nl:
                text = re.sub('\s+', ' ', text)
            filename = '%s_llm_completion.txt' % time()
            if not os.path.exists('.logs/gpt_logs'):
                os.makedirs('.logs/gpt_logs')
            with open('.logs/gpt_logs/%s' % filename, 'w', encoding='utf-8') as outfile:
                outfile.write(f"System prompt: ===\n{system}\n===\n"+f"Chat prompt: ===\n{chat_prompt}\n===\n" + f'RESPONSE:\n====\n{text}\n===\n')
            return text
        except Exception as oops:
            retry += 1
            error_str = str(oops)
            
            # Extrair tempo de retry se for erro 429 (rate limit)
            if "429" in error_str:
                # Verificar se é limite diário (específico do Gemini)
                if "GenerateRequestsPerDayPerProjectPerModel" in error_str and api_provider == "Gemini":
                    print(f'DAILY QUOTA EXCEEDED on {api_provider}! You have reached the daily limit of 200 requests for the free tier.')
                    print('Please wait until tomorrow or upgrade your Gemini API plan.')
                    # Não adianta tentar novamente se excedeu quota diária
                    raise Exception(f"Daily quota exceeded for {api_provider}. Please wait 24 hours or upgrade your API plan.")
                
                try:
                    # Tentar extrair o tempo de retry da mensagem de erro
                    if "retryDelay" in error_str:
                        # Procurar por retryDelay no erro
                        import re as regex
                        match = regex.search(r"'retryDelay':\s*'(\d+)s'", error_str)
                        if match:
                            retry_delay = int(match.group(1))
                            print(f'Rate limit exceeded on {api_provider}. Waiting {retry_delay} seconds before retry {retry}/{max_retry}...')
                            sleep(retry_delay)
                            continue
                except:
                    pass
                
                # Se não conseguiu extrair o tempo, usar backoff exponencial
                wait_time = min(60, 2 ** retry)
                print(f'Rate limit exceeded on {api_provider}. Waiting {wait_time} seconds before retry {retry}/{max_retry}...')
                sleep(wait_time)
            else:
                # Para outros erros, imprimir mensagem correta
                print(f'Error communicating with {api_provider}:', oops)
                error = error_str
                sleep(1)
                
    raise Exception(f"Error communicating with {api_provider} LLM. Completion failed after {max_retry} retries. Last error: {error}")