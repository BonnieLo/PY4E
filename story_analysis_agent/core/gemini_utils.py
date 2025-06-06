import os
import time
from typing import List, Dict
import google.generativeai as genai
import re


# 環境變數中獲取 API 金鑰
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 初始化 Gemini 模型
#GEMINI_MODEL = "gemini-1.5-pro-latest"
GEMINI_MODEL = "models/gemini-1.5-flash-latest"
model = genai.GenerativeModel(GEMINI_MODEL)

# -------------------------------
# ✳️ 簡易版：單句 prompt 呼叫
# -------------------------------
def call_gemini(prompt: str, retries: int = 3, delay: int = 30) -> str:
    """
    呼叫 Gemini 模型，若遇錯誤自動重試。
    適合小量多次測試時使用，避免配額暫時失效時馬上中止。
    """
    for attempt in range(1, retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"⚠️ 第 {attempt} 次：API 配額限制，等待 {delay} 秒後重試...")
                time.sleep(delay)
            else:
                raise RuntimeError(f"Gemini 呼叫失敗: {str(e)}")
    
    raise RuntimeError("❌ 多次重試仍無法取得 Gemini 回應")


# -------------------------------
# 🧠 結構化對話版本：支援多輪訊息格式（user / system / assistant）
# -------------------------------

def format_messages(messages: List[Dict]) -> str:
    """
    將訊息陣列轉為 Gemini 可理解的 prompt 格式。
    支援 role: system / user / assistant。
    """
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
    """
    將多輪對話訊息送入 Gemini 模型，支援 429 重試機制。
    回傳文字型回應。
    """
    prompt = format_messages(messages)
    for attempt in range(3):  # 最多重試 3 次
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

def clean_json_string(s: str) -> str:
    """
    清除 Gemini 回傳中以 ```json 包起來的 markdown 格式，回傳純 JSON 字串。
    """
    return re.sub(r"^```json\s*|\s*```$", "", s.strip(), flags=re.DOTALL)