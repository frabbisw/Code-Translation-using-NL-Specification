import os
import time
import openai
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

load_dotenv()

def approx_tokens(messages, encoding_model="gpt-4o-mini"):
    # Best-effort estimate; provider tokenization may differ.
    try:
        enc = tiktoken.encoding_for_model(encoding_model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")

    total = 0
    for m in messages:
        c = m.get("content", "")
        if isinstance(c, str):
            total += len(enc.encode(c))
    return total

def send_message_to_openai(message_log, model):
    client = OpenAI()  # needs OPENAI_API_KEY in env

    # Pick a conservative cap if you don't know the model's true context.
    # Better: just set a fixed max_tokens like 1024 or 2048.
    max_tokens = 2048

    last_err = None
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=message_log,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content

        except openai.BadRequestError as e:
            # Includes invalid params, wrong model id, context length exceeded, etc.
            return f"# BadRequestError: {e}"

        except openai.RateLimitError as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
            continue

        except (openai.APIConnectionError, openai.APIError) as e:
            last_err = e
            time.sleep(0.8 * (attempt + 1))
            continue

    return f"# Failed after retries. Last error: {last_err}"

def send_message_to_deepseek(message_log):
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY is missing.")

    # Use the correct DeepSeek model id for your account (often deepseek-chat / deepseek-coder)
    model = "deepseek-coder"

    max_tokens = 2048

    last_err = None
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=message_log,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content

        except openai.BadRequestError as e:
            return f"# BadRequestError: {e}"

        except openai.RateLimitError as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
            continue

        except (openai.APIConnectionError, openai.APIError) as e:
            last_err = e
            time.sleep(0.8 * (attempt + 1))
            continue

    return f"# Failed after retries. Last error: {last_err}"
