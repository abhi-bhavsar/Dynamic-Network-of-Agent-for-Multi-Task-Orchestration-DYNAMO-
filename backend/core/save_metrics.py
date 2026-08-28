from .database import SessionLocal
from .models import BenchmarkRun

def save_benchmark_to_db(
    user_query: str, 
    model_used: str, 
    static_latency: float, 
    static_tokens: int, 
    dynamic_latency: float, 
    dynamic_tokens: int,
    latency_improv: float,
    token_savings: float,
    policy: str,
    agents_count: int
):
    print("💾 Attempting to save metrics to PostgreSQL...")
    db = SessionLocal() 
    
    try:
        latency_saved = latency_improv
        tokens_saved = token_savings
        
        if static_latency and dynamic_latency and static_latency > 0 and not latency_saved:
            latency_saved = ((static_latency - dynamic_latency) / static_latency) * 100
            
        if static_tokens and dynamic_tokens and static_tokens > 0 and not tokens_saved:
            tokens_saved = ((static_tokens - dynamic_tokens) / static_tokens) * 100
            
        # EXACTLY matching your models.py (Removed policy and agents_spawned)
        new_run = BenchmarkRun(
            user_query=user_query,
            model_used=model_used,
            static_latency_ms=static_latency,
            static_tokens=static_tokens,
            dynamic_latency_ms=dynamic_latency,
            dynamic_tokens=dynamic_tokens,
            latency_reduction_percent=latency_saved, 
            token_savings_percent=tokens_saved
        )
        
        db.add(new_run)
        db.commit()
        print("✅ Successfully saved benchmark run to database!")
        
    except Exception as e:
        db.rollback() 
        print(f"❌ Error saving to database: {e}")
    finally:
        db.close()