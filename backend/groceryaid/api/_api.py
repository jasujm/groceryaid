"""API setup"""

import fastapi

from . import stores, storevisits

app = fastapi.APIRouter()

app.include_router(stores.router, prefix="/stores", tags=["stores"])
app.include_router(storevisits.router, prefix="/storevisits", tags=["storevisits"])
