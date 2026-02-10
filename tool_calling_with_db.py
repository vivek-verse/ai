from openai import OpenAI
from dotenv import load_dotenv
import json
import sqlite3
import gradio as gr
load_dotenv()

DB = "prices.db"

with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS prices (city TEXT PRIMARY KEY, price REAL)')
    conn.commit()

openai = OpenAI()

MODEL = "gpt-4.1-mini"

system_message = """
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
"""

# ticket_prices = {
#     "london": 799,
#     "paris": 899,
#     "tokyo": 1400,
#     "berlin": 499
# }

# def set_ticket_price(city, price):
#     with sqlite3.connect(DB) as conn:
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO prices (city, price) VALUES (?, ?) ON CONFLICT(city) DO UPDATE SET price = ?', (city.lower(), price, price))
#         conn.commit()

# for city, price in ticket_prices.items():
#     set_ticket_price(city, price)

def get_ticket_price(city):
    print(f"Tool called for city {city}")
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT price FROM prices WHERE city = ?', (city.lower(),))
        result = cursor.fetchone()
        return f"Ticket price to {city} is ${result[0]}" if result else "No price data available for this city"

price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to"
            }
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": price_function}]

def handle_tool_calls(message):
    responses = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            price_details = get_ticket_price(city)
            responses.append({
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            })

    return responses  # This returns a list

# In the chat function, change this:
def chat(message, history):
    history = [{
        "role": h["role"],
        "content": h["content"]
    } for h in history]

    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(tool_responses)  # Changed from append to extend
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    
    return response.choices[0].message.content

gr.ChatInterface(fn=chat).launch()