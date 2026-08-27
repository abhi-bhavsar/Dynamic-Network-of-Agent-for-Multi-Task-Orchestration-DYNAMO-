from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.core.database import Base
import datetime

# This class represents the exact table in your PostgreSQL database!
class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    # Core identification columns
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Query details
    user_query = Column(String, nullable=False)
    model_used = Column(String, default="gpt-oss")
    
    # Static Metrics (The Control Group)
    static_latency_ms = Column(Float, nullable=True)
    static_tokens = Column(Integer, nullable=True)
    
    # Dynamic Metrics (DYNAMO)
    dynamic_latency_ms = Column(Float, nullable=True)
    dynamic_tokens = Column(Integer, nullable=True)
    
    # Mathematical Improvements (What you show in the IEEE Paper!)
    latency_reduction_percent = Column(Float, nullable=True)
    token_savings_percent = Column(Float, nullable=True)