import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

from github_api import get_today_commits
from claude_api import generate_report


def main():
    load_dotenv()

    # 检查必需的凭据
    if not os.getenv("GITHUB_TOKEN"):
        print("错误: 请在 .env 文件中设置 GITHUB_TOKEN")
        sys.exit(1)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("错误: 请在 .env 文件中设置 ANTHROPIC_API_KEY")
        sys.exit(1)

    # 解析参数
    username = None
    provider = "mimo"  # 默认使用 mimo

    for arg in sys.argv[1:]:
        if arg in ("--mimo", "--claude"):
            provider = arg[2:]  
        elif not arg.startswith("--"):
            username = arg

    if not username:
        print("用法: python main.py <github_username> [--mimo|--claude]")
        print("  --mimo   使用 Mimo API (默认)")
        print("  --claude 使用 Claude API")
        sys.exit(1)

    try:
        # 获取今日 commits
        print(f"正在获取 {username} 今日的 commits...")
        commits = get_today_commits(username)
    except Exception as e:
        print(f"获取 commits 失败: {e}")
        sys.exit(1)

    if not commits:
        print("今日没有 commits 记录")
        return

    print(f"获取到 {len(commits)} 条 commits, 正在调用 {provider.upper()} 生成日报...")

    try:
        report = generate_report(commits, provider=provider)
    except Exception as e:
        print(f"生成日报失败: {e}")
        sys.exit(1)

    # 保存到 .md 文件（用 UTC 时间）
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{today}-daily-report.md"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {today} 代码日报\n\n")
            f.write(report)
    except OSError as e:
        print(f"保存文件失败: {e}")
        sys.exit(1)

    print(f"\n日报已保存到 {filename}")


if __name__ == "__main__":
    main()
