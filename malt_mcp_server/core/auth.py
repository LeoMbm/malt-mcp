"""Authentication detection and session management for Malt."""

import logging

from patchright.async_api import Page

from malt_mcp_server.constants import MALT_BASE_URL, MALT_LOGIN_URL
from malt_mcp_server.core.exceptions import MaltAuthError

logger = logging.getLogger(__name__)


async def is_authenticated(page: Page) -> bool:
    """Check if the current browser session is authenticated on Malt."""
    url = page.url
    if MALT_LOGIN_URL in url or url == f"{MALT_BASE_URL}/":
        return False

    try:
        await page.goto(MALT_BASE_URL, wait_until="domcontentloaded")
        current_url = page.url
        return MALT_LOGIN_URL not in current_url
    except Exception:
        logger.warning("Failed to check authentication status")
        return False


async def require_auth(page: Page) -> None:
    """Raise MaltAuthError if the session is not authenticated."""
    if not await is_authenticated(page):
        raise MaltAuthError("Not logged in to Malt. Run: malt-mcp --login")


async def wait_for_login(page: Page, *, timeout_ms: int = 300_000) -> None:
    """Navigate to Malt login page and wait for the user to log in manually.

    Args:
        page: Browser page to use.
        timeout_ms: Max time to wait for login (default: 5 minutes).
    """
    await page.goto(MALT_LOGIN_URL, wait_until="domcontentloaded")
    logger.info("Waiting for manual login on Malt...")

    try:
        await page.wait_for_url(
            lambda url: MALT_LOGIN_URL not in url,
            timeout=timeout_ms,
        )
        logger.info("Login successful")
    except Exception as e:
        raise MaltAuthError(f"Login timed out after {timeout_ms // 1000}s: {e}") from e
