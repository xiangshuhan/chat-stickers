"""Read-only sticker MCP. Run locally via stdio or host via Streamable HTTP."""
import json
import os
from pathlib import Path
from urllib.parse import quote

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent

ROOT = Path(__file__).resolve().parent
CATALOG = json.loads((ROOT / "stickers.json").read_text(encoding="utf-8"))
mcp = FastMCP("chat-stickers", host="0.0.0.0", port=int(os.getenv("PORT", "8000")),
              stateless_http=True, json_response=True)

def sticker_record(item):
    ref = os.getenv("STICKER_REF", "main")
    repo = os.getenv("STICKER_REPO", "xiangshuhan/chat-stickers")
    url = f"https://cdn.jsdelivr.net/gh/{repo}@{quote(ref, safe='')}/{quote(item['path'], safe='/')}"
    return {**item, "url": url, "markdown": f"![{item['description']}]({url})"}

@mcp.tool()
def list_stickers(query: str = "") -> list[dict]:
    """列出表情包名称、用途、标签及图片地址。query 可按名称或情绪筛选。"""
    return [sticker_record(item) for item in CATALOG
            if query.casefold() in json.dumps(item, ensure_ascii=False).casefold()]

@mcp.tool()
def show_sticker(filename: str) -> list[TextContent | ImageContent]:
    """按 list_stickers 返回的准确文件名展示图片，附 CDN 地址和 Markdown。"""
    item = next((entry for entry in CATALOG if entry["filename"] == filename), None)
    if item is None:
        raise ValueError("未知表情包，请先调用 list_stickers。")
    import base64
    image = (ROOT / item["path"]).read_bytes()
    return [TextContent(type="text", text=json.dumps(sticker_record(item), ensure_ascii=False)),
            ImageContent(type="image", data=base64.b64encode(image).decode(), mimeType="image/jpeg")]

if __name__ == "__main__":
    mcp.run(transport="streamable-http" if os.getenv("TRANSPORT") == "http" else "stdio")
