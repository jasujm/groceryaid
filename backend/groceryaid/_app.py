"""The ASGI application"""

import fastapi
from hrefs.starlette import HrefMiddleware

from . import api

app = fastapi.FastAPI(
    title="Grocery Aid",
    description="App aiding grocery shopping in Finland",
)

app.add_middleware(HrefMiddleware)

app.include_router(api.app, prefix="/api/v1")
