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
memory = [] # 全域記憶（包含 agent 規則）

# ===== Agent 規則 =====
from rules import agent_rules

# 工具 schema 模擬表
tool_schemas = {
    "list_files": {
        "description": "Recursively list all files under a directory.",
        "parameters": {
            "dir": {"type": "string", "required": False, "default": "."}
        }
    },
    "read_file": {
        "description": "Read the content of a file.",
        "parameters": {
            "file_name": {"type": "string", "required": True}
        }
    },
    "report": {
        "description": "Report a summary back to the user.",
        "parameters": {
            "summary": {"type": "string", "required": True}
        }
    },
    "terminate": {
        "description": "End the conversation.",
        "parameters": {
            "message": {"type": "string", "required": True}
        }
    }
}

# ===== 初始化 =====
# 載入 .env 中的 GOOGLE_API_KEY
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 對應的 Gemini 模型（你可以用 gemini-1.5-pro-latest 或其他支援的）
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# ===== 工具函數 =====
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
    
def validate_args(tool_name: str, args: dict) -> (bool, str):
    if tool_name not in tool_schemas:
        return False, f"Unknown tool: {tool_name}"

    schema = tool_schemas[tool_name]["parameters"]

    # 檢查必要參數是否都有提供
    for param, spec in schema.items():
        if spec.get("required", False) and param not in args:
            return False, f"Missing required argument: '{param}' for tool '{tool_name}'"

        # 檢查參數類型是否正確（若有提供）
        if param in args:
            expected_type = spec["type"]
            actual_value = args[param]
            if expected_type == "string" and not isinstance(actual_value, str):
                return False, f"Argument '{param}' must be a string"
            # 你也可以延伸支援 int, bool, list, dict 等類型

    return True, "OK"

def list_files(dir="."):
    files = []

    if not os.path.isdir(dir):
        return f"Error: {dir} is not a valid directory."
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

# ===== 工具函數對應 =====
# 將工具函數對應到 agent 的 action
tool_functions = {
    "list_files": list_files,
    "read_file": read_file,
    "report": lambda summary: print(f"..."),
    "terminate": lambda message: print(f"...")
}

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

        # Step 4: 驗證參數 → 執行工具
        tool_name = action["tool_name"]
        tool_args = action.get("args", {})

        # 驗證參數是否正確
        is_valid, validation_msg = validate_args(tool_name, tool_args)

        if not is_valid:
            result = {"error": validation_msg}
        elif tool_name == "list_files":
            dir_to_scan = tool_args.get("dir", ".")
            result = {"result": list_files(dir_to_scan)}
        elif tool_name == "read_file":
            result = {"result": read_file(tool_args["file_name"])}
        elif tool_name == "terminate":
            print(f"\n🎯 Agent Termination Message: {tool_args['message']}")
            print("✅ Termination detected. Ending agent loop cleanly.")
            break
        elif tool_name == "report":
            summary = tool_args.get("summary", "")
            report(summary)
            result = {"result": f"Report sent: {summary}"}
        else:
            result = {"error": f"Unknown action: {tool_name}"}  

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
    
    
