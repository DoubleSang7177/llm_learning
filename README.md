# 📦 LLM 学习与实战项目说明

## 📌 项目简介

本项目用于学习和实践大模型（LLM）、Web3 以及自动化交易相关技术，包含课程学习代码与 AI 辅助开发代码。

---

## 📁 项目结构说明

### 🎓 黑马程序员课程代码（基础学习）

以下文件以 `01`、`02`、`03...` 开头，来源于黑马程序员大模型课程：

* `01-Test-APIKEY.py`
  👉 测试 API Key 是否可用

* `02-OpenAI库的基础使用.py`
  👉 OpenAI / 兼容接口的基础调用方法

* `03-OpenAI库的流式输出.py`
  👉 流式输出（stream）实现

---

### 🤖 AI 辅助开发代码（进阶实践）

以下代码为基于 AI（如 GPT / DeepSeek）辅助开发：

* `GPT-Agent.py`
  👉 Agent 模型尝试（自动执行逻辑）

* `GPT-main.py`
  👉 主入口程序（核心调用逻辑）

* `GPT-WebSocket.py`
  👉 WebSocket 实时通信版本

* `GPT-WebSocketPro.py`
  👉 WebSocket 高级优化版本

---

### ⚙️ 配置文件

* `.env`
  👉 存放 API Key / 私钥等敏感信息（⚠️ 不要上传到 Git）

* `.gitignore`
  👉 忽略敏感文件和环境

* `rules.json`
  👉 自定义规则 / 策略配置

---

### 🧪 测试文件

* `test.py`
  👉 临时代码测试

---

## 🚀 技术栈

* Python 3.x
* OpenAI / DeepSeek API
* WebSocket
* Web3（区块链交互）

---

## ⚠️ 注意事项

* `.env` 文件包含敏感信息，请勿泄露
* 建议使用虚拟环境 `.venv`
* API Key 建议定期更换

---

## 🎯 后续方向

* 构建自动交易 Agent
* 接入行情数据（币安 / OKX）
* 策略回测 + 实盘执行

---

## 👤 作者

桑桑（AI + Web3 + 交易方向实践）
