# Code Review

## Summary

This is a well-structured MVP with clear separation of concerns, a solid test pyramid (unit + integration + e2e), and clean React state management. All Critical and High issues have been fixed (commit `9640bf0`). Remaining open items are Medium and Low severity.

---

## Issues by Severity

### Critical

**~~Path traversal in SPA catch-all route~~** ✅ Fixed — commit `9640bf0`
File: `backend/main.py`

Both file-path branches now call `.resolve()` and guard with `.is_relative_to(_static_root)` before serving.

---

### High

**~~Unauthenticated endpoint that triggers paid API calls~~** ✅ Fixed — commit `9640bf0`
File: `backend/main.py`

`POST /api/ai/test` now requires `Depends(get_current_user)` and is hidden from the OpenAPI schema via `include_in_schema=False`.

---

**~~`ChatMessage.role` is unconstrained — prompt injection via history~~** ✅ Fixed — commit `9640bf0`
File: `backend/main.py`

`role` is now `Literal["user", "assistant"]`; Pydantic rejects any other value at the boundary.

---

**~~Silent data loss on board save failures~~** ✅ Fixed — commit `9640bf0`
File: `frontend/src/components/KanbanBoard.tsx`

Debounced PUT now has `.then`/`.catch`; a "Save failed — changes may be lost" message appears in the header on failure and clears on the next successful save.

---

**~~`get_board` and `save_board` crash with unhandled `TypeError` if user or board is missing~~** ✅ Fixed — commit `9640bf0`
File: `backend/database.py`

Both functions now check for `None` after each `fetchone()` and raise `HTTPException(404)` with a clear message.

---

**~~`ai_chat` endpoint does not handle OpenAI API errors~~** ✅ Fixed — commit `9640bf0`
File: `backend/main.py`

`client.chat.completions.create(...)` is now wrapped in `try/except` → `HTTPException(502)`.

---

### Medium

**`uv.lock` is not copied into the Docker image — builds are not reproducible**
File: `Dockerfile`, lines 14–15

The Dockerfile copies only `pyproject.toml` and then runs `uv sync --no-dev`. Without `uv.lock`, `uv sync` resolves dependencies at build time and may pull in different package versions on different days. By contrast the frontend stage correctly copies `package-lock.json` before `npm ci`.

Fix:

```dockerfile
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --no-dev --frozen
```

`--frozen` makes the build fail if the lockfile is out of sync rather than silently resolving a different dependency graph.

---

**Cards referenced in `cardIds` but missing from `cards` map crash column rendering**
File: `frontend/src/components/KanbanBoard.tsx`, line 212; `KanbanColumn.tsx`, line 54

```tsx
cards={column.cardIds.map((cardId) => board.cards[cardId])}
```

If `board.cards[cardId]` is `undefined` (e.g., because the AI returns a `board_update` where `cardIds` lists an ID not present in `cards`), the `Card[]` array contains `undefined` values. `KanbanColumn` then renders `KanbanCard` with an undefined `card` prop, and `card.id` on line 54 throws. This is a plausible AI failure mode — the prompt asks the AI to return the "complete" board, but it may omit cards.

Fix: filter undefined entries and optionally log a warning:

```tsx
cards={column.cardIds.flatMap((cardId) => {
  const card = board.cards[cardId];
  return card ? [card] : [];
})}
```

---

**Column title can be set to an empty string with no validation**
File: `frontend/src/components/KanbanColumn.tsx`, line 44; `backend/models.py`, line 12

Every keystroke fires `onRename`, including clearing the title entirely. An empty-string column title is then persisted to the database (`title TEXT NOT NULL` allows empty strings in SQLite). The backend model also has no `min_length` constraint.

Fix on the backend: `title: str = Field(min_length=1, max_length=200)`. On the frontend, prevent saving when the title is empty or restore the previous value on blur if empty.

---

**`pydantic` is not declared as a direct dependency**
File: `backend/pyproject.toml`

`pydantic` is used directly in `models.py` and `ai.py` but it is only an implicit transitive dependency of `fastapi`. If `fastapi` ever drops or changes its pydantic requirement, the backend silently breaks.

Fix: add `"pydantic>=2.0"` to the `dependencies` list in `pyproject.toml`.

---

**AISidebar sends unbounded conversation history on every message**
File: `frontend/src/components/AISidebar.tsx`, line 43

Every call to `handleSend` includes the full message history with no cap. A long conversation will eventually hit the model's context window limit, causing the API call to fail. It also increases token costs linearly with session length.

Fix: cap history to the last N exchanges before sending:

```typescript
history: messages.slice(-20).map((m) => ({ role: m.role, content: m.content })),
```

---

**`session` cookie is not marked `Secure` in production**
File: `backend/auth.py` / `backend/main.py`, lines 68–74

`response.set_cookie(...)` sets `httponly=True` and `samesite="lax"` but omits `secure=True`. Over HTTP (e.g., the Docker dev setup) this is intentional, but there is no mechanism to enable `Secure` when deploying over HTTPS, which is stated as a future goal (Vercel). A plain HTTP interception would expose the session token.

Fix: read from an env var:

```python
SECURE_COOKIE = os.environ.get("SECURE_COOKIE", "false").lower() == "true"
# then in the route:
response.set_cookie(..., secure=SECURE_COOKIE)
```

---

**`SECRET_KEY` is hardcoded**
File: `backend/auth.py`, line 3

```python
SECRET_KEY = "dev-secret-key"
```

Session tokens are signed with this key. If the key is not rotated between deployments (there is no mechanism to set it via environment variable), all sessions signed in development are valid in production, and vice versa. This is distinct from the intentionally hardcoded credentials — those are documented MVP decisions. The signing key is a different threat: knowing it lets an attacker forge session tokens for any username.

Fix: read from the environment with a loud failure if unset in production:

```python
SECRET_KEY = os.environ.get("SESSION_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SESSION_SECRET_KEY environment variable is required")
```

---

### Low

**`page.waitForTimeout(800)` in Playwright e2e test**
File: `frontend/tests/kanban.spec.ts`, line 45

`waitForTimeout` is an unconditional sleep. It makes the test slow and brittle: too short on a slow machine (flaky), unnecessary wait on a fast one. It exists to wait for the 500ms debounce to fire and the PUT to complete.

Fix: wait for the network request instead:

```typescript
await page.waitForResponse((resp) => resp.url().includes("/api/board") && resp.request().method() === "PUT");
await page.reload();
```

---

**`/api/ai/test` endpoint is included in the OpenAPI schema**
File: `backend/main.py`, line 100

The test endpoint appears in the generated docs (`/docs`). It is a development artifact and should not be discoverable.

Fix: add `include_in_schema=False` to the decorator.

---

**`initialData` in `kanban.ts` is dead code in production**
File: `frontend/src/lib/kanban.ts`, lines 18–72

`initialData` is used only in `KanbanBoard.test.tsx` (as test seed data). The live app fetches board state from the API. The constant being exported and colocated with the library types is misleading — it implies it is part of the production data path.

Fix: move `initialData` into the test file where it is used, or co-locate it in `src/test/fixtures.ts`.

---

**Drag-and-drop e2e test uses raw mouse coordinates and is inherently fragile**
File: `frontend/tests/kanban.spec.ts`, lines 99–108

The drag test moves the mouse with hardcoded pixel offsets (`columnBox.y + 120`) rather than targeting a DOM element. This is brittle to layout changes and will fail if the column height or card positioning changes.

Fix: use `page.dragAndDrop('[data-testid="card-card-1"]', '[data-testid="column-col-review"]')` if Playwright's built-in drag works with the pointer sensor, or use `dnd-kit`'s recommended testing patterns with keyboard accessibility (which are deterministic).

---

## Positive Observations

- The `_connect()` context manager correctly handles commit/rollback in a single place. All SQL uses parameterized queries — no string interpolation anywhere.
- `moveCard` in `kanban.ts` is a well-structured pure function covering all three cases (same-column reorder, cross-column drop on card, cross-column drop on column). The unit tests cover all three branches.
- The `isFirstSync` ref pattern for skipping the initial debounced save is correct and avoids a redundant PUT on load.
- The test fixture in `test_api.py` properly monkeypatches `database.DB_PATH` before the `TestClient` context manager runs `lifespan`, giving each test a clean isolated database.
- The Dockerfile multi-stage build is clean: `npm ci` with a lockfile in the frontend stage, then a minimal Python runtime image. The `uv` binary is pulled from the official image rather than installed via pip.
- The `DragOverlay` + `KanbanCardPreview` pattern (a separate component without drag listeners) is the correct dnd-kit approach and avoids the common mistake of reusing the sortable card as the overlay.
