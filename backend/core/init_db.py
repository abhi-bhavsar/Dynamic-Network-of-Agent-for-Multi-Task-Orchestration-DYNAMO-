import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import engine, Base
from backend.core.models import BenchmarkRun

print("🚀 Initializing PostgreSQL Database...")

Base.metadata.create_all(bind=engine)

print("✅ Database tables created successfully in dynamo_db!")