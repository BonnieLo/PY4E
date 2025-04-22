# repopilot - 通用型程式碼分析 AI Agent

import os
import time
from typing import List, Dict
import google.generativeai as genai
from core.analyzer import analyze_repo

# 取得使用者的 repo 路徑
def get_target_repo_path() -> str:
    """User can input the repo path or use the default one."""
    default_path = "/Users/bonnie/Documents/program/core"
    print(f"🔍 預設分析路徑為：{default_path}")
    custom = input("請輸入新的 repo 路徑（直接 Enter 代表使用預設）: ").strip()
    repo_path = custom if custom else default_path

    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"❌ 找不到資料夾：{repo_path}")

    return repo_path

# ===== repopilot 執行流程：初版（僅處理一支範例程式碼） =====

def main():
    print("👋 歡迎使用 REPOPILOT ｡:.ﾟヽ(*´∀`)ﾉﾟ.:｡")

    # Step 0: 取得 repo 路徑
    repo_path = get_target_repo_path()
    print(f"📁 目前要分析的專案路徑為：{repo_path}")

    # Step 1: 取得 repo 中的檔案列表
    analyze_repo(repo_path, output_dir="outputs", max_files=2)
    print("✅ 分析完成！")

if __name__ == "__main__":
    main()
    
    
