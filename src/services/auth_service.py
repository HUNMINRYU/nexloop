from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models import User, Team


class AuthService:
    def __init__(
        self, secret: str, expire_hours: int, algorithm: str = "HS256"
    ) -> None:
        self._secret = secret
        self._expire_hours = expire_hours
        self._algorithm = algorithm
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, plain: str) -> str:
        trimmed = plain.encode("utf-8")[:72]
        return self._pwd_context.hash(trimmed)

    def verify_password(self, plain: str, hashed: str) -> bool:
        trimmed = plain.encode("utf-8")[:72]
        return self._pwd_context.verify(trimmed, hashed)

    def _create_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user.email,
            "uid": user.id,
            "role": getattr(user, "role", "editor"),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=self._expire_hours)).timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc

    async def signup(
        self,
        session: AsyncSession,
        name: str,
        email: str,
        password: str,
        team_name: str | None = None,
        job_title: str | None = None,
        phone_number: str | None = None,
    ) -> dict[str, Any]:
        normalized_email = email.strip().lower()
        if not normalized_email or "@" not in normalized_email:
            raise HTTPException(status_code=400, detail="Invalid email")

        exists = await session.scalar(
            select(User).where(User.email == normalized_email)
        )
        if exists:
            raise HTTPException(status_code=409, detail="User already exists")

        # Team 처리
        team_id = None
        if team_name:
            team = await session.scalar(select(Team).where(Team.name == team_name))
            if not team:
                team = Team(name=team_name)
                session.add(team)
                await session.flush()  # team_id 생성을 위해 flush
            team_id = team.id

        user = User(
            name=name,
            email=normalized_email,
            password=self.hash_password(password),
            team_id=team_id,
            job_title=job_title,
            phone_number=phone_number,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {"token": self._create_token(user)}

    async def login(
        self, session: AsyncSession, email: str, password: str
    ) -> dict[str, Any]:
        normalized_email = email.strip().lower()
        user = await session.scalar(select(User).where(User.email == normalized_email))
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"token": self._create_token(user)}

    async def get_current_user(self, session: AsyncSession, token: str) -> User:
        payload = self.verify_token(token)
        user_id = payload.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
