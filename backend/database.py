import sqlite3
from contextlib import contextmanager
from pathlib import Path

from fastapi import HTTPException
from models import BoardData, Card, Column

DB_PATH = Path(__file__).parent / "data" / "kanban.db"

_SEED_COLUMNS = [
    ("col-backlog", "Backlog", 0),
    ("col-discovery", "Discovery", 1),
    ("col-progress", "In Progress", 2),
    ("col-review", "Review", 3),
    ("col-done", "Done", 4),
]

_SEED_CARDS = [
    ("card-1", "col-backlog", "Align roadmap themes", "Draft quarterly themes with impact statements and metrics.", 0),
    ("card-2", "col-backlog", "Gather customer signals", "Review support tags, sales notes, and churn feedback.", 1),
    ("card-3", "col-discovery", "Prototype analytics view", "Sketch initial dashboard layout and key drill-downs.", 0),
    ("card-4", "col-progress", "Refine status language", "Standardize column labels and tone across the board.", 0),
    ("card-5", "col-progress", "Design card layout", "Add hierarchy and spacing for scanning dense lists.", 1),
    ("card-6", "col-review", "QA micro-interactions", "Verify hover, focus, and loading states.", 0),
    ("card-7", "col-done", "Ship marketing page", "Final copy approved and asset pack delivered.", 0),
    ("card-8", "col-done", "Close onboarding sprint", "Document release notes and share internally.", 1),
]


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS boards (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title   TEXT    NOT NULL DEFAULT 'My Board'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS columns (
                id       TEXT    PRIMARY KEY,
                board_id INTEGER NOT NULL REFERENCES boards(id),
                title    TEXT    NOT NULL,
                position INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id        TEXT    PRIMARY KEY,
                column_id TEXT    NOT NULL REFERENCES columns(id),
                title     TEXT    NOT NULL,
                details   TEXT    NOT NULL DEFAULT '',
                position  INTEGER NOT NULL
            )
        """)
        _seed_if_empty(conn)


def _seed_if_empty(conn):
    if conn.execute("SELECT 1 FROM users WHERE username = 'user'").fetchone():
        return
    conn.execute("INSERT INTO users (username) VALUES ('user')")
    user_id = conn.execute("SELECT id FROM users WHERE username = 'user'").fetchone()["id"]
    conn.execute("INSERT INTO boards (user_id) VALUES (?)", (user_id,))
    board_id = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user_id,)).fetchone()["id"]
    for col_id, title, pos in _SEED_COLUMNS:
        conn.execute(
            "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
            (col_id, board_id, title, pos),
        )
    for card_id, col_id, title, details, pos in _SEED_CARDS:
        conn.execute(
            "INSERT INTO cards (id, column_id, title, details, position) VALUES (?, ?, ?, ?, ?)",
            (card_id, col_id, title, details, pos),
        )


def get_board(username: str) -> BoardData:
    with _connect() as conn:
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        board = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user["id"],)).fetchone()
        if board is None:
            raise HTTPException(status_code=404, detail="Board not found")

        cols = conn.execute(
            "SELECT id, title FROM columns WHERE board_id = ? ORDER BY position",
            (board["id"],),
        ).fetchall()

        cards = conn.execute(
            """
            SELECT c.id, c.title, c.details, c.column_id
            FROM cards c
            JOIN columns col ON c.column_id = col.id
            WHERE col.board_id = ?
            ORDER BY c.column_id, c.position
            """,
            (board["id"],),
        ).fetchall()

        cards_by_col: dict[str, list[str]] = {col["id"]: [] for col in cols}
        cards_map: dict[str, Card] = {}
        for card in cards:
            cards_map[card["id"]] = Card(id=card["id"], title=card["title"], details=card["details"])
            if card["column_id"] in cards_by_col:
                cards_by_col[card["column_id"]].append(card["id"])

        columns = [
            Column(id=col["id"], title=col["title"], cardIds=cards_by_col[col["id"]])
            for col in cols
        ]
        return BoardData(columns=columns, cards=cards_map)


def save_board(username: str, board: BoardData):
    with _connect() as conn:
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        board_row = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user["id"],)).fetchone()
        if board_row is None:
            raise HTTPException(status_code=404, detail="Board not found")
        board_id = board_row["id"]

        conn.execute(
            "DELETE FROM cards WHERE column_id IN (SELECT id FROM columns WHERE board_id = ?)",
            (board_id,),
        )
        conn.execute("DELETE FROM columns WHERE board_id = ?", (board_id,))

        for pos, col in enumerate(board.columns):
            conn.execute(
                "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
                (col.id, board_id, col.title, pos),
            )
            for card_pos, card_id in enumerate(col.cardIds):
                card = board.cards.get(card_id)
                if card:
                    conn.execute(
                        "INSERT INTO cards (id, column_id, title, details, position) VALUES (?, ?, ?, ?, ?)",
                        (card.id, col.id, card.title, card.details, card_pos),
                    )
