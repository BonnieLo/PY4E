import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

# === 1. 讀取 GitHub Token ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print("🔑 使用 GitHub Token:", GITHUB_TOKEN)
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# === 2. 設定 repo 清單與參數 ===
OWNER = "openbmc"
API_URL_GRAPHQL = "https://api.github.com/graphql"
API_URL_REST = "https://api.github.com"
REPOS = [
    "openbmc", "docs", "phosphor-dbus-interfaces", "entity-manager", "phosphor-inventory-manager",
    "phosphor-logging", "phosphor-host-ipmid", "phosphor-ipmi-flash", "phosphor-networkd",
    "phosphor-settingsd", "phosphor-fan-presence", "phosphor-state-manager", "phosphor-power",
    "phosphor-bmc-code-mgmt", "phosphor-objmgr", "obmc-console", "bmcweb", "webui-vue",
    "pldm", "libpldm", "telemetry", "service-config-manager", "bios-settings-mgr",
    "openbmc-test-automation", "openbmc-tools", "openpower-host-ipmi-oem",
    "meta-phosphor", "meta-aspeed", "meta-nuvoton"
]

DAYS_BACK = 60
since_date = (datetime.utcnow() - timedelta(days=DAYS_BACK)).replace(tzinfo=timezone.utc)

# === 3. 建立 GraphQL 查詢函式（拉 PR 資訊）===
def build_pr_query(repo):
    return f"""
    {{
      repository(owner: "{OWNER}", name: "{repo}") {{
        pullRequests(last: 100, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            number
            title
            state
            createdAt
            mergedAt
            author {{
              login
            }}
            reviews(first: 20) {{
              nodes {{
                author {{
                  login
                }}
                state
                submittedAt
              }}
            }}
          }}
        }}
      }}
    }}
    """

# === 4. 統計 PR & Commit 數量 ===
results = []
'''for repo in REPOS:
    # Step 1: 查 PR
    pr_query = build_pr_query(repo)
    pr_response = requests.post(API_URL_GRAPHQL, json={"query": pr_query}, headers=HEADERS)
    pr_count = 0
    reviewers = set()
    if pr_response.status_code == 200:
        pr_data = pr_response.json().get("data", {}).get("repository")
        if pr_data and pr_data.get("pullRequests"):
            for pr in pr_data["pullRequests"]["nodes"]:
                created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
                if created_at > since_date:
                    pr_count += 1
                    reviewers.update(
                        r["author"]["login"] for r in pr["reviews"]["nodes"] if r["author"]
                    )
    else:
        print(f"⚠️ 無法取得 PR 資料：{repo}")'''

    # Step 2: 查 Commit 數
    commit_count = 0
    commits_url = f"{API_URL_REST}/repos/{OWNER}/{repo}/commits"
    params = {"since": since_date.isoformat()}
    commit_response = requests.get(commits_url, headers=HEADERS, params=params)
    if commit_response.status_code == 200:
        commit_count = len(commit_response.json())
    else:
        print(f"⚠️ 無法取得 Commit 資料：{repo}")

    results.append({
        "Repo": repo,
        "Recent PRs": pr_count,
        "Unique Reviewers": len(reviewers),
        "Recent Commits": commit_count
    })

# === 5. 顯示綜合統計表 ===
df = pd.DataFrame(results).sort_values(by="Recent Commits", ascending=False)
print("\n📊 OpenBMC Repo 活躍度分析（依 Commit 數排序）")
print(df.to_markdown(index=False))