from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import os

api_key = os.environ.get("GEMINI_API_KEY", "")
print(f"Key preview: {api_key[:5]}...")
genai.configure(api_key=api_key)

try:
    print("Available models:")
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error fetching models: {e}")
