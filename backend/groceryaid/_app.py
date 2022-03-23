"""The ASGI application"""

import fastapi
from hrefs.starlette import HrefMiddleware

from . import api

app = fastapi.FastAPI()

app.add_middleware(HrefMiddleware)

app.mount("/api/v1", api.app)
