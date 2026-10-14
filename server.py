"""Read-only sticker MCP. Run locally via stdio or host via Streamable HTTP."""
import json
import os
from pathlib import Path
from urllib.parse import quote

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, CallToolResult, ToolAnnotations

ROOT = Path(__file__).resolve().parent
CATALOG = json.loads((ROOT / "stickers.json").read_text(encoding="utf-8"))
mcp = FastMCP("chat-stickers", host="0.0.0.0", port=int(os.getenv("PORT", "8000")),
              stateless_http=True, json_response=True)
UI_URI = "ui://stickers/display-v1.html"
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)

@mcp.resource(UI_URI, name="sticker-display", mime_type="text/html;profile=mcp-app",
              meta={"ui": {"prefersBorder": False,
                           "csp": {"resourceDomains": ["https://cdn.jsdelivr.net"]}},
                    "openai/widgetDescription": "在对话中展示一张已选中的表情包。",
                    "openai/widgetPrefersBorder": False,
                    "openai/widgetCSP": {"connect_domains": [],
                                         "resource_domains": ["https://cdn.jsdelivr.net"]}})
def sticker_display() -> str:
    return (ROOT / "ui" / "sticker.html").read_text(encoding="utf-8")

def sticker_record(item):
    ref = os.getenv("STICKER_REF", "main")
    repo = os.getenv("STICKER_REPO", "xiangshuhan/chat-stickers")
    url = f"https://cdn.jsdelivr.net/gh/{repo}@{quote(ref, safe='')}/{quote(item['path'], safe='/')}"
    return {**item, "url": url, "markdown": f"![{item['description']}]({url})"}

@mcp.tool(annotations=READ_ONLY)
def list_stickers(query: str = "") -> list[dict]:
    """列出表情包名称、用途、标签及图片地址。query 可按名称或情绪筛选。"""
    return [sticker_record(item) for item in CATALOG
            if query.casefold() in json.dumps(item, ensure_ascii=False).casefold()]

@mcp.tool(annotations=READ_ONLY, structured_output=False,
          meta={"ui": {"resourceUri": UI_URI}, "openai/outputTemplate": UI_URI,
                "openai/toolInvocation/invoking": "正在发表情包",
                "openai/toolInvocation/invoked": "表情包已准备好"})
def show_sticker(filename: str) -> CallToolResult:
    """在聊天内展示一张表情包。先调用 list_stickers 检索，再传入返回的准确文件名。"""
    item = next((entry for entry in CATALOG if entry["filename"] == filename), None)
    if item is None:
        raise ValueError("未知表情包，请先调用 list_stickers。")
    import base64
    image = (ROOT / item["path"]).read_bytes()
    record = sticker_record(item)
    return CallToolResult(structuredContent={"sticker": record}, content=[
        TextContent(type="text", text=f"展示表情包：{item['filename']}。{item['description']}"),
        ImageContent(type="image", data=base64.b64encode(image).decode(), mimeType="image/jpeg")])

if __name__ == "__main__":
    mcp.run(transport="streamable-http" if os.getenv("TRANSPORT") == "http" else "stdio")
