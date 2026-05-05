from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

import database
from routers import ai, auth, board

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(board.router)
app.include_router(ai.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if STATIC_DIR.exists():
    _static_root = STATIC_DIR.resolve()

    @app.get("/{path:path}", include_in_schema=False)
    async def serve_spa(path: str):
        html_file = (STATIC_DIR / f"{path}.html").resolve()
        if html_file.is_file() and html_file.is_relative_to(_static_root):
            return FileResponse(html_file)
        exact = (STATIC_DIR / path).resolve()
        if exact.is_file() and exact.is_relative_to(_static_root):
            return FileResponse(exact)
        return FileResponse(STATIC_DIR / "index.html")
