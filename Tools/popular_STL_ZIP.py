# -*- coding: utf-8 -*-

import os
import re
import shutil
import zipfile
import tempfile
import requests
import pandas as pd
from collections import defaultdict
import google.generativeai as genai
import time

# 你想要分析的 Repo 清單
openbmc_repos = [
    "https://github.com/openbmc/openbmc",
    "https://github.com/openbmc/bmcweb",
    "https://github.com/openbmc/entity-manager",
    "https://github.com/openbmc/dbus-sensors",
    "https://github.com/openbmc/libpldm",
    "https://github.com/openbmc/pldm",
    "https://github.com/openbmc/phosphor-host-ipmid",
    "https://github.com/openbmc/phosphor-logging",
    "https://github.com/openbmc/phosphor-dbus-interfaces",
    "https://github.com/openbmc/sdbusplus",
    "https://github.com/openbmc/phosphor-power",
    "https://github.com/openbmc/phosphor-state-manager"
]

# 下載並解壓縮 GitHub Repo
def download_and_extract_github_repo_zip(repo_url):
    if not repo_url.endswith('/'):
        repo_url += '/'
    zip_url = repo_url + 'archive/refs/heads/master.zip'
    response = requests.get(zip_url)
    if response.status_code != 200:
        raise Exception(f"下載失敗：{zip_url}")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'repo.zip')
    with open(zip_path, 'wb') as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    for name in os.listdir(temp_dir):
        if os.path.isdir(os.path.join(temp_dir, name)) and name != '__MACOSX':
            extracted_path = os.path.join(temp_dir, name)
            return extracted_path, temp_dir

    raise Exception("找不到解壓縮後的資料夾")

# 分析 C++ STL 使用狀況
def analyze_cpp_stl_usage(base_path, repo_name, stl_usage):
    stl_pattern = re.compile(r"\bstd::\w+\b")

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith((".cpp", ".hpp", ".h", ".cc", ".cxx")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for idx, line in enumerate(f, 1):
                            matches = stl_pattern.findall(line)
                            for match in matches:
                                rel_path = os.path.relpath(file_path, base_path)
                                stl_usage[match]["count"] += 1
                                stl_usage[match]["locations"].append(f"{repo_name}/{rel_path}:{idx}")
                except Exception as e:
                    print(f"無法讀取檔案 {file_path}: {e}")

# Gemini 查詢函式（使用 gemini-1.5-flash-latest）
GEMINI_MODEL = "models/gemini-1.5-flash-latest"
model = genai.GenerativeModel(GEMINI_MODEL)

def call_gemini(prompt: str, retries: int = 3, delay: int = 30) -> str:
    for attempt in range(1, retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"第 {attempt} 次：API 限制，等待 {delay} 秒後重試...")
                time.sleep(delay)
            else:
                raise RuntimeError(f"Gemini 呼叫失敗: {str(e)}")
    raise RuntimeError("多次重試仍無法取得 Gemini 回應")

# 建立 Gemini 的 Prompt
def make_prompt(stl_name, sample_files):
    prompt = f"""
I am learning C++ STL from a real-world project (OpenBMC).

Please explain the use and best practices of `{stl_name}`, based on real firmware development.

Then, consider that in OpenBMC project, `{stl_name}` appears in the following files:
{sample_files}

Please tell me:
1. Why this STL might be used in those firmware files
2. What are some common mistakes or risks in using this STL
3. Any OpenBMC-specific pattern worth noticing

Format your reply in Markdown for easy copying.
"""
    return prompt.strip()

# 主程式執行流程
if __name__ == "__main__":
    all_stl_usage = defaultdict(lambda: {"count": 0, "locations": []})

    for repo_url in openbmc_repos:
        print(f"\n分析中 repo: {repo_url}")
        try:
            repo_path, temp_dir = download_and_extract_github_repo_zip(repo_url)
            repo_name = repo_url.rstrip('/').split('/')[-1]
            print(f"解壓成功：{repo_name}")
            analyze_cpp_stl_usage(repo_path, repo_name, all_stl_usage)
        except Exception as e:
            print(f"分析失敗：{e}")
        finally:
            if 'temp_dir' in locals() and os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
                print("已清除暫存資料夾")

    # 匯出 STL 統計結果
    result = []
    for stl_type, data in sorted(all_stl_usage.items(), key=lambda x: x[1]["count"], reverse=True):
        result.append({
            "STL_Type": stl_type,
            "Count": data["count"],
            "SampleFiles": ", ".join(data["locations"][:3])
        })

    df = pd.DataFrame(result)
    df.to_csv("all_repo_stl_usage_summary.csv", index=False)
    print("\n統計完成，儲存為 all_repo_stl_usage_summary.csv")
    print(df.head(10).to_string(index=False))

    # Gemini API 金鑰設定
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    print("Gemini API Key 已載入")

    # 建立輸出資料夾
    output_dir = "stl_notes"
    os.makedirs(output_dir, exist_ok=True)

    for index, row in df.iterrows():
        stl = row["STL_Type"]
        sample_files = row["SampleFiles"]
        prompt = make_prompt(stl, sample_files)
        print(f"\n分析：{stl}")
        try:
            response = call_gemini(prompt)
            with open(f"{output_dir}/{stl}.md", "w") as f:
                f.write(response)
            print(f"{stl} 分析完成，已儲存。")
        except Exception as e:
            print(f"{stl} 產生失敗：{e}")