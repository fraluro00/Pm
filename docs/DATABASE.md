# Database Design

SQLite, local file at `/app/data/kanban.db`. Auto-created on startup.

## Schema

```sql
CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    UNIQUE NOT NULL
);

CREATE TABLE boards (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title   TEXT    NOT NULL DEFAULT 'My Board'
);

CREATE TABLE columns (
    id       TEXT    PRIMARY KEY,  -- e.g. "col-backlog"
    board_id INTEGER NOT NULL REFERENCES boards(id),
    title    TEXT    NOT NULL,
    position INTEGER NOT NULL      -- ordering left to right
);

CREATE TABLE cards (
    id        TEXT    PRIMARY KEY,  -- e.g. "card-abc123"
    column_id TEXT    NOT NULL REFERENCES columns(id),
    title     TEXT    NOT NULL,
    details   TEXT    NOT NULL DEFAULT '',
    position  INTEGER NOT NULL      -- ordering within column
);
```

## Seed data on first run

If no user `user` exists, insert:
- `users`: username = "user"
- `boards`: one board for that user, title = "My Board"
- `columns`: 5 columns (Backlog, Discovery, In Progress, Review, Done) with positions 0–4
- `cards`: the 8 demo cards from the frontend initialData

## Notes

- TEXT IDs on columns and cards match the frontend ID format — no mapping needed.
- `position` integer on both columns and cards drives ordering; no linked-list complexity.
- One board per user for MVP; the schema supports multiple boards for future.
- SQLite file mounted as a Docker volume so data persists across container restarts.
