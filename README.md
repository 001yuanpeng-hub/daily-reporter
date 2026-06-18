# Daily Reporter (GitHub 日报生成器)

一个基于 Python 的命令行工具（CLI），能够自动获取指定 GitHub 用户当天的 Commit 提交记录，并利用 Claude 大模型智能生成结构清晰、排版美观的技术代码日报。

---

## 🚀 功能特点

* **自动化数据采集**：直接调用 GitHub REST API，精准提取用户的仓库名、Commit 消息和提交时间。
* **AI 智能摘要**：对接 Claude API，对凌乱的 Commit 记录进行去粗取精，自动归纳今日工作亮点。
* **标准 Markdown 输出**：自动生成以日期命名的 `.md` 日报文件，方便复制和存档。

## 🛠️ 技术栈

* **语言**：Python 3.10+
* **网络请求**：HTTPX / Requests (用于调用 GitHub API)
* **大模型对接**：Anthropic Claude API
* **配置管理**：Python-dotenv (环境保护，拒绝密钥泄露)

## 📦 快速开始

### 1. 克隆与配置
首先克隆本项目到本地，并在项目根目录下创建一个 `.env` 文件，填入你的密钥：

```env
GITHUB_TOKEN=your_github_personal_access_token
ANTHROPIC_API_KEY=your_claude_api_key
