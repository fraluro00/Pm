# PM Kanban

AI-powered Kanban board. FastAPI backend + Next.js frontend, served via Docker.

## Requirements

- Docker
- OpenRouter API key → [openrouter.ai](https://openrouter.ai)

## Setup

```bash
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY
```

## Run

```bash
./scripts/start.sh   # builds image, starts container at http://localhost:8000
./scripts/stop.sh    # stop and remove container
```

## Credentials

Default login: `user` / `password`

## Dev

```bash
# Backend tests
cd backend && uv run pytest

# Frontend dev server
cd frontend && npm install && npm run dev   # http://localhost:3000
```