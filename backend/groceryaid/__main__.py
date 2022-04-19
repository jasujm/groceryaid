"""Command line interface"""

import asyncio
import typing

import typer

from . import db
from .retail import RetailChain, tasks as retail_tasks

cli = typer.Typer()


@cli.command()
def init():
    """Bootstrap the application"""
    asyncio.run(db.init())


async def _fetch_stores_async(chains: list[RetailChain]):
    for chain in chains:
        await retail_tasks.fetch_and_save_stores_and_products(chain)


@cli.command()
def fetch_stores(chains: typing.Optional[list[RetailChain]] = None):
    """Fetch store and product data"""
    chains = (
        chains
        if chains
        else [chain for chain in RetailChain if chain is not RetailChain.FAKER]
    )
    asyncio.run(_fetch_stores_async(chains))


if __name__ == "__main__":
    cli()
