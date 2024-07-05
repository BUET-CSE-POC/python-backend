from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.auth import UserAuth, TokenData
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.core.config import settings
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps
from app.core.supabase import supabase 

router = APIRouter()

@router.get("/")
async def protected_route(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
        return {"message": f"Hello, user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")