"""Command line interface"""

import asyncio

from .tasks import fetch_and_save_stores_and_prices

if __name__ == "__main__":
    asyncio.run(fetch_and_save_stores_and_prices())
