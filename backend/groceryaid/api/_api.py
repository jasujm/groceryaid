"""API setup"""

import fastapi

from . import stores

app = fastapi.FastAPI(
    title="Grocery Aid API",
    description="SaaS platform to make grocery shopping easier and more enjoyable",
)

app.include_router(stores.router, prefix="/stores", tags=["stores"])
