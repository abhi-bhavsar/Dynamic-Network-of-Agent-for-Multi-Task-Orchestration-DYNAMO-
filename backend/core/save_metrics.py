from .database import SessionLocal
from .models import BenchmarkRun

def save_benchmark_to_db(query: str, static_time: float, dynamic_time: float, static_tok: int, dynamic_tok: int):
    """
    Takes the execution metrics from the DYNAMO run and saves them
    as a new row in the PostgreSQL database for the IEEE paper.
    """
    print("💾 Attempting to save metrics to PostgreSQL...")
    
    # 1. Open a connection to the database
    db = SessionLocal() 
    
    try:
        # 2. Calculate percentages safely (handling None if static was skipped)
        latency_saved = None
        tokens_saved = None
        
        if static_time and dynamic_time and static_time > 0:
            latency_saved = ((static_time - dynamic_time) / static_time) * 100
            
        if static_tok and dynamic_tok and static_tok > 0:
            tokens_saved = ((static_tok - dynamic_tok) / static_tok) * 100
        
        # 3. Create a new "Row" of data using the Blueprint from models.py
        new_run = BenchmarkRun(
            user_query=query,
            static_latency_ms=static_time,
            dynamic_latency_ms=dynamic_time,
            static_tokens=static_tok,
            dynamic_tokens=dynamic_tok,
            latency_reduction_percent=latency_saved,
            token_savings_percent=tokens_saved
        )
        
        # 4. Add the row to the database and "commit" (save) it
        db.add(new_run)
        db.commit()
        
        print("✅ Successfully saved benchmark run to database!")
        
    except Exception as e:
        db.rollback() # Cancel the transaction if it failed
        print(f"❌ Error saving to database: {e}")
    finally:
        # 5. Always close the connection when done
        db.close()