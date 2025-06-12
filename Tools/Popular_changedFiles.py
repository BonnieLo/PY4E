import os
import requests
from datetime import datetime, timedelta, timezone
from collections import Counter

# === 設定 GitHub Token 與 Headers ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print("🔑 使用 GitHub Token:", GITHUB_TOKEN)
HEADERS_GRAPHQL = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
HEADERS_REST = {"Authorization": f"token {GITHUB_TOKEN}"}

OWNER = "openbmc"
REPO = "openbmc"
DAYS_BACK = 30
since_date = (datetime.utcnow() - timedelta(days=DAYS_BACK)).replace(tzinfo=timezone.utc)
since_iso = since_date.isoformat()

# === GraphQL 查詢：取得近期 commit SHAs ===
def build_commit_query(after_cursor=None):
    after_clause = f', after: "{after_cursor}"' if after_cursor else ""
    return f"""
    {{
      repository(owner: "{OWNER}", name: "{REPO}") {{
        defaultBranchRef {{
          target {{
            ... on Commit {{
              history(first: 100{after_clause}, since: "{since_iso}") {{
                pageInfo {{
                  hasNextPage
                  endCursor
                }}
                nodes {{
                  oid
                  committedDate
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

print("🔍 正在取得 recent commits...")
commit_shas = []
has_next_page = True
cursor = None

while has_next_page:
    query = build_commit_query(cursor)
    response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=HEADERS_GRAPHQL)
    if response.status_code != 200:
        print("❌ GraphQL 錯誤:", response.text)
        break
    data = response.json()
    try:
        history = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]
        for node in history["nodes"]:
            commit_shas.append(node["oid"])
        has_next_page = history["pageInfo"]["hasNextPage"]
        cursor = history["pageInfo"]["endCursor"]
    except Exception as e:
        print("⚠️ 資料處理錯誤:", e)
        break

print(f"✅ 取得 commit 數量：{len(commit_shas)}")

# === REST API 查每個 commit 的變動檔案 ===
print("📂 分析每個 commit 的變動路徑...")
dir_counter = Counter()

for sha in commit_shas:
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits/{sha}"
    resp = requests.get(url, headers=HEADERS_REST)
    if resp.status_code != 200:
        print(f"❌ 無法取得 commit {sha} 的資料")
        continue
    commit_data = resp.json()
    for f in commit_data.get("files", []):
        path = f.get("filename", "")
        top_dir = "/".join(path.split("/")[:2]) if "/" in path else path
        dir_counter[top_dir] += 1

# === 顯示統計結果 ===
print("\n📊 最近 30 天內改動最多的前 20 個目錄：")
for dir_path, count in dir_counter.most_common(20):
    print(f"{count:>4} 次 - {dir_path}")