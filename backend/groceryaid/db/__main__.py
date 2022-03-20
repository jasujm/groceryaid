"""Command line interface"""

import asyncio

from ._db import init

if __name__ == "__main__":
    asyncio.run(init())
