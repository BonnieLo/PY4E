import requests
import json
import time

# 設定基本參數
PROJECT = "openbmc/pldm"
LIMIT = 100
OUTPUT_FILE = "pldm_gerrit_comments.json"

# Gerrit API URL
BASE_URL = "https://gerrit.openbmc.org"
CHANGES_API = f"{BASE_URL}/changes/?q=project:{PROJECT}&n={LIMIT}"

# Helper function to clean XSSI prefix
def clean_response_text(text):
    return text.lstrip(")]}'\n")

# 擷取留言內容
def fetch_comments_for_change(change_id):
    try:
        url = f"{BASE_URL}/changes/{change_id}/comments"
        response = requests.get(url)
        if response.status_code == 200:
            cleaned = clean_response_text(response.text)
            return json.loads(cleaned)
        else:
            print(f"❌ 無法取得留言：{change_id}, Status: {response.status_code}")
            return {}
    except Exception as e:
        print(f"⚠️ 錯誤：{e}")
        return {}

# 擷取變更清單
def fetch_changes():
    print("📥 擷取變更清單中...")
    response = requests.get(CHANGES_API)
    if response.status_code == 200:
        changes = json.loads(clean_response_text(response.text))
        print(f"✅ 成功取得 {len(changes)} 筆變更")
        return changes
    else:
        print("❌ 取得變更失敗")
        return []

# 主程式
if __name__ == "__main__":
    all_data = []
    changes = fetch_changes()
    for idx, change in enumerate(changes):
        print(f"\n🔍 處理第 {idx+1} 筆：{change['subject']}")
        comments = fetch_comments_for_change(change['id'])
        all_data.append({
            "change_id": change['id'],
            "change_number": change['_number'],
            "subject": change['subject'],
            "owner": change['owner'].get('email', 'unknown'),
            "comments": comments
        })
        time.sleep(1)  # 避免過快連線造成封鎖

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"\n📦 留言資料已儲存至 {OUTPUT_FILE}")
