import os
import logging
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

from scrapper import fetch_website_content


# -------------------- Setup --------------------

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -------------------- AI Logic --------------------

def call_ai(model: str, messages: List[Dict[str, str]]) -> str:
    """
    Call OpenAI and return the response text.
    """
    try:
        response = client.responses.create(
            model=model,
            input=messages
        )
        return response.output_text.strip()

    except Exception as e:
        logging.exception("OpenAI call failed")
        raise RuntimeError("AI request failed") from e


def build_messages(
    system_prompt: str,
    user_prompt_prefix: str,
    website_content: str
) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": system_prompt.strip()},
        {
            "role": "user",
            "content": f"{user_prompt_prefix.strip()}\n\n{website_content}"
        }
    ]


# -------------------- Prompts --------------------

SYSTEM_PROMPT = """
You are a snarky assistant that analyzes the contents of a website and provides
a short, snarky, humorous summary.

Ignore navigation, footer, cookie notices, and boilerplate text.

Respond in markdown.
Do NOT wrap the markdown in a code block.
"""

USER_PROMPT_PREFIX = """
Here are the contents of a website.

Provide:
- A short snarky summary
- Any news or announcements (if present)
"""


# -------------------- Main --------------------

def main() -> None:
    logging.info("Starting website analysis")

    url = "https://convopipe.com"
    website_content = fetch_website_content(url)

    if not website_content.strip():
        raise ValueError("Website content is empty")

    messages = build_messages(
        system_prompt=SYSTEM_PROMPT,
        user_prompt_prefix=USER_PROMPT_PREFIX,
        website_content=website_content
    )

    model = "gpt-4.1-mini"

    summary = call_ai(model, messages)
    print("\n" + summary)


if __name__ == "__main__":
    main()
