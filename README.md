# mcp_client_demo

基于 mcp 官方代码示例做出改进，实现 sse, stdio, stream 三种连接方式，并调用本地大模型，在线大模型对话 🚀

## 功能特性 ✨

- 支持多种 MCP 连接方式：
  - SSE (Server-Sent Events) 🌐
  - Stdio (标准输入输出) 💻
  - Streamable HTTP 🔄
- 支持本地大模型和在线大模型对话 🤖
- 可配置的模型参数和连接设置 ⚙️
- 工具自动发现和调用 🔍

## 配置说明 📝

在 `config/config.yaml` 文件中进行配置：

```yaml
model: # 使用的模型名称 🧠
max_tokens: 8096 # 最大token数 📏
base_url: # LLM API基础URL 🔗
api_key: # API密钥 🔐
mcp_type: sse # MCP连接类型: sse | stdio | streamablehttp 🔄
mcp_url: # 当mcp_type为sse或streamablehttp时设置此参数 🌐
server_script_path: ./server.py # 当mcp_type为stdio时设置此参数 💻
```

## 安装与运行 ⚡

1. 克隆项目到本地 📥
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 根据需要修改 `config/config.yaml` 配置文件 ⚙️
4. 运行客户端：
   ```bash
   python client.py
   ```

## 使用方法 🎯

运行 [client.py](file://d:\workplace\mcp_client_demo\client.py) 后，程序会自动连接到配置的 MCP 服务器，并显示可用工具列表。用户可以输入自然语言查询，系统会自动调用相应的工具并返回结果。✅

输入 `quit` 退出程序。👋

## 项目结构 📁

- client.py: 主客户端程序，处理与 MCP 服务器的交互和用户对话 💬
- utils.py: 工具函数集合，包括配置读取、LLM 客户端创建和不同连接方式的实现 🔧
- `config/config.yaml`: 配置文件，包含模型参数和连接设置 ⚙️

