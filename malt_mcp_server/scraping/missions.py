from __future__ import annotations

import logging
from typing import Any

from patchright.async_api import Error as PlaywrightError
from patchright.async_api import Locator, Page

from malt_mcp_server.core.exceptions import MaltScrapingError

logger = logging.getLogger(__name__)

# Selectors verified on live Malt messages HTML (2026-04-29).
# Two types of items: conversations (.conversation-summary__wrapper)
# and project offers (.client-project-offer-summary__wrapper).
_SEL_CONVERSATION = ".conversation-summary__wrapper"
_SEL_PROJECT_OFFER = ".client-project-offer-summary__wrapper"
_SEL_CONV_NAME = ".conversation-summary-header__title"
_SEL_CONV_COMPANY = ".client-company-overview__name"
_SEL_CONV_DATE = ".conversation-summary-header__date"
_SEL_CONV_LAST_MSG = ".conversation-summary__last-message"
_SEL_CONV_STATUS = ".conversation-summary__activity_status"
_SEL_OFFER_LAST_MSG = ".client-project-offer-summary__last-message"
_SEL_OFFER_STATUS = ".client-project-offer-summary__activity_status"
_SEL_LIST = "#messengerConversationList"


async def scrape_missions(page: Page) -> list[dict[str, Any]]:
    """Extract the conversation/mission list from the Malt messages page."""
    logger.info("Scraping messages: %s", page.url)

    try:
        await page.wait_for_function(
            "() => !document.title.includes('instant')",
            timeout=30_000,
        )
        await page.wait_for_selector(_SEL_LIST, state="visible", timeout=15_000)
    except PlaywrightError as e:
        title = await page.title()
        raise MaltScrapingError(
            f"Messages page did not render. URL: {page.url} | Title: {title}"
        ) from e

    # Scroll the conversation list to load all lazy-loaded items.
    scrollable = (
        page.locator(_SEL_LIST)
        .locator("xpath=ancestor::*[contains(@class,'scrollable')]")
        .first
    )
    all_items_sel = f"{_SEL_CONVERSATION}, {_SEL_PROJECT_OFFER}"
    await _scroll_to_load_all(scrollable, all_items_sel, page)

    # Parse all items in DOM order to preserve Malt's chronological sort.
    all_items = page.locator(all_items_sel)
    count = await _safe_count(all_items)
    missions: list[dict[str, Any]] = []

    for i in range(count):
        el = all_items.nth(i)
        cls = await el.get_attribute("class") or ""
        if "conversation-summary__wrapper" in cls:
            item = await _parse_conversation(el)
        else:
            item = await _parse_offer(el)
        if item:
            missions.append(item)

    if not missions:
        raise MaltScrapingError("No missions found in inbox.")

    return missions


async def _parse_conversation(el: Locator) -> dict[str, Any] | None:
    try:
        name = await _el_text(el.locator(_SEL_CONV_NAME))
        company = await _el_text(el.locator(_SEL_CONV_COMPANY))
        date = await _el_text(el.locator(_SEL_CONV_DATE))
        last_msg = await _el_text(el.locator(_SEL_CONV_LAST_MSG))
        status = await _el_text(el.locator(_SEL_CONV_STATUS))

        if not name:
            return None

        result: dict[str, Any] = {
            "type": "conversation",
            "name": name,
            "date": date,
        }
        if company:
            result["company"] = company
        if last_msg:
            result["last_message"] = last_msg
        if status:
            result["status"] = status
        return result
    except PlaywrightError:
        logger.debug("Failed to parse conversation item")
        return None


async def _parse_offer(el: Locator) -> dict[str, Any] | None:
    try:
        title = await _el_text(el.locator(_SEL_CONV_NAME))
        company = await _el_text(el.locator(_SEL_CONV_COMPANY))
        date = await _el_text(el.locator(_SEL_CONV_DATE))
        last_msg = await _el_text(el.locator(_SEL_OFFER_LAST_MSG))
        status = await _el_text(el.locator(_SEL_OFFER_STATUS))

        result: dict[str, Any] = {
            "type": "project_offer",
            "date": date,
        }
        if title:
            result["title"] = title
        if company:
            result["company"] = company
        if last_msg:
            result["last_message"] = last_msg
        if status:
            result["status"] = status
        return result
    except PlaywrightError:
        logger.debug("Failed to parse offer item")
        return None


async def _el_text(locator: Locator) -> str | None:
    try:
        if await locator.count() > 0:
            text = await locator.first.inner_text()
            return text.strip() if text else None
    except PlaywrightError:
        return None
    return None


async def _safe_count(locator: Locator) -> int:
    try:
        return await locator.count()
    except PlaywrightError:
        return 0


_MAX_SCROLLS = 20


async def _scroll_to_load_all(
    scrollable: Locator,
    items_selector: str,
    page: Page,
) -> None:
    """Scroll the conversation list container to load all items."""
    prev_count = 0
    for _ in range(_MAX_SCROLLS):
        current_count = await _safe_count(page.locator(items_selector))
        if current_count == prev_count and prev_count > 0:
            break
        prev_count = current_count
        try:
            await scrollable.evaluate("el => el.scrollTop = el.scrollHeight")
        except PlaywrightError:
            break
        await page.wait_for_timeout(1000)
    logger.info("Loaded %d items after scrolling", prev_count)
