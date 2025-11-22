import os
from groq import Groq
from dotenv import load_dotenv
from utils.json_prompts import STRICT_JSON_SYSTEM_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_agent_llm(user_prompt, temperature=0.2):
    """
    Calls Groq model with STRICT JSON system prompt.
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": STRICT_JSON_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq API Error: {str(e)}"
