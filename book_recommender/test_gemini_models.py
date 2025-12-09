# test_gemini_models.py
import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY no está definida")

genai.configure(api_key=api_key)

print("Modelos disponibles para esta API key:")
for m in genai.list_models():
    # m.name suele ser "models/xxxx"
    print("-", m.name, "=>", getattr(m, "supported_generation_methods", []))
