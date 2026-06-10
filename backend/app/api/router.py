from fastapi import APIRouter
from app.api.v1 import auth, users, chat, conversations, skills, tools, artifacts

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(conversations.router, tags=["conversations"])
api_router.include_router(skills.router, tags=["skills"])
api_router.include_router(tools.router, tags=["tools"])
api_router.include_router(artifacts.router, tags=["artifacts"])
