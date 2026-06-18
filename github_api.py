import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件


GITHUB_API = "https://api.github.com"


def get_today_commits(username: str) -> list[dict]:
    """获取指定用户今日的所有 commits

    Returns:
        list[dict]: 每个 dict 包含 repo, message, sha 等信息
    """
    token = os.getenv("GITHUB_TOKEN")
    url = f"{GITHUB_API}/users/{username}/events"
    headers = {"Authorization": f"Bearer {token}"}

    response = httpx.get(url, headers=headers)

    if response.status_code != 200:
        print(f"GitHub API 请求失败 (HTTP {response.status_code}): {response.text[:200]}")
        return []

    events = response.json()

    if not isinstance(events, list):
        return []
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")  # 用 UTC 时间
    commits = []

    for event in events:
        # 只处理 PushEvent（推送代码的事件）
        if event["type"] != "PushEvent":
            continue

        # 检查是不是今天发生的
        created_at = event["created_at"][:10]  # 取日期部分 "2024-01-15T..." -> "2024-01-15"
        if created_at != today:
            continue

        # 提取 commits 信息（有些 PushEvent 可能没有 commits）
        repo = event["repo"]["name"]
        for commit in event["payload"].get("commits", []):
            commits.append({
                "repo": repo,
                "message": commit["message"],
                "sha": commit["sha"],
            })

    return commits
