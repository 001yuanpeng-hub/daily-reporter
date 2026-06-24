import os

import httpx
from dotenv import load_dotenv

load_dotenv()

# API 配置
MIMO_API = "https://api.xiaomimimo.com/anthropic/v1/messages"
CLAUDE_API = "https://coderelay.cn/v1/messages"


def generate_report(commits: list[dict], provider: str = "mimo") -> str:
    """调用 AI API 生成日报

    Args:
        commits: 提交记录列表
        provider: API 提供商，可选 "mimo" 或 "claude"

    Returns:
        str: AI 生成的日报文本
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # 把 commits 列表转成文本，方便发给 AI
    commits_text = "\n".join(
        f"- [{c['repo']}] {c['message']}" for c in commits
    )

    # 根据 provider 选择 API 地址和模型
    if provider == "mimo":
        api_url = MIMO_API
        model = "mimo-v2.5-pro"
    else:
        api_url = CLAUDE_API
        model = "claude-opus-4-6"

    # 构建请求体
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": model,
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": f"""请根据以下 GitHub 提交记录，生成一份简洁的中文代码日报。

要求：
1. 开头用一句话概括今日工作重点
2. 按仓库分组，每个仓库列出提交的改动要点
3. 用简洁的技术语言，不要啰嗦
4. 不要提问，不要说"需要我协助"之类的话
5. 使用 Markdown 格式

今日提交记录：
{commits_text}"""
            }
        ]
    }

    # 发送 POST 请求（超时设为 60 秒）
    response = httpx.post(api_url, headers=headers, json=data, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(
            f"API 请求失败 (HTTP {response.status_code}): {response.text[:300]}"
        )

    result = response.json()

    # 提取 AI 的回复
    try:
        return result["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"解析响应失败: {e}\n原始响应: {str(result)[:300]}")
