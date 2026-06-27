import ollama

def run_ollama_chat(messages, primary_model="qwen3:14b", fallback_model="qwen3:8b"):
    """
    Executes a chat session with Ollama, using a fallback model if the primary model fails.
    """
    try:
        response = ollama.chat(
            model=primary_model,
            messages=messages
        )
        return response["message"]["content"], primary_model
    except Exception as e:
        print(f"Ollama error with model {primary_model}: {e}. Retrying with fallback model {fallback_model}...")
        try:
            response = ollama.chat(
                model=fallback_model,
                messages=messages
            )
            return response["message"]["content"], fallback_model
        except Exception as fallback_err:
            print(f"Ollama fallback error with model {fallback_model}: {fallback_err}")
            raise fallback_err
