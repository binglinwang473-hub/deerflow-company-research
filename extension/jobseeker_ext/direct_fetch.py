"""免费的 web_fetch 替代：直接用 httpx 抓取网页 + DeerFlow 自带的 Readability 提取正文。
上游默认的 Jina Reader 在匿名模式下可能因网络信誉被拒（401），这里不依赖任何第三方 API Key。"""
import asyncio
import httpx
from langchain.tools import tool
from deerflow.utils.readability import ReadabilityExtractor

_extractor = ReadabilityExtractor()
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}


@tool("web_fetch", parse_docstring=True)
async def web_fetch_tool(url: str) -> str:
    """Fetch the readable text of a public web page at a given URL.
    Only fetch EXACT URLs returned by web_search or provided by the user. URLs must include https://.

    Args:
        url: The URL to fetch.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15, headers=_HEADERS) as c:
            r = await c.get(url)
        if r.status_code >= 400:
            return f"Error: HTTP {r.status_code} for {url}"
        html = r.text[:2_000_000]
        article = await asyncio.to_thread(_extractor.extract_article, html, url=url)
        return article.to_markdown()[:6000]
    except Exception as e:  # noqa: BLE001
        return f"Error: failed to fetch {url}: {type(e).__name__}"
