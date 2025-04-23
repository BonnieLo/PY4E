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
    
def extract_markdown_block(text: str, block_type: str) -> str:
    """Extracts the content inside a markdown code block of a given type."""
    start_marker = f"```{block_type}"
    end_marker = "```"

    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"No block of type {block_type} found.")

    start += len(start_marker)
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"Block not closed properly.")

    return text[start:end].strip()

def parse_action(response: str) -> Dict:
    """Parse the LLM response into a structured action dictionary."""
    try:
        response = extract_markdown_block(response, "action")
        response_json = json.loads(response)
        if "tool_name" in response_json and "args" in response_json:
            return response_json
        else:
            return {"tool_name": "error", "args": {"message": "You must respond with a JSON tool invocation."}}
    except json.JSONDecodeError:
        return {"tool_name": "error", "args": {"message": "Invalid JSON response. You must respond with a JSON tool invocation."}}
    except ValueError as e:
        return {"tool_name": "error", "args": {"message": str(e)}}

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

    while True:
        # Step 1: 構建 Prompt
        prompt = agent_rules + memory

        # Step 3: 生成回應
        response = generate_response(prompt)
        print("AI Response:", response)

        # Step 4: 解析回應
        action = parse_action(response)

        if action["tool_name"] == "list_files":
            result = {"result": list_files()}
        elif action["tool_name"] == "read_file":
            result = {"result": read_file(action["args"]["file_name"])}
        elif action["tool_name"] == "error":
            result = {"error": action["args"]["message"]}
        elif action["tool_name"] == "terminate":
            print(action["args"]["message"])
            break
        else:
            result = {"error": "Unknown action: " + action["tool_name"]}

        # Step 5: 更新記憶
        # The assistant role captures the structured response generated by the LLM.
        # The user role captures the feedback in the form of the action result, 
        # ensuring that the LLM has a clear understanding of what happened after 
        # the action was performed. The results of actions are always communicated 
        # back to the LLM with the “user” role.

        memory.append({"role": "assistant", "content": response})
        memory.append({"role": "user", "content": str(result)})

if __name__ == "__main__":
    # Step 1: 取得使用者輸入
    print("👋 歡迎使用 Ask the file:.ﾟヽ(*´∀`)ﾉﾟ.:｡")
    user_input = input("Ask something about the files: ")
    # AI負責決策（What to do），程式負責執行（How to do），Result 是執行後的回饋。
    memory.append({"role": "user", "content": user_input})
    agent_loop()
    
    
