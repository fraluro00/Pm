import os

from openai import OpenAI
from pydantic import BaseModel

from models import BoardData

MODEL = "openai/gpt-oss-120b"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "no-key"),
)


class AIResponse(BaseModel):
    message: str
    board_update: BoardData | None = None


def build_system_prompt(board_json: str) -> str:
    return f"""You are a Kanban board assistant. The current board state is:

{board_json}

Always respond with a valid JSON object with exactly two keys:
- "message": your reply to the user (string)
- "board_update": null, or the COMPLETE updated board if the user asked to modify it

The board_update must include every column and every card — not just the changed parts.
Only include board_update when the user explicitly requests a board change."""
