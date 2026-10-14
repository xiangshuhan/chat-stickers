# chat-stickers

公开表情包仓库，图片用途由 `stickers.json` 的名称、描述及标签说明。

## 示例图片

![抱臂无语](https://cdn.jsdelivr.net/gh/xiangshuhan/chat-stickers@main/stickers/%E6%8A%B1%E8%87%82%E6%97%A0%E8%AF%AD.jpg)

## MCP 工具

- `list_stickers(query="")`：按名称、描述、情绪标签查找表情包。
- `show_sticker(filename)`：返回 CDN 地址、Markdown 和 MCP 图片内容。

URL、Markdown 和 MCP 图片内容能否显示，取决于客户端；接入后请实际验证。

## 本地启动（支持本地 MCP 的客户端）

需要 Python 3.10 或更新版本。克隆仓库后运行：

```sh
python -m pip install -r requirements.txt
python server.py
```

在客户端 MCP 配置中使用 `python` 作为 command，仓库内 `server.py` 的绝对路径作为 args。Windows 可使用 Python 可执行文件的绝对路径。

## 远程启动（ChatGPT 的远程连接）

GitHub 与 jsDelivr 只提供文件，不运行 MCP 服务。将本仓库 Dockerfile 部署到支持长期 HTTP 服务的托管平台，配置 HTTPS 公网入口。容器内设置 `TRANSPORT=http`；`PORT` 默认 8000，可由平台指定。MCP 路径是 `/mcp`。随后把该服务的 HTTPS MCP 地址添加到支持远程 MCP 的客户端。

本服务只有读取公开图片的两个工具，无写入接口，也不需要 GitHub token。无需在代码里添加凭据。

`STICKER_REPO` 默认 `xiangshuhan/chat-stickers`，`STICKER_REF` 默认 `main`；可用提交 SHA 固定 CDN 版本。

## 自然聊天规则

聊天时可以根据语境自然主动使用表情包，不需要每次征求同意，也不要每句话都发。先从目录选择合适标签，再调用 show_sticker。不要虚构图片地址。

## 添加图片

将图片放入 `stickers/`，同步更新 `stickers.json`。本示例支持 JPEG；添加其他格式时需同步更新服务返回的 MIME 类型。图片保留其原有权利，本仓库不为第三方图片另行授予许可。
