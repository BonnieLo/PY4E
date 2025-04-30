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
import time
from typing import List, Dict
import google.generativeai as genai
import google.api_core.exceptions

# ===== 變數定義 =====
USE_SUMMARY = True  # 是否使用摘要模式
MAX_MEMORY = 12       # 最多保留幾則 message（建議偶數，表示 3 輪互動）
chat_session = None  # 全域聊天 session

# ===== Agent 規則 =====
agent_rules = [{
    "role": "user",
    "content": """You are an AI agent that performs actions based on user input.

Available tools:
- list_files(dir: str = ".") -> List[str]: Recursively list all files (excluding hidden files and folders) under the specified directory. Defaults to the current directory.
- read_file(file_name: str) -> str: Read the content of a file.
- report(summary: str): Send a final report summary back to the user.
- terminate(message: str): End the agent loop with a message.

Mission workflow:
1. Always start by using `list_files` to list all files in the specified directory.
2. For every file listed, individually call `read_file(file_name)` to read its content.
3. Do not skip any file unless it is unreadable or irrelevant.
4. After reading all files, analyze their contents and generate a final summary.
5. Use the `report` tool to send the summary to the user.
6. After reporting, use the `terminate` tool to gracefully end the interaction.

Interaction rules:
- When the user asks about the contents of a specific directory, extract the directory name from their input and pass it as the "dir" argument to the `list_files` tool.
- Always complete the full file reading and reporting process before termination.
- If unsure at any step, prioritize completing the full reading and reporting process before deciding to terminate.

Response formatting rules:
- You must ONLY respond using a single Markdown code block containing a JSON object specifying the tool to invoke.
- The code block must use the language tag `action`.
- Do NOT explain, justify, comment, or add any extra text outside the code block.
- Do NOT wrap your response with additional explanations, confirmations, or commentary, even after completing a report or termination.
- Any non-action text will be treated as an invalid response and ignored.

Reporting formatting rules:
- When using the `report` tool, organize your findings with a clear bullet point structure:
  - List each file separately with a bullet point (`-`).
  - Start each bullet point with the filename.
  - After the filename, provide a concise description of the file’s purpose or contents.
  - Keep the report clean, readable, and avoid long paragraphs.

Example report format:

- `main.py`: The main orchestrator script for the AI agent.
- `analyzer.py`: Functions for analyzing Python files.
- `prompt_utils.py`: Handles prompt formatting and Gemini API interaction.

Correct action invocation format example:

```action
{
  "tool_name": "list_files",
  "args": {
    "dir": "OpenAI"
  }
}
""" }]


memory = []

# 載入 .env 中的 GOOGLE_API_KEY
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 對應的 Gemini 模型（你可以用 gemini-1.5-pro-latest 或其他支援的）
model = genai.GenerativeModel("gemini-1.5-pro-latest")
# This part of code is response from keyword to action not from AI.
# It works but it's not the best way to do it.

#def generate_response(prompt):
#    last_input = prompt[-1]['content']

    # 建立語意分類的關鍵字字典
#    file_query_keywords = ["what files", "list files", "檔案", "目錄", "有什麼"]
#    read_file_keywords = ["read", "open", "讀取", "打開"]

    # 統一轉小寫處理（英文）
#    lower_input = last_input.lower()

#    print(f"User Input: {last_input}")

#    if any(keyword in last_input for keyword in file_query_keywords) or any(keyword in lower_input for keyword in file_query_keywords):
#        return '''
#            ```action
#            {
#                "tool_name": "list_files",
#                "args": {}
#            }
#            ```'''
#    elif any(keyword in last_input for keyword in read_file_keywords) or any(keyword in lower_input for keyword in read_file_keywords):
#        return '''
#            ```action
#            {
#                "tool_name": "read_file",
#                "args": {"file_name": "file1.txt"}
#            }
#            ```'''
#    else:
#        return '''
#            ```action
#            {
#                "tool_name": "terminate",
#                "args": {"message": "No further action needed."}
#            }
#            ```'''

def generate_response(messages: List[Dict]) -> str:
    """使用 Gemini chat session 來取得回應"""

    global chat_session
    # 如果尚未初始化 chat session，從頭建立
    if chat_session is None:
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat_session = model.start_chat(
            history=[{"role": m["role"], "parts": [m["content"]]} for m in messages]
        )
    else:
        # 更新 history（只用最後一則 user message 發問）
        chat_session.history.extend([{"role": m["role"], "parts": [m["content"]]} for m in messages[-2:]])

    response = chat_session.send_message(messages[-1]["content"])
    return response.text.strip()

def safe_generate_response(messages):
    for attempt in range(3):
        try:
            return generate_response(messages)
        except google.api_core.exceptions.ResourceExhausted as e:
            print("⏳ Quota exceeded. Waiting 60 seconds before retry...")
            time.sleep(60)
    raise RuntimeError("❌ Failed after 3 attempts due to quota limits.")
    
def extract_markdown_block(text: str, block_type: str) -> str:
    """Extracts the content inside a markdown code block of a given type, with fallback."""
    start_marker = f"```{block_type}"
    end_marker = "```"

    start = text.find(start_marker)

    if start == -1:
        # fallback 找沒有指定 block_type 的純 code block
        start = text.find("```")
        if start == -1:
            raise ValueError(f"No code block found at all.")
        start += 3
    else:
        # 找到正確的 block_type，也要跳過 block_type 長度
        start += len(start_marker)

    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"Block not closed properly.")

    return text[start:end].strip()

def parse_action(response: str) -> Dict:
    try:
        response = extract_markdown_block(response, "action")
        response_json = json.loads(response)
        if "tool_name" in response_json and "args" in response_json:
            return response_json
        else:
            return {"tool_name": "error", "args": {"message": "You must respond with a JSON tool invocation."}}
    except Exception as e:
        print(f"⚠️ Warning: Invalid response detected: {str(e)}")
        return {"tool_name": "error", "args": {"message": "Invalid or non-action response received."}}

def list_files(dir="."):
    files = []

    if not os.path.isdir(dir):
        return [f"Error: {dir} is not a valid directory."]
    for dirpath, dirnames, filenames in os.walk(dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for f in filenames:
            if not f.startswith('.'):
                full_path = os.path.relpath(os.path.join(dirpath, f), '.')
                files.append(full_path)
    
    print(f"\n📂 [Debug] Files in '{dir}':")
    for f in files:
        print(" -", f)
    print("")
    return files

def read_file(file_name):
    try:
        if not os.path.isfile(file_name):
            return f"Error: {file_name} is not a file."
        with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: {file_name} does not exist."
    except Exception as e:
        return f"Error reading {file_name}: {str(e)}"

def terminate(message):
    print(f"Agent terminated: {message}")

def trim_memory(memory: List[Dict], max_messages: int) -> List[Dict]:
    """只保留最後 max_messages 則記憶"""
    return memory[-max_messages:]

def summarize_memory(memory: List[Dict], keep: int = MAX_MEMORY) -> List[Dict]:
    """摘要前面的記憶，保留最新 keep 則"""
    old_context = memory[:-keep]
    new_context = memory[-keep:]

    summary_prompt = [
    {"role": "user", "content": """You are a helpful summarizer. Summarize the previous agent-user interaction into a single user message for memory compression."""},
    *old_context,
    {"role": "user", "content": "Please summarize the above interaction in English."}
]

    summary_response = generate_response(summary_prompt)
    summary_message = {"role": "user", "content": f"(Summary of previous turns): {summary_response}"}
    return [summary_message] + new_context

def report(summary):
    print("\n📝 AI Agent Report")
    print("────────────────────────")
    print(summary.strip())
    print("────────────────────────\n")

# ===== 執行流程：初版（僅處理一支範例程式碼） =====
def agent_loop():
    global memory

    while True:
        # Step 0: 控制 memory 長度
        if USE_SUMMARY and len(memory) > MAX_MEMORY:
            memory = summarize_memory(memory, keep=MAX_MEMORY)
        else:
            memory = trim_memory(memory, max_messages=MAX_MEMORY)

        # Step 1: 構建 Prompt
        prompt = agent_rules + memory

        # Step 2: 生成回應
        response = safe_generate_response(prompt)
        print("AI Response:", response)

        # Step 3: 解析回應
        action = parse_action(response)

        # Step 4: 執行工具
        if action["tool_name"] == "list_files":
            dir_to_scan = action["args"].get("dir", ".")
            result = {"result": list_files(dir_to_scan)}
        elif action["tool_name"] == "read_file":
            result = {"result": read_file(action["args"]["file_name"])}
        elif action["tool_name"] == "error":
            result = {"error": action["args"]["message"]}
        elif action["tool_name"] == "terminate":
            print(f"\n🎯 Agent Termination Message: {action['args']['message']}")
            print("✅ Termination detected. Ending agent loop cleanly.")
            break  # 強制結束，不再處理後面任何 LLM output
        elif action["tool_name"] == "report":
            summary = action["args"].get("summary", "")
            report(summary)
            result = {"result": f"Report sent: {summary}"}
        else:
            result = {"error": "Unknown action: " + action["tool_name"]}

        # Step 5: 更新記憶
        # The assistant role captures the structured response generated by the LLM.
        # The user role captures the feedback in the form of the action result, 
        # ensuring that the LLM has a clear understanding of what happened after 
        # the action was performed. The results of actions are always communicated 
        # back to the LLM with the “user” role.
       # 僅當回應是合法的 ```action``` 格式時，才記錄進 memory
        if response.strip().startswith("```action"):
            memory.append({"role": "assistant", "content": response})
            memory.append({"role": "user", "content": str(result)})
        else:
            print("⚠️ 回應不是合法 action 格式，未加入記憶。")

if __name__ == "__main__":
    print("👋 歡迎使用 Ask the file:.ﾟヽ(*´∀`)ﾉﾟ.:｡")

    user_input = input("Ask something about the files: ").strip()

    if user_input:
        memory.append({"role": "user", "content": user_input})
        agent_loop()
    else:
        print("❗請輸入一些內容來啟動對話。")
    
    
