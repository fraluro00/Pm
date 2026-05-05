# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the app (Docker):**
```bash
./scripts/start.sh   # build image + start container at http://localhost:8000
./scripts/stop.sh    # stop and remove container
```

**Frontend dev (outside Docker):**
```bash
cd frontend
npm run dev          # dev server at http://localhost:3000
npm run build        # static export to frontend/out/
npm run lint
npm run test:unit    # vitest (unit tests)
npm run test:e2e     # playwright (targets http://localhost:8000 — requires Docker running)
```

**Backend tests (outside Docker):**
```bash
cd backend
uv run pytest                          # all tests
uv run pytest tests/test_api.py::test_name  # single test
```

## Architecture

**Deployment:** Multi-stage Dockerfile. Node stage builds NextJS static export (`frontend/out/`); Python stage (FastAPI + uvicorn) serves it via `StaticFiles` mount at `/`. All traffic on port 8000. SQLite DB at `/app/data/kanban.db` persisted via Docker volume (`-v $PROJECT_DIR/data:/app/data`).

**Backend (`backend/`):**
- `main.py` — FastAPI app, all routes, `lifespan` calls `database.init_db()`
- `auth.py` — session cookie via `itsdangerous`; hardcoded `user`/`password`
- `database.py` — SQLite with raw `sqlite3`; `init_db()` creates tables + seeds default user/board
- `models.py` — Pydantic models: `BoardData`, `Column`, `Card`
- `ai.py` — OpenAI SDK pointed at OpenRouter; `AIResponse` model (`message`, `board_update`)

**API routes:**
| Method | Path | Auth |
|---|---|---|
| POST | `/api/auth/login` | — |
| POST | `/api/auth/logout` | — |
| GET | `/api/auth/me` | required |
| GET | `/api/board` | required |
| PUT | `/api/board` | required |
| POST | `/api/ai/chat` | required |
| POST | `/api/ai/test` | — |

**Board persistence:** `PUT /api/board` replaces entire board (delete all columns+cards for user, reinsert). Frontend debounces this 500ms after any change.

**AI flow:** `POST /api/ai/chat` sends full board JSON + conversation history to OpenRouter. AI responds with `{message, board_update}` JSON; if `board_update` is non-null, backend calls `save_board()` before returning.

**Frontend (`frontend/src/app/`):**
- `page.tsx` — fetches `/api/auth/me` on load; redirects to `/login` if 401; renders `KanbanBoard`
- `KanbanBoard.tsx` — owns all board state; fetches on mount, debounced PUT on change; renders columns + `AISidebar`
- `AISidebar.tsx` — chat UI; calls `POST /api/ai/chat`; `board_update` in response triggers `onBoardUpdate` callback
- Drag-and-drop: `@dnd-kit` with `closestCorners` strategy; 6px activation distance

**Data model (TypeScript + Python both use this shape):**
```
BoardData: { columns: Column[]; cards: Record<string, Card> }
Column: { id: string; title: string; cardIds: string[] }
Card: { id: string; title: string; details: string }
```

## Business Requirements

- User signs in (hardcoded `user`/`password` for MVP)
- One Kanban board per user; fixed columns (can be renamed)
- Cards: drag-and-drop between columns, inline edit
- AI chat sidebar: can create/edit/move cards via natural language

## Technical Decisions

- NextJS frontend (static export)
- Python FastAPI backend; serves static NextJS site at `/`
- `uv` as Python package manager
- OpenRouter for AI (`openai/gpt-oss-120b` model)
- SQLite via built-in `sqlite3` (no ORM)
- Vercel for hosting (future); `VERCEL_API_KEY` in `.env`

## Color Scheme

| Token | Value | Usage |
|---|---|---|
| `--accent-yellow` | `#ecad0a` | Column accent bars, highlights |
| `--primary-blue` | `#209dd7` | Links, key sections |
| `--secondary-purple` | `#753991` | Submit buttons, important actions |
| `--navy-dark` | `#032147` | Main headings |
| `--gray-text` | `#888888` | Supporting text, labels |

## Coding Standards

1. Latest library versions, idiomatic approaches
2. Simple — never over-engineer, no unnecessary defensive programming, no extra features
3. No emojis, minimal README
4. Identify root cause before fixing — prove with evidence, then fix

## Working Documentation

Plans and design docs in `docs/`. Review `docs/PLAN.md` before proceeding.
