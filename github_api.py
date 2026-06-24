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

        repo = event["repo"]["name"]
        payload = event["payload"]

        # 直接从 payload 提取 commits
        if payload.get("commits"):
            for commit in payload["commits"]:
                commits.append({
                    "repo": repo,
                    "message": commit["message"],
                    "sha": commit["sha"],
                })
        else:
            # 如果 payload 中没有 commits，用 compare API 获取
            before = payload.get("before")
            head = payload.get("head")
            if before and head:
                compare_commits = _get_compare_commits(headers, repo, before, head)
                commits.extend(compare_commits)

    return commits


def _get_compare_commits(headers: dict, repo: str, before: str, head: str) -> list[dict]:
    """通过 compare API 获取两个 commit 之间的差异"""
    url = f"{GITHUB_API}/repos/{repo}/compare/{before}...{head}"
    response = httpx.get(url, headers=headers)

    if response.status_code != 200:
        return []

    data = response.json()
    commits = []

    for c in data.get("commits", []):
        commits.append({
            "repo": repo,
            "message": c["commit"]["message"].strip(),
            "sha": c["sha"][:7],
        })

    return commits
