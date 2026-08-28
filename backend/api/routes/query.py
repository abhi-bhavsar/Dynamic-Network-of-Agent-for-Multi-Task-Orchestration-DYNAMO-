import time
import asyncio
from fastapi import APIRouter, HTTPException

from ..schemas.request import QueryRequest, BenchmarkRequest
from ..schemas.response import QueryResponse, BenchmarkResult
from ...orchestrator.graph import dynamo_graph, get_empty_state
from ...core.save_metrics import save_benchmark_to_db

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main DYNAMO endpoint.
    Runs the full 5-node LangGraph pipeline:
      feature_extraction → pse → orchestrator → agent_execution → synthesis
    """
    state = get_empty_state(
        query=request.query,
        session_history=request.session_history or [],
    )

    wall_start = time.time()
    try:
        result = await dynamo_graph.ainvoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DYNAMO pipeline error: {str(e)}")
    
    wall_latency = round((time.time() - wall_start) * 1000.0, 2)

    return QueryResponse(
        query=request.query,
        policy=result.get("selected_policy", "unknown"),
        agents_used=list(result.get("agent_outputs", {}).keys()),
        feature_vector=result.get("feature_vector", {}),
        report=result.get("final_report", ""),
        confidence=result.get("confidence_score", 0.0),
        tokens_used=result.get("total_tokens", 0),
        latency_ms=result.get("latency_ms", wall_latency),
        agent_outputs=result.get("agent_outputs", {}),
        errors=result.get("errors", []),
    )


@router.post("/benchmark", response_model=BenchmarkResult)
async def run_benchmark(request: BenchmarkRequest):
    """
    Benchmarking endpoint — runs DYNAMO (dynamic) and optionally
    a static 5-agent baseline, then returns comparative metrics.
    This is the core of the IEEE research paper benchmarking.
    """

    # ── Dynamic run ────────────────────────────────────────────
    dyn_state = get_empty_state(query=request.query)
    t0 = time.time()
    try:
        dyn_result = await dynamo_graph.ainvoke(dyn_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dynamic run failed: {str(e)}")
    
    # Keep raw precision for the database
    dyn_latency_raw = (time.time() - t0) * 1000.0
    dyn_tokens = dyn_result.get("total_tokens", 0)
    dyn_agents = len(dyn_result.get("agent_outputs", {}))
    policy_name = dyn_result.get("selected_policy", "unknown")

    # ── Static baseline run (optional) ────────────────────────
    stat_tokens, stat_latency_raw, stat_agents = None, None, 5

    if request.include_static:
        from ...benchmark.runner import run_static_baseline
        try:
            t1 = time.time()
            stat_result = await run_static_baseline(request.query)
            stat_latency_raw = (time.time() - t1) * 1000.0
            stat_tokens = stat_result.get("total_tokens", 0)
        except Exception:
            pass  # Static baseline failure doesn't break benchmark

    # ── Compute raw improvement metrics (Double Precision) ─────
    raw_token_savings_pct = None
    raw_latency_improvement_pct = None

    if stat_tokens and stat_tokens > 0:
        raw_token_savings_pct = ((stat_tokens - dyn_tokens) / stat_tokens) * 100.0
    if stat_latency_raw and stat_latency_raw > 0:
        raw_latency_improvement_pct = ((stat_latency_raw - dyn_latency_raw) / stat_latency_raw) * 100.0

    # ── Save unrounded metrics to PostgreSQL ───────────────────
    try:
        save_benchmark_to_db(
            user_query=request.query,
            model_used=dyn_result.get("model_used", "openai/gpt-oss-20b"),
            static_latency=stat_latency_raw or 0.0,
            static_tokens=stat_tokens or 0,
            dynamic_latency=dyn_latency_raw,
            dynamic_tokens=dyn_tokens,
            latency_improv=raw_latency_improvement_pct or 0.0,
            token_savings=raw_token_savings_pct or 0.0,
            policy=policy_name,
            agents_count=dyn_agents,
        )
    except Exception as db_err:
        print(f"⚠️ Database logging warning: {db_err}")

    # ── Return formatted UI payload + Synthesized Report ───────
    return BenchmarkResult(
        query=request.query,
        dynamic_tokens=dyn_tokens,
        static_tokens=stat_tokens,
        dynamic_latency_ms=round(dyn_latency_raw, 2),
        static_latency_ms=round(stat_latency_raw, 2) if stat_latency_raw else None,
        token_savings_pct=round(raw_token_savings_pct, 2) if raw_token_savings_pct is not None else None,
        latency_improvement_pct=round(raw_latency_improvement_pct, 2) if raw_latency_improvement_pct is not None else None,
        policy_selected=policy_name,
        policy=policy_name,
        agents_spawned=dyn_agents,
        static_agents=stat_agents,
        report=dyn_result.get("final_report", "No report generated."),
        confidence=dyn_result.get("confidence_score", 0.0),
        agent_outputs=dyn_result.get("agent_outputs", {}),
        feature_vector=dyn_result.get("feature_vector", {}),
        errors=dyn_result.get("errors", []),
    )