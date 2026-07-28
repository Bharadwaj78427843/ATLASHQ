from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_in: UserCreate) -> User:
        # Note: password hashing should normally be done before calling repository, 
        # but for this specific isolated test without auth logic, we just mock it or assume it's done.
        # Actually, the user asked for no business logic. We will just use the password as the hash.
        # But UserCreate has 'password', and User has 'password_hash'. 
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            password_hash=user_in.password, # Direct assignment due to no auth logic
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            avatar_url=user_in.avatar_url
        )
        self.session.add(db_user)
        try:
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Email or username already exists")

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        stmt = select(User).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_user(self, user_id: UUID, user_in: UserUpdate) -> User | None:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = update_data.pop("password")
            
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        try:
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Email or username already exists")

    async def delete_user(self, user_id: UUID) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False
        await self.session.delete(db_user)
        await self.session.commit()
        return True
