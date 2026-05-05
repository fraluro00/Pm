# Backend Codebase

Python FastAPI app. Runs inside Docker via uv. Serves the static NextJS frontend and all API routes.

## Stack

- **Python 3.12**
- **FastAPI** — web framework
- **uvicorn** — ASGI server
- **uv** — package manager (runs inside Docker; deps declared in pyproject.toml)

## Running

Start/stop via `scripts/start.sh` (or `.bat` on Windows). The Dockerfile installs uv, syncs deps, copies source, runs uvicorn on port 8000.

## File Structure

```
backend/
  main.py          — FastAPI app entrypoint
  pyproject.toml   — Python project + dependency declarations
```

## Routes

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Returns `{"status": "ok"}` |
| GET | `/` | Hello world HTML (temporary; replaced by static NextJS in Part 3) |

## Environment Variables

Passed in via `--env-file .env` in the Docker run command:

- `OPENROUTER_API_KEY` — used in Part 8+ for AI calls
