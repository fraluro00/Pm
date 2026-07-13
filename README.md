# PM Kanban

An AI-powered Kanban board — a FastAPI backend and Next.js frontend served from a single Docker container, with LLM features via OpenRouter.

**Run it**:

```bash
cp .env.example .env    # set OPENROUTER_API_KEY (get one at openrouter.ai)
./scripts/start.sh      # builds image, starts container at http://localhost:8000
./scripts/stop.sh       # stop and remove container
```

Default login: `user` / `password`

## The app

### Board

A Kanban board for managing tasks across columns, backed by a persistent API rather than browser state.

### AI assistance

LLM-powered features driven by OpenRouter — the AI works with your board through the backend.

### Accounts

Simple credential login; the container ships with a default user.

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js, TypeScript |
| Backend | FastAPI (Python / uv) |
| AI | OpenRouter |
| Runtime | Single Docker container on port 8000 |
| Tests | pytest (backend) |

## Architecture

```
Next.js frontend → FastAPI backend → OpenRouter
```

- One Docker image serves both frontend and API on port 8000
- Development mode: `cd backend && uv run pytest` for tests, `cd frontend && npm run dev` for the UI at http://localhost:3000
- Configuration is a single `.env` file with the OpenRouter key
