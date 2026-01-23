from openai import OpenAI

OLLAMA_URL = "http://localhost:11434/v1"

ollama = OpenAI(base_url=OLLAMA_URL, api_key="ollama")

response = ollama.chat.completions.create(model="phi3:latest", messages=[
    {
        "role": "user", "content": "Tell me a fun fact"
    }
])

response_text = response.choices[0].message.content

print(response_text)
