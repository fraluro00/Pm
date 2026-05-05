# Project Management MVP — Detailed Plan

## Part 1: Plan

**Goal:** Produce this document and the frontend/CLAUDE.md. Get user sign-off.

### Steps
- [x] Explore existing frontend code
- [x] Write detailed PLAN.md (this document)
- [x] Write frontend/CLAUDE.md
- [ ] User reviews and approves plan

### Success Criteria
- User has approved this plan in conversation before any build work begins

---

## Part 2: Scaffolding

**Goal:** Docker container runs locally; FastAPI serves a "hello world" HTML page at `/` and a test API endpoint responds.

### Steps
- [x] Create `backend/` Python project with `uv` (pyproject.toml)
- [x] Add FastAPI + uvicorn as dependencies via uv
- [x] Create `backend/main.py` with a GET `/` that returns static HTML "hello world" and a GET `/api/health` that returns `{"status": "ok"}`
- [x] Create `Dockerfile` at project root: installs uv, installs python deps, copies backend, runs uvicorn on port 8000
- [x] Create `scripts/start.sh` (Mac/Linux) and `scripts/start.bat` (Windows) that run `docker build` + `docker run`
- [x] Create `scripts/stop.sh` (Mac/Linux) and `scripts/stop.bat` (Windows) that stop and remove the container
- [ ] Verify: `docker build` succeeds, container starts, `curl http://localhost:8000/` returns HTML, `curl http://localhost:8000/api/health` returns JSON

### Tests
- Manual: curl `/` → HTML with "hello world"
- Manual: curl `/api/health` → `{"status": "ok"}`

### Success Criteria
- Docker container builds and starts without errors
- Both endpoints respond correctly
- Start/stop scripts work on Mac

---

## Part 3: Add in Frontend

**Goal:** NextJS app statically built, copied into Docker image, served by FastAPI at `/`.

### Steps
- [x] Add `next build` output mode `export` to `frontend/next.config.ts` (static export)
- [x] Update `Dockerfile`: add Node build stage, runs `npm ci && npm run build` in `frontend/`, copies `frontend/out/` into the Python image
- [x] Update `backend/main.py`: mount the `out/` directory as static files; serve `index.html` as fallback for all non-API routes (SPA routing)
- [ ] Verify: Kanban board renders at `http://localhost:8000/`
- [ ] Add frontend unit tests for `moveCard` logic (vitest) — these run outside Docker during development
- [ ] Add Playwright e2e smoke test: page loads, 5 columns visible, drag a card, column rename works

### Tests
- `npm run test:unit` in `frontend/` — all pass
- `npm run test:e2e` in `frontend/` — smoke test passes against dev server
- Manual Docker: Kanban board visible at `http://localhost:8000/`

### Success Criteria
- Static build produces `frontend/out/`
- Docker container serves full Kanban UI
- All existing unit and e2e tests pass

---

## Part 4: Fake User Sign-in

**Goal:** `/` redirects to login if not authenticated. Login with `user`/`password` sets a session cookie. Logout clears it.

### Steps
- [x] Add `itsdangerous` to backend deps for session token signing
- [x] Add `POST /api/auth/login` route: accepts `{username, password}`, validates against hardcoded `user`/`password`, returns signed session cookie (httponly)
- [x] Add `POST /api/auth/logout` route: clears the cookie
- [x] Add `GET /api/auth/me` route: returns `{username}` if authenticated, 401 otherwise
- [x] Create `frontend/src/app/login/page.tsx`: login form (username + password fields, submit button)
- [x] Add auth check in `frontend/src/app/page.tsx`: fetch `/api/auth/me` on load; if 401, redirect to `/login`
- [x] Add logout button to Kanban header that calls `/api/auth/logout` then redirects to `/login`
- [ ] Verify end-to-end in Docker

### Tests
- Backend unit test: POST `/api/auth/login` with correct creds → 200 + cookie set
- Backend unit test: POST `/api/auth/login` with wrong creds → 401
- Backend unit test: GET `/api/auth/me` without cookie → 401
- Backend unit test: GET `/api/auth/me` with valid cookie → 200
- Playwright e2e: visiting `/` without session redirects to `/login`
- Playwright e2e: logging in with `user`/`password` shows Kanban board
- Playwright e2e: logout returns to login page

### Success Criteria
- Cannot access Kanban without login
- Login/logout cycle works end-to-end in Docker

---

## Part 5: Database Modeling

**Goal:** Propose and document SQLite schema for the Kanban; get user sign-off before writing any DB code.

### Steps
- [ ] Design schema (see below) and save as `docs/DATABASE.md`
- [ ] User reviews and approves schema

### Proposed Schema

**users** table
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `username` TEXT UNIQUE NOT NULL

**boards** table
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id` INTEGER NOT NULL REFERENCES users(id)
- `title` TEXT NOT NULL DEFAULT 'My Board'

**columns** table
- `id` TEXT PRIMARY KEY  (e.g. "col-backlog")
- `board_id` INTEGER NOT NULL REFERENCES boards(id)
- `title` TEXT NOT NULL
- `position` INTEGER NOT NULL  (ordering)

**cards** table
- `id` TEXT PRIMARY KEY  (e.g. "card-abc123")
- `column_id` TEXT NOT NULL REFERENCES columns(id)
- `title` TEXT NOT NULL
- `details` TEXT NOT NULL DEFAULT ''
- `position` INTEGER NOT NULL  (ordering within column)

### Success Criteria
- User has approved schema before Part 6 begins

---

## Part 6: Backend API

**Goal:** FastAPI routes read/write the Kanban for a given authenticated user. SQLite DB auto-created on startup.

### Steps
- [x] Use built-in `sqlite3` (no extra dep needed)
- [x] Create `backend/database.py`: init DB, create tables if not exist, seed default user `user` and board on first run
- [x] Create `backend/models.py`: Pydantic models matching schema
- [x] Add `GET /api/board` route: returns full board JSON (columns + cards) for authenticated user
- [x] Add `PUT /api/board` route: accepts full board JSON, replaces columns+cards for user
- [x] Wire up DB init on app startup (`lifespan` event)
- [x] Write backend unit tests with pytest (temp SQLite DB per test)
- [ ] Run tests and confirm passing
- [ ] Verify in Docker: board data persists across restarts

### Tests
- `pytest backend/` — all tests pass
- Manual: `curl` the board endpoints with a valid session cookie

### Success Criteria
- All pytest tests pass
- Board data persists across container restarts (SQLite file mounted as volume or baked in — volume preferred)

---

## Part 7: Frontend + Backend Integration

**Goal:** Frontend reads/writes board state via the API instead of local `useState` with `initialData`.

### Steps
- [x] Replace `initialData` in `KanbanBoard.tsx` with a `useEffect` fetch to `GET /api/board` on mount
- [x] After any board change, debounce a `PUT /api/board` call (500ms) with full board state
- [x] Show loading state while initial fetch is in progress
- [x] Show error state if fetch fails
- [x] Update unit tests to mock fetch, pass `onLogout` prop
- [x] Update Playwright config to target Docker (`http://localhost:8000`)
- [x] Update e2e tests: login flow, persistence test (add card → reload → still present)
- [ ] Run `./scripts/start.sh` and verify full flow in Docker

### Tests
- Playwright e2e: add card → reload → card persists
- Playwright e2e: drag card to different column → reload → card in new column
- Playwright e2e: rename column → reload → new name persists
- `npm run test:unit` still passes

### Success Criteria
- All board mutations persist across page reloads
- All tests pass end-to-end in Docker

---

## Part 8: AI Connectivity

**Goal:** Backend can call OpenRouter AI API. Verified with a simple arithmetic test.

### Steps
- [x] Add `openai` Python SDK to backend deps
- [x] Create `backend/ai.py`: OpenAI client pointed at OpenRouter, `MODEL` constant
- [x] Add `POST /api/ai/test` route: sends "What is 2+2?" to model, returns response text
- [x] `OPENROUTER_API_KEY` already passed via `--env-file .env` in start scripts
- [x] Backend test: mock `client.chat.completions.create`, verify route returns string
- [ ] Run `./scripts/start.sh` and `curl -X POST http://localhost:8000/api/ai/test` to confirm live AI call

### Tests
- pytest with mocked OpenRouter call passes
- Manual curl confirms real API call returns expected result

### Success Criteria
- `/api/ai/test` returns a coherent answer from the AI
- API key loaded correctly from env

---

## Part 9: AI + Kanban Structured Outputs

**Goal:** AI receives the full board JSON + conversation history, responds with a message and an optional board update.

### Steps
- [x] Define `AIResponse` in `backend/ai.py`: `message: str`, `board_update: BoardData | None`
- [x] Create `POST /api/ai/chat`: builds system prompt with board JSON, calls AI with `json_object` mode, parses response, applies `board_update` to DB if present
- [x] System prompt instructs AI to return complete board on changes, null otherwise
- [x] Backend tests: chat without update, chat with board update (verifies DB persisted), unauthenticated → 401
- [ ] Rebuild Docker and verify end-to-end with a real chat message

### Tests
- pytest tests with mocked AI responses cover both update and non-update cases
- Manual: asking AI to create a card actually creates it in the DB

### Success Criteria
- AI correctly returns structured output
- Board updates from AI are persisted

---

## Part 10: AI Chat Sidebar UI

**Goal:** Beautiful sidebar with full chat history; AI can update the Kanban and the UI auto-refreshes.

### Steps
- [x] Create `frontend/src/components/AISidebar.tsx`: fixed right panel, chat messages, textarea + send button
- [x] Style matches color scheme: purple user bubbles, navy headings, gray assistant bubbles
- [x] Conversation state + history sent with each request
- [x] `board_update` in response triggers `onBoardUpdate` callback → `setBoard` in KanbanBoard
- [x] "AI Assistant" toggle button added to Kanban header (blue outline)
- [x] Playwright e2e test: mocked `/api/ai/chat` response, verifies card appears on board
- [ ] Run `./scripts/start.sh` and verify full flow end-to-end in Docker

### Tests
- Playwright e2e: AI chat creates a card, board updates without page reload
- `npm run test:unit` still passes

### Success Criteria
- Sidebar opens/closes cleanly
- Full chat history visible
- AI-driven board changes appear immediately without reload
- All tests pass in Docker
