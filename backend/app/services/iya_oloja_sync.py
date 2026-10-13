
import logging
from typing import Any

import httpx
import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from app.database import locations as locations_db
from app.database.validation import LocationData
from app.services.cache import cache


logger = logging.getLogger("pricebiz")

API_URL = "https://iya-oloja.pages.dev/api/markets"
PAGE_SIZE = 100


class MarketSyncError(Exception):
    """Raised when the external market directory cannot be synced."""



async def _retry_delay(response, attempt: int) -> float:
    """Respect Retry-After when supplied; otherwise use backoff."""
    retry_after = response.headers.get("Retry-After")

    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(retry_after)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)

                return max(
                    0.0,
                    (retry_at - datetime.now(timezone.utc)).total_seconds(),
                )
            except (TypeError, ValueError, OverflowError):
                pass

    return min(15.0 * (2 ** attempt), 300.0)


async def fetch_all_markets() -> list[dict[str, Any]]:
    markets: list[dict[str, Any]] = []
    offset = 0

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    ) as client:
        while True:
            # Keep requests spaced out instead of rapidly exhausting
            # the API's request allowance.
            if offset > 0:
                await asyncio.sleep(1.1)

            for attempt in range(7):
                try:
                    response = await client.get(
                        API_URL,
                        params={
                            "limit": PAGE_SIZE,
                            "offset": offset,
                            "order": "asc",
                        },
                    )

                    if response.status_code == 429:
                        if attempt == 6:
                            raise MarketSyncError(
                                f"Rate limit persisted at offset {offset} "
                                "after 7 attempts. Retry the sync later."
                            )

                        delay = await _retry_delay(response, attempt)
                        logger.warning(
                            "Iya Oloja rate limit reached at offset %s. "
                            "Retrying in %.1f seconds (attempt %s/7).",
                            offset,
                            delay,
                            attempt + 1,
                        )
                        await asyncio.sleep(delay)
                        continue

                    response.raise_for_status()
                    payload = response.json()
                    break

                except httpx.HTTPStatusError as exc:
                    raise MarketSyncError(
                        f"Iya Oloja returned HTTP "
                        f"{exc.response.status_code} at offset {offset}"
                    ) from exc
                except (httpx.RequestError, ValueError) as exc:
                    if attempt == 6:
                        raise MarketSyncError(
                            f"Unable to fetch markets at offset {offset} "
                            "after 7 attempts."
                        ) from exc

                    delay = min(2.0 * (2 ** attempt), 30.0)
                    logger.warning(
                        "Request failed at offset %s. Retrying in %.1f "
                        "seconds (attempt %s/7): %s",
                        offset,
                        delay,
                        attempt + 1,
                        exc,
                    )
                    await asyncio.sleep(delay)
            else:
                raise MarketSyncError(
                    f"Unable to fetch markets at offset {offset}"
                )

            if not isinstance(payload, dict):
                raise MarketSyncError(
                    "The market API returned an invalid response."
                )

            if payload.get("success") is False:
                raise MarketSyncError(
                    f"Market API error: {payload}"
                )

            page = payload.get("data")
            if not isinstance(page, list):
                raise MarketSyncError(
                    "The market API response has no valid data list."
                )

            markets.extend(page)

            meta = payload.get("meta") or {}
            total = meta.get("total")

            if not page:
                break

            offset += len(page)

            if isinstance(total, int) and offset >= total:
                break

            if len(page) < PAGE_SIZE:
                break

    return markets

async def sync_markets() -> dict[str, int]:
    """
    Import the Iya Oloja directory into PriceBiz locations.

    Existing location documents and IDs are preserved.
    """
    markets = await fetch_all_markets()

    if not markets:
        raise MarketSyncError(
            "The API returned no markets. Sync cancelled to avoid "
            "mistaking an empty response for a successful import."
        )

    imported = 0
    skipped = 0

    for record in markets:
        if not isinstance(record, dict):
            skipped += 1
            continue

        market_name = record.get("name")
        state_name = record.get("state_name")
        lga_name = record.get("lga_name")

        if (
            not isinstance(market_name, str)
            or not market_name.strip()
            or not isinstance(state_name, str)
            or not state_name.strip()
        ):
            logger.warning(
                "Skipping market with missing name or state: %r",
                record,
            )
            skipped += 1
            continue

        values = {
            "country": "Nigeria",
            "state": state_name.strip(),
            "lga": (
                lga_name.strip()
                if isinstance(lga_name, str) and lga_name.strip()
                else None
            ),
            "area": None,
            "market": market_name.strip(),
        }

        try:
            # Apply the same schema validation as ordinary locations.
            validated = LocationData(**values).model_dump()

            await locations_db.upsert_location(**validated)
            imported += 1

        except Exception:
            logger.exception(
                "Failed to import market %r",
                market_name,
            )
            raise

    if imported:
        cache.delete_prefix("locations:")
        cache.delete_prefix("price_analysis:")

    return {
        "fetched": len(markets),
        "processed": imported,
        "skipped": skipped,
    }


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def main():
        result = await sync_markets()
        print("Iya Oloja synchronization completed:")
        print(result)

    asyncio.run(main())
