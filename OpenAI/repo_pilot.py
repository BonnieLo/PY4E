# 通用型 Gemini 程式碼分析 Agent 框架

import os
import time
from typing import List
import google.generativeai as genai

# 初始化 Gemini API
GEMINI_MODEL = "gemini-1.5-pro-latest"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(GEMINI_MODEL)

# 產生分析用 prompt

def generate_prompt(file_path: str, code: str) -> str:
    return f"""
You are an expert Python software engineer and technical document writer.
Please analyze the following file and generate a clear documentation in markdown format including:

1. The purpose of the file.
2. A summary of each function or class.
3. If there's a main execution flow, explain how it works.
4. Identify any dependencies imported and explain how they may relate.
5. Provide suggestions for better modularity or refactoring if needed.

File Path: {file_path}

```python
{code}
```
"""

# 分析單一檔案

def analyze_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        prompt = generate_prompt(file_path, code)
        time.sleep(1)  # 避免 API rate limit
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error reading {file_path}: {e}"

# 遞迴分析整個 repo

def analyze_repo(repo_path: str, output_dir: str = "doc_output"):
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                print(f"📄 Analyzing: {full_path}")
                markdown = analyze_file(full_path)

                # 輸出對應的說明檔
                relative_path = os.path.relpath(full_path, repo_path)
                output_file = os.path.join(output_dir, relative_path.replace(os.sep, "_") + ".md")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(markdown)

# 範例執行
if __name__ == "__main__":
    target_repo = "/Users/bonnie/Documents/code/home-assistant/core"
    analyze_repo(target_repo)
    print("✅ Analysis complete!")
