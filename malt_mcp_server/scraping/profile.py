from __future__ import annotations

import logging
import re
from typing import Any

from patchright.async_api import Error as PlaywrightError
from patchright.async_api import Page

from malt_mcp_server.core.exceptions import MaltScrapingError

logger = logging.getLogger(__name__)

# CSS selectors for profile fields.
# Each selector tries data-testid first, then common class fallbacks.
# Adjust these when Malt changes their HTML.
_SEL_HEADLINE = "[data-testid='profile-headline'], .profile-headline, h1"
_SEL_RATE = "[data-testid='profile-rate'], .profile-rate, .daily-rate"
_SEL_RATING = "[data-testid='profile-rating'], .profile-rating, .rating-value"
_SEL_MISSIONS = "[data-testid='missions-count'], .missions-count"
_SEL_SKILLS = "[data-testid='skill-tag'], .skill-tag, .profile-skill"
_SEL_BIO = "[data-testid='profile-bio'], .profile-bio, .profile-description"
_SEL_AVAILABILITY = (
    "[data-testid='availability-status'], .availability-badge, .availability-status"
)
_SEL_EXPERIENCE = "[data-testid='experience-years'], .experience-years"


async def scrape_profile(page: Page) -> dict[str, Any]:
    """Extract profile data from the current Malt profile page."""
    data: dict[str, Any] = {}

    data["url"] = page.url

    headline = await _text(page, _SEL_HEADLINE)
    if headline:
        data["headline"] = headline

    daily_rate = await _text(page, _SEL_RATE)
    if daily_rate:
        data["daily_rate"] = _parse_rate(daily_rate)
        data["daily_rate_raw"] = daily_rate

    rating = await _text(page, _SEL_RATING)
    if rating:
        data["rating"] = _parse_float(rating)

    missions = await _text(page, _SEL_MISSIONS)
    if missions:
        data["missions_count"] = _parse_int(missions)

    skills = await _all_texts(page, _SEL_SKILLS)
    if skills:
        data["skills"] = skills

    bio = await _text(page, _SEL_BIO)
    if bio:
        data["bio"] = bio

    availability = await _text(page, _SEL_AVAILABILITY)
    if availability:
        data["availability"] = availability

    experience_years = await _text(page, _SEL_EXPERIENCE)
    if experience_years:
        data["experience_years"] = _parse_int(experience_years)

    if len(data) <= 1:
        raise MaltScrapingError("No profile data found. Selectors may be outdated.")

    return data


async def _text(page: Page, selector: str) -> str | None:
    """Get innerText of first matching element, or None."""
    try:
        locator = page.locator(selector)
        if await locator.count() > 0:
            text = await locator.first.inner_text()
            return text.strip() if text else None
    except PlaywrightError:
        logger.debug("Selector not found: %s", selector)
    return None


async def _all_texts(page: Page, selector: str) -> list[str]:
    """Get innerText of all matching elements."""
    try:
        elements = page.locator(selector)
        count = await elements.count()
        return [
            text
            for i in range(count)
            if (text := (await elements.nth(i).inner_text()).strip())
        ]
    except PlaywrightError:
        logger.debug("Selector not found: %s", selector)
    return []


def _parse_rate(raw: str) -> int | None:
    """Extract numeric rate from strings like '500 EUR/jour' or '500.00€/j'."""
    match = re.search(r"(\d[\d\s]*[.,]?\d*)", raw)
    if match:
        num_str = match.group(1).replace(" ", "")
        num_str = num_str.replace(",", ".")
        try:
            return round(float(num_str))
        except ValueError:
            return None
    return None


def _parse_float(raw: str) -> float | None:
    match = re.search(r"(\d+[.,]?\d*)", raw)
    if match:
        return float(match.group(1).replace(",", "."))
    return None


def _parse_int(raw: str) -> int | None:
    match = re.search(r"(\d+)", raw)
    if match:
        return int(match.group(1))
    return None
