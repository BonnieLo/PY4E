# core/prompt_utils.py

import os
import time
from typing import List, Dict
import google.generativeai as genai

# 初始化 Gemini 模型
GEMINI_MODEL = "gemini-1.5-pro-latest"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(GEMINI_MODEL)

# 將 messages 轉換為 Gemini 可理解的 prompt 格式
def format_messages(messages: List[Dict]) -> str:
    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"(System Instruction)\n{m['content']}\n\n"
        elif m["role"] == "user":
            prompt += f"User:\n{m['content']}\n\n"
        elif m["role"] == "assistant":
            prompt += f"Assistant:\n{m['content']}\n\n"
    return prompt

# 生成 Gemini 回應
def generate_response(messages: List[Dict]) -> str:
    prompt = format_messages(messages)
    for attempt in range(3):  # The max number of retries is 3
        try:
            time.sleep(1)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                print("⚠️ API 配額限制，等待 60 秒後重試...")
                time.sleep(60)
            else:
                raise e
    raise RuntimeError("❌ 多次重試仍無法取得 Gemini 回應")
