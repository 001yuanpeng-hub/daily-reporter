import os

import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API = "https://coderelay.cn/v1/messages"


def generate_report(commits: list[dict]) -> str:
    """调用 Claude API 生成日报

    Returns:
        str: Claude 生成的日报文本
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # 把 commits 列表转成文本，方便发给 Claude
    commits_text = "\n".join(
        f"- [{c['repo']}] {c['message']}" for c in commits
    )

    # 构建请求体
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": "claude-opus-4-6",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": f"请总结以下今日的代码提交：\n\n{commits_text}"
            }
        ]
    }

    # 发送 POST 请求（超时设为 60 秒）
    response = httpx.post(ANTHROPIC_API, headers=headers, json=data, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(
            f"Claude API 请求失败 (HTTP {response.status_code}): {response.text[:300]}"
        )

    result = response.json()

    # 提取 Claude 的回复
    try:
        return result["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"解析 Claude 响应失败: {e}\n原始响应: {str(result)[:300]}")
