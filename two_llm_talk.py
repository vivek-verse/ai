from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

model_one = "gpt-4.1-mini"
model_two = "gpt-5-nano"

model_one_system = (
    "You are a chatbot who is very argumentative. "
    "You disagree with anything in the conversation and challenge everything in a snarky way."
)

model_two_system = (
    "You are a very polite, courteous chatbot. "
    "You try to agree with everything or find common ground. "
    "If the other person is argumentative, you try to calm them down."
)

# Conversation history for each model
model_one_messages = [
    {"role": "system", "content": model_one_system},
    {"role": "user", "content": "Hi there"}
]

model_two_messages = [
    {"role": "system", "content": model_two_system},
    {"role": "user", "content": "Hi"}
]


def call_model(model, messages):
    response = client.responses.create(
        model=model,
        input=messages
    )
    return response.output_text


# Run 5 interaction rounds
for turn in range(5):
    print(f"\n--- Turn {turn + 1} ---")

    # Model One speaks
    model_one_reply = call_model(model_one, model_one_messages)
    print("Model One:", model_one_reply)

    # Feed Model One reply to Model Two
    model_two_messages.append({"role": "user", "content": model_one_reply})

    # Model Two speaks
    model_two_reply = call_model(model_two, model_two_messages)
    print("Model Two:", model_two_reply)

    # Feed Model Two reply back to Model One
    model_one_messages.append({"role": "user", "content": model_two_reply})
