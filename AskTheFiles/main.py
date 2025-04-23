'''
    askthefile - 通用型程式碼分析 AI Agent
    This agent will be able to list files in a directory, 
    read their content, and answer questions about them. 
    We’ll break down the agent loop—how it receives input, 
    decides on actions, executes them, and updates its memory
    —step by step.
'''

import os
import json
from typing import List, Dict
import google.generativeai as genai

# ===== 變數定義 =====
agent_rules = [{
    "role": "system",
    "content": """
    You are an AI agent that can perform tasks by using available tools.

    Available tools:
    - list_files() -> List[str]: List all files in the current directory.
    - read_file(file_name: str) -> str: Read the content of a file.
    - terminate(message: str): End the agent loop and print a summary to the user.

    If a user asks about files, list them before reading.

    Every response MUST have an action.
    Respond in this format:

    ```action
    {
        "tool_name": "insert tool_name",
        "args": {...}
    }
    """
    }]
memory = []

# 載入 .env 中的 GOOGLE_API_KEY
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 對應的 Gemini 模型（你可以用 gemini-1.5-pro-latest 或其他支援的）
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Functions
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

def generate_response(prompt):
    last_input = prompt[-1]['content']

    # 建立語意分類的關鍵字字典
    file_query_keywords = ["what files", "list files", "檔案", "目錄", "有什麼"]
    read_file_keywords = ["read", "open", "讀取", "打開"]

    # 統一轉小寫處理（英文）
    lower_input = last_input.lower()

    print(f"User Input: {last_input}")

    if any(keyword in last_input for keyword in file_query_keywords) or any(keyword in lower_input for keyword in file_query_keywords):
        return '''
            ```action
            {
                "tool_name": "list_files",
                "args": {}
            }
            ```'''
    elif any(keyword in last_input for keyword in read_file_keywords) or any(keyword in lower_input for keyword in read_file_keywords):
        return '''
            ```action
            {
                "tool_name": "read_file",
                "args": {"file_name": "file1.txt"}
            }
            ```'''
    else:
        return '''
            ```action
            {
                "tool_name": "terminate",
                "args": {"message": "No further action needed."}
            }
            ```'''
def parse_response(response):
    if '```action' not in response:
        print("⚠️ Error: Response does not contain expected action block.")
        print(f"Response was: {response}")
        return None, None
    try:
        action_block = response.split('```action')[1].strip().strip('`')
        action_json = json.loads(action_block)
        return action_json['tool_name'], action_json.get('args', {})
    except Exception as e:
        print(f"⚠️ Error parsing response: {e}")
        print(f"Response content: {response}")
        return None, None

def list_files():
    return os.listdir('.')

def read_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: {file_name} does not exist."

def terminate(message):
    print(f"Agent terminated: {message}")

# ===== 執行流程：初版（僅處理一支範例程式碼） =====

def agent_loop():
    MAX_ITERATIONS = 3
    iteration = 0

    while iteration < MAX_ITERATIONS:
        iteration += 1

        # Step 1: 構建 Prompt
        prompt = agent_rules + memory

        # Step 3: 生成回應
        response = generate_response(prompt)
        print("AI Response:", response)

        # Step 4: 解析回應
        tool_name, args = parse_response(response)
        if tool_name == "list_files":
            result = list_files()
            print(f"📂 Files: {result}")
        elif tool_name == "read_file":
            result = read_file(args.get('file_name', ''))
            print(f"📖 File Content: {result}")
        elif tool_name == "terminate":
            terminate(args.get('message', 'Task completed.'))
            break
        else:
            print("⚠️ Unknown action.")
            break
        # Step 5: 更新記憶
        memory.append({"role": "assistant", "content": response})
        memory.append({"role": "user", "content": str(result)})

if __name__ == "__main__":
    # Step 1: 取得使用者輸入
    print("👋 歡迎使用 Ask the file:.ﾟヽ(*´∀`)ﾉﾟ.:｡")
    user_input = input("Ask something about the files: ")
    memory.append({"role": "user", "content": user_input})

    agent_loop()
    
    
