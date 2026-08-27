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
    wall_latency = round((time.time() - wall_start) * 1000, 2)

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
    dyn_latency = round((time.time() - t0) * 1000, 2)
    dyn_tokens = dyn_result.get("total_tokens", 0)
    dyn_agents = len(dyn_result.get("agent_outputs", {}))

    # ── Static baseline run (optional) ────────────────────────
    stat_tokens, stat_latency, stat_agents = None, None, 5

    if request.include_static:
        from ...benchmark.runner import run_static_baseline
        try:
            t1 = time.time()
            stat_result = await run_static_baseline(request.query)
            stat_latency = round((time.time() - t1) * 1000, 2)
            stat_tokens = stat_result.get("total_tokens", 0)
        except Exception:
            pass  # Static baseline failure doesn't break benchmark

    # ── Compute improvement metrics ────────────────────────────
    token_savings_pct = None
    latency_improvement_pct = None

    if stat_tokens and stat_tokens > 0:
        token_savings_pct = round((1 - dyn_tokens / stat_tokens) * 100, 2)
    if stat_latency and stat_latency > 0:
        latency_improvement_pct = round((1 - dyn_latency / stat_latency) * 100, 2)

    # ── Save metrics to PostgreSQL ─────────────────────────────
    try:
        save_benchmark_to_db(
            user_query=request.query,
            model_used=dyn_result.get("model_used", "openai/gpt-oss-20b"),
            static_latency=stat_latency or 0.0,
            static_tokens=stat_tokens or 0,
            dynamic_latency=dyn_latency,
            dynamic_tokens=dyn_tokens,
            latency_improv=latency_improvement_pct or 0.0,
            token_savings=token_savings_pct or 0.0,
            policy=dyn_result.get("selected_policy", "unknown"),
            agents_count=dyn_agents,
        )
    except Exception as db_err:
        print(f"⚠️ Database logging warning: {db_err}")

    return BenchmarkResult(
        query=request.query,
        dynamic_tokens=dyn_tokens,
        static_tokens=stat_tokens,
        dynamic_latency_ms=dyn_latency,
        static_latency_ms=stat_latency,
        token_savings_pct=token_savings_pct,
        latency_improvement_pct=latency_improvement_pct,
        policy_selected=dyn_result.get("selected_policy", "unknown"),
        agents_spawned=dyn_agents,
        static_agents=stat_agents,
    )