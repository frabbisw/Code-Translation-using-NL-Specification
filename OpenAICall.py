import openai
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

def send_message_to_openai(message_log):
    load_dotenv()
    "Use OpenAI's ChatCompletion API to get the chatbot's response"
    encoding = tiktoken.encoding_for_model("gpt-4")
    num_tokens = len(encoding.encode(message_log[1]["content"]))

    response = "exceptional case"
    is_success = False
    max_attempts = 5
    client = OpenAI()
    while max_attempts > 0:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # The name of the OpenAI chatbot model to use
                # The conversation history up to this point, as a list of dictionaries
                messages=message_log,
                # The maximum number of tokens (words or subwords) in the generated response
                max_tokens=max(1, 8000-num_tokens),
                # The "creativity" of the generated response (higher temperature = more creative)
                temperature=0.7,
            )
            is_success = True
            break
        except openai.error.InvalidRequestError as e:
            return "# Token size exceeded."
        except:
            max_attempts -= 1
            continue

    if not is_success:
        return response

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content