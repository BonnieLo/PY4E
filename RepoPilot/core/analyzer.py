# core/analyzer.py

import os
import time
from core.prompt_utils import format_messages, generate_response

# 建立 Gemini 分析 prompt

def generate_analysis_prompt(file_path: str, code: str) -> str:
    return f"""
You are a senior Python software engineer and technical writer.
Please analyze the following Python file and generate a clear Markdown report that includes:

1. A high-level purpose of the file.
2. Summary of each function or class.
3. Whether there is any main execution flow.
4. A list of imported dependencies and why they might be used.
5. Suggestions for improvement if necessary.

File path: {file_path}

```python
{code}
```
"""

# 單一檔案分析

def analyze_file(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        prompt = generate_analysis_prompt(file_path, code)
        time.sleep(1)
        messages = [
            {"role": "system", "content": "You are a Python code analyst."},
            {"role": "user", "content": prompt}
        ]
        return generate_response(messages)

    except Exception as e:
        return f"⚠️ Error reading {file_path}: {e}"

# 專案分析 - 遞迴走訪所有 .py 檔案

def analyze_repo(repo_path: str, output_dir: str = "outputs", max_files: int = None):
    os.makedirs(output_dir, exist_ok=True)
    count = 0

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                print(f"🔍 分析中: {full_path}")

                markdown = analyze_file(full_path)
                rel_path = os.path.relpath(full_path, repo_path)
                safe_name = rel_path.replace(os.sep, "__") + ".md"

                with open(os.path.join(output_dir, safe_name), "w", encoding="utf-8") as f:
                    f.write(markdown)

                count += 1
                if max_files and count >= max_files:
                    print(f"🚧 已達分析上限 {max_files} 個檔案，提前結束。")
                    return

    print(f"✅ 分析完成，共處理 {count} 個檔案。")
