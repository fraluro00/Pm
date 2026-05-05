from fastapi import APIRouter, Depends

import database
from auth import get_current_user
from models import BoardData

router = APIRouter(prefix="/api")


@router.get("/board")
def get_board(username: str = Depends(get_current_user)):
    return database.get_board(username)


@router.put("/board")
def put_board(board: BoardData, username: str = Depends(get_current_user)):
    database.save_board(username, board)
    return {"ok": True}
