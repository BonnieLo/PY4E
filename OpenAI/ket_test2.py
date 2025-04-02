import os
import google.generativeai as genai
from typing import List, Dict

# 載入 .env 中的 GOOGLE_API_KEY
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 對應的 Gemini 模型（你可以用 gemini-1.5-pro-latest 或其他支援的）
model = genai.GenerativeModel("gemini-1.5-pro-latest")


def format_messages(messages: List[Dict]) -> str:
    """把 OpenAI messages 格式轉成 Gemini 的 prompt"""
    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"(System Instruction)\n{m['content']}\n\n"
        elif m["role"] == "user":
            prompt += f"User:\n{m['content']}\n\n"
        elif m["role"] == "assistant":
            prompt += f"Assistant:\n{m['content']}\n\n"
    return prompt


def generate_response(messages: List[Dict]) -> str:
    prompt = format_messages(messages)
    response = model.generate_content(prompt) 
    return response.text

what_to_help_with = input("What do you need help with?\n")

messages = [
    {"role": "system", "content": "You are an expert software engineer that prefers functional programming."},
    {"role": "user", "content": what_to_help_with}
]

response = generate_response(messages)
print(response)