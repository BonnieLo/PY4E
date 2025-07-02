import os
import re
import shutil
import zipfile
import tempfile
import requests
import pandas as pd
from collections import defaultdict

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

    # 找到解壓縮後的資料夾
    for name in os.listdir(temp_dir):
        if os.path.isdir(os.path.join(temp_dir, name)) and name != '__MACOSX':
            extracted_path = os.path.join(temp_dir, name)
            return extracted_path, temp_dir

    raise Exception("找不到解壓縮後的資料夾")

def analyze_cpp_stl_usage(base_path):
    stl_pattern = re.compile(r"\bstd::\w+\b")
    stl_usage = defaultdict(lambda: {"count": 0, "locations": []})

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
                                if len(stl_usage[match]["locations"]) < 3:
                                    stl_usage[match]["locations"].append(f"{rel_path}:{idx}")
                except Exception as e:
                    print(f"⚠️ 無法讀取檔案 {file_path}: {e}")

    result = []
    for stl_type, data in sorted(stl_usage.items(), key=lambda x: x[1]["count"], reverse=True):
        result.append({
            "STL_Type": stl_type,
            "Count": data["count"],
            "Sample_Location_1": data["locations"][0] if len(data["locations"]) > 0 else "",
            "Sample_Location_2": data["locations"][1] if len(data["locations"]) > 1 else "",
            "Sample_Location_3": data["locations"][2] if len(data["locations"]) > 2 else ""
        })

    return pd.DataFrame(result)

# --- 主程式 ---
if __name__ == "__main__":
    print("請輸入 GitHub repo 網址（例如：https://github.com/openbmc/libpldm）：")
    repo_url = input("> ").strip()

    try:
        repo_path, temp_dir = download_and_extract_github_repo_zip(repo_url)
        print(f"✅ 成功下載並解壓縮到：{repo_path}")
        print("🔍 開始分析 C++ STL 使用情況...")

        df = analyze_cpp_stl_usage(repo_path)

        if df.empty:
            print("⚠️ 沒有找到任何 STL 使用紀錄")
        else:
            output_file = os.path.join(os.getcwd(), "stl_usage_summary.csv")
            df.to_csv(output_file, index=False)
            print(f"✅ 分析完成，結果已儲存為：{output_file}")
            print(df.head(10).to_string(index=False))

    finally:
        if 'temp_dir' in locals() and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
            print("🧹 已清除暫存資料夾")

