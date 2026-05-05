import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import ai as ai_module
import database
from auth import get_current_user

router = APIRouter(prefix="/api/ai")


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    user_message: str
    history: list[ChatMessage] = []


@router.post("/test", include_in_schema=False)
def ai_test(username: str = Depends(get_current_user)):
    response = ai_module.client.chat.completions.create(
        model=ai_module.MODEL,
        messages=[{"role": "user", "content": "What is 2+2? Reply with just the number."}],
    )
    return {"response": response.choices[0].message.content}


@router.post("/chat")
def ai_chat(req: ChatRequest, username: str = Depends(get_current_user)):
    board = database.get_board(username)
    board_json = json.dumps(board.model_dump(), indent=2)
    system_prompt = ai_module.build_system_prompt(board_json)

    messages = [{"role": "system", "content": system_prompt}]
    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.user_message})

    try:
        response = ai_module.client.chat.completions.create(
            model=ai_module.MODEL,
            messages=messages,
            response_format={"type": "json_object"},
        )
    except Exception:
        raise HTTPException(status_code=502, detail="AI service unavailable")

    raw = response.choices[0].message.content
    try:
        parsed = ai_module.AIResponse.model_validate_json(raw)
    except Exception:
        return ai_module.AIResponse(message="Sorry, I couldn't process that request.")

    if parsed.board_update:
        database.save_board(username, parsed.board_update)

    return parsed
