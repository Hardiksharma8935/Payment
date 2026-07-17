import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import BigInteger, Float, Integer, String, DateTime
from config import config

engine = create_async_engine(config.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    balance_inr: Mapped[float] = mapped_column(Float, default=0.0)
    balance_usd: Mapped[float] = mapped_column(Float, default=0.0)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PurchaseHistory(Base):
    __tablename__ = 'purchase_history'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    product_name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    method: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="Pending")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# database.py ke andar baaki models ke sath ise add karein:
class SecurityLog(Base):
    __tablename__ = 'security_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String, nullable=True)
    reason: Mapped[str] = mapped_column(String)  # e.g., "Flood Attempt", "Failed CAPTCHA"
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)
    if not user:
        user = User(id=user_id)
        session.add(user)
        await session.commit()
    return user
    
