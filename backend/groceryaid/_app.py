"""The ASGI application"""

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from hrefs.starlette import HrefMiddleware

from . import api

app = fastapi.FastAPI(
    title="Grocery Aid",
    description="App aiding grocery shopping in Finland",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(HrefMiddleware)

app.include_router(api.app, prefix="/api/v1")
