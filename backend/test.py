import ollama

response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": "What is Edge AI?"
        }
    ]
)

print(response["message"]["content"])