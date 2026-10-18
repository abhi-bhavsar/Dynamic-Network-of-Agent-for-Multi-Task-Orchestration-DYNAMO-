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
        memory_slices=result.get("memory_slices", {}),
        spawn_manifest=result.get("spawn_manifest", {}),
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
        memory_slices=dyn_result.get("memory_slices", {}),
        spawn_manifest=dyn_result.get("spawn_manifest", {}),
        feature_vector=dyn_result.get("feature_vector", {}),
        errors=dyn_result.get("errors", []),
    )


@router.get("/agents")
async def get_agent_fleet():
    """Returns the specialist agent registry metadata and domain parameters."""
    from ...memory.slicer import AGENT_RELEVANCE_MAP
    return {
        "agents": [
            {
                "id": "deploy_market",
                "name": "Market Data Agent",
                "role": "market_specialist",
                "domain": "Prices, Trading Volumes, Momentum, Moving Averages, Technicals",
                "keywords": AGENT_RELEVANCE_MAP.get("deploy_market", []),
                "description": "Analyzes market conditions, historical price action, momentum, and technical chart indicators.",
                "color": "#06B6D4"
            },
            {
                "id": "deploy_sentiment",
                "name": "Sentiment Agent",
                "role": "sentiment_specialist",
                "domain": "News Sentiment, Analyst Ratings, Social Buzz, Media Perception",
                "keywords": AGENT_RELEVANCE_MAP.get("deploy_sentiment", []),
                "description": "Performs NLP analysis across financial news, analyst consensus, and social chatter.",
                "color": "#8B5CF6"
            },
            {
                "id": "deploy_fundamental",
                "name": "Fundamental Agent",
                "role": "fundamental_specialist",
                "domain": "Earnings, Balance Sheets, Valuation Ratios, SEC Filings",
                "keywords": AGENT_RELEVANCE_MAP.get("deploy_fundamental", []),
                "description": "Evaluates P/E, EPS, balance sheet health, cash flows, and corporate quarterly filings.",
                "color": "#10B981"
            },
            {
                "id": "deploy_risk",
                "name": "Risk Assessment Agent",
                "role": "risk_specialist",
                "domain": "Volatility, Beta, Downside Risk, VaR, Hedging",
                "keywords": AGENT_RELEVANCE_MAP.get("deploy_risk", []),
                "description": "Quantifies portfolio exposure, market correlation, volatility limits, and risk hedging strategies.",
                "color": "#F59E0B"
            },
            {
                "id": "deploy_macro",
                "name": "Macroeconomic Agent",
                "role": "macro_specialist",
                "domain": "GDP, Inflation, Interest Rates, Central Bank Policy, Currency",
                "keywords": AGENT_RELEVANCE_MAP.get("deploy_macro", []),
                "description": "Assesses monetary policy trends, sovereign yield curves, macroeconomic inflation, and FX shifts.",
                "color": "#EC4899"
            }
        ]
    }


@router.get("/policies")
async def get_policies():
    """Returns the PSE policy space descriptions and trigger criteria."""
    from ...pse.policies import PolicyType, POLICY_DESCRIPTIONS, COMPLEXITY_TO_AGENTS
    return {
        "policies": [
            {
                "type": PolicyType.ON_DEMAND.value,
                "name": "On-Demand Spawning",
                "condition": "N ≥ 0.7, C ≤ 2, U < 0.6",
                "best_for": "Novel, simple, non-urgent queries. Zero idle overhead.",
                "description": POLICY_DESCRIPTIONS[PolicyType.ON_DEMAND]
            },
            {
                "type": PolicyType.POOL_BASED.value,
                "name": "Pool-Based Spawning",
                "condition": "N < 0.4, U ≥ 0.7",
                "best_for": "Urgent, predictable queries requiring near-zero spawn latency.",
                "description": POLICY_DESCRIPTIONS[PolicyType.POOL_BASED]
            },
            {
                "type": PolicyType.PREDICTIVE.value,
                "name": "Predictive Provisioning",
                "condition": "R ≥ 0.6, U < 0.7",
                "best_for": "Recurring session query patterns where history predicts required agents.",
                "description": POLICY_DESCRIPTIONS[PolicyType.PREDICTIVE]
            },
            {
                "type": PolicyType.HIERARCHICAL.value,
                "name": "Hierarchical Decomposition",
                "condition": "C ≥ 4, N ≥ 0.5",
                "best_for": "Deeply complex, multi-domain novel research requiring all specialist agents.",
                "description": POLICY_DESCRIPTIONS[PolicyType.HIERARCHICAL]
            },
            {
                "type": PolicyType.COMPOSITE.value,
                "name": "Composite Hybrid",
                "condition": "Mixed signals / boundary conditions",
                "best_for": "Ambiguous query profiles; hedges by spawning an extra agent.",
                "description": POLICY_DESCRIPTIONS[PolicyType.COMPOSITE]
            }
        ],
        "complexity_mapping": COMPLEXITY_TO_AGENTS
    }


@router.post("/pse/analyze")
async def analyze_pse(request: QueryRequest):
    """
    Simulates the PSE module for a given query without calling LLMs.
    Returns computed feature vector F(Q), selected policy, and target agents in under 5ms.
    """
    from ...pse.feature_extractor import feature_extractor
    from ...pse.policy_selector import policy_selector
    from ...pse.policies import PolicyType

    features = feature_extractor.compute(request.query)
    policy = policy_selector.select_policy(features)
    agents = policy_selector.select_agents(features, policy)
    explanation = policy_selector.get_policy_explanation(features, policy)

    return {
        "query": request.query,
        "feature_vector": features,
        "selected_policy": policy.value,
        "selected_agents": agents,
        "explanation": explanation
    }