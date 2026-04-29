from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from malt_mcp_server.constants import MALT_ANALYTICS_URL, TOOL_TIMEOUT_SECONDS
from malt_mcp_server.core.auth import require_auth
from malt_mcp_server.core.browser import BrowserManager
from malt_mcp_server.core.exceptions import (
    MaltAuthError,
    MaltNetworkError,
    MaltScrapingError,
)
from malt_mcp_server.scraping.stats import scrape_statistics


def _get_browser(ctx: Context) -> BrowserManager:
    return ctx.lifespan_context["browser"]


def register_stats_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
        tags={"stats", "scraping"},
    )
    async def get_statistics(
        ctx: Context,
    ) -> dict[str, Any]:
        """Get your Malt freelance statistics.

        Returns Super Malter points, visibility stats (favorites,
        search appearances, profile views), project reviews/rating,
        and keyword rankings.
        """
        browser = _get_browser(ctx)

        try:
            await require_auth(browser.page)
        except MaltAuthError as e:
            raise ToolError(str(e)) from e

        await ctx.info(f"Fetching analytics: {MALT_ANALYTICS_URL}")

        try:
            await browser.navigate(MALT_ANALYTICS_URL)
        except MaltNetworkError as e:
            raise ToolError(f"Could not load analytics: {e}") from e

        try:
            stats = await scrape_statistics(browser.page)
        except MaltScrapingError as e:
            raise ToolError(f"Failed to parse analytics: {e}") from e

        await ctx.info("Analytics loaded")
        return stats
