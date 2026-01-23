import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4.1-mini")

tokens = encoding.encode("Hi, my name is Vivek Yadav")

for tok in tokens:
    token_text = encoding.decode([tok])
    print(f"{tok} = {token_text}")