import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None
Base = declarative_base()

if DATABASE_URL:
    # Supabase / Render connection URLs often start with postgres://
    # SQLAlchemy 1.4+ / 2.0+ requires postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,  # Automatically reconnect dropped/idle connections (critical for Supabase)
            pool_recycle=300,   # Recycle connections every 5 minutes
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        print(f"⚠️ Warning: Could not create database engine with DATABASE_URL: {e}")
else:
    print("⚠️ DATABASE_URL environment variable is not set. Database persistence will be disabled.")


def get_db():
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()