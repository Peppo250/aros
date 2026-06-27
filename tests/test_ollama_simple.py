import ollama
import sys

# Reconfigure stdout to use UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("Testing Ollama with qwen3:8b...")
try:
    resp = ollama.chat(model="qwen3:8b", messages=[{"role": "user", "content": "hello"}])
    print("qwen3:8b response:", resp["message"]["content"])
except Exception as e:
    print("qwen3:8b failed:", e)

print("\nTesting Ollama with qwen3:14b...")
try:
    resp = ollama.chat(model="qwen3:14b", messages=[{"role": "user", "content": "hello"}])
    print("qwen3:14b response:", resp["message"]["content"])
except Exception as e:
    print("qwen3:14b failed:", e)
