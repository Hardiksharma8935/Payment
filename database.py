from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import BigInteger, Float, Integer, Boolean, String
from config import config

# Create async engine and sessionmaker
engine = create_async_engine(config.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) # Telegram User ID
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    balance_inr: Mapped[float] = mapped_column(Float, default=0.0)
    balance_usd: Mapped[float] = mapped_column(Float, default=0.0)
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    total_referrals: Mapped[int] = mapped_column(Integer, default=0)
    referral_earnings_inr: Mapped[float] = mapped_column(Float, default=0.0)

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
  
