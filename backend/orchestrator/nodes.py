"""
LangGraph Node Functions for DYNAMO Pipeline.

Node execution order:
  feature_extraction → pse → orchestrator → agent_execution → synthesis

Each node receives the full DynamoState and returns a partial dict
that LangGraph merges back into the state.
"""

import asyncio
import time
from typing import Dict, Any

from ..orchestrator.state import DynamoState
from ..orchestrator.spawn_manifest import SpawnManifest, AVAILABLE_AGENTS
from ..pse.feature_extractor import feature_extractor
from ..pse.policy_selector import policy_selector
from ..memory.slicer import memory_slicer
from ..synthesis.synthesizer import SynthesisAgent
from ..core.config import settings

# ── Agent Registry ────────────────────────────────────────────────────────────
# Maps spawn manifest keys → Agent classes (lazy import to avoid circular deps)
def _get_agent_registry() -> Dict[str, Any]:
    from ..agents.market_agent import MarketDataAgent
    from ..agents.sentiment_agent import SentimentAgent
    from ..agents.fundamental_agent import FundamentalAgent
    from ..agents.risk_agent import RiskAgent
    from ..agents.macro_agent import MacroAgent
    return {
        "deploy_market":      MarketDataAgent,
        "deploy_sentiment":   SentimentAgent,
        "deploy_fundamental": FundamentalAgent,
        "deploy_risk":        RiskAgent,
        "deploy_macro":       MacroAgent,
    }


# ── Node 1: Feature Extraction ────────────────────────────────────────────────
def feature_extraction_node(state: DynamoState) -> Dict:
    """
    Computes F(Q) = (N, U, C, R) — no LLM call needed, fast keyword analysis.
    """
    query = state["query"]
    features = feature_extractor.compute(query)
    feature_extractor.add_to_history(query)
    return {"feature_vector": features}


# ── Node 2: PSE (Policy Selection) ────────────────────────────────────────────
def pse_node(state: DynamoState) -> Dict:
    """
    Applies Φ(F(Q)) → selects optimal spawning policy from policy space Π.
    """
    features = state["feature_vector"]
    policy = policy_selector.select_policy(features)
    return {"selected_policy": policy.value}


# ── Node 3: Orchestrator (Spawn Manifest) ─────────────────────────────────────
async def orchestrator_node(state: DynamoState) -> Dict:
    """
    Uses Groq + Instructor to generate a validated SpawnManifest.
    Instructor forces deterministic JSON output matching the Pydantic schema.
    Falls back to rule-based manifest if LLM call fails.
    """
    from ..core.llm import get_instructor_client

    features = state["feature_vector"]
    policy = state["selected_policy"]
    query = state["query"]

    # Pre-select agents based on complexity (rule-based fallback)
    pre_selected = policy_selector.select_agents(features, __import__(
        'backend.pse.policies', fromlist=['PolicyType']
    ).PolicyType(policy))

    system_msg = (
        f"You are DYNAMO's Orchestrator. Your job is to generate a precise agent spawn manifest.\n"
        f"Available agents: {AVAILABLE_AGENTS}\n"
        f"Selected policy: {policy}\n"
        f"Feature vector: N={features['N']:.2f}, U={features['U']:.2f}, "
        f"C={int(features['C'])}, R={features['R']:.2f}\n"
        f"Pre-selected agents (override if necessary): {pre_selected}"
    )

    user_msg = (
        f"Query: {query}\n"
        f"Generate the spawn manifest for this query."
    )

    try:
        client = get_instructor_client()

        def _sync_call():
            return client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                response_model=SpawnManifest,
                max_retries=2,
            )

        # Run sync instructor call in thread pool to avoid blocking async event loop
        manifest: SpawnManifest = await asyncio.to_thread(_sync_call)

        # Always enforce pre-selected agents (LLM might hallucinate agent names)
        manifest.agents = pre_selected
        manifest.policy = policy

    except Exception as e:
        # Rule-based fallback — system still works without instructor
        manifest = SpawnManifest(
            agents=pre_selected,
            policy=policy,
            complexity=int(features["C"]),
            reasoning=f"Rule-based fallback (instructor error: {str(e)[:60]})",
            memory_keys=[],
        )

    return {"spawn_manifest": manifest.model_dump()}


# ── Node 4: Agent Execution (concurrent via asyncio.gather) ──────────────────
async def agent_execution_node(state: DynamoState) -> Dict:
    """
    Core DYNAMO execution node.
    Spawns only the required agents concurrently, each with a memory slice.
    L_dynamic(Q) = max{ λ(aᵢ) : aᵢ ∈ S(Q) }  [not sequential]
    """
    manifest = state["spawn_manifest"]
    query = state["query"]
    agents_to_deploy = manifest.get("agents", [])
    REGISTRY = _get_agent_registry()

    # Build global context
    global_context = {
        "query": query,
        "policy": manifest.get("policy", ""),
        "complexity": manifest.get("complexity", 1),
        "feature_vector": state.get("feature_vector", {}),
        "session_recent": state.get("session_history", [])[-3:],
        "reasoning": manifest.get("reasoning", ""),
    }

    # Slice memory per agent — M(aᵢ) ⊆ GlobalContext
    memory_slices = {
        agent_key: memory_slicer.slice(global_context, agent_key)
        for agent_key in agents_to_deploy
    }

    # Concurrent agent execution
    async def _run_single_agent(agent_key: str):
        AgentClass = REGISTRY.get(agent_key)
        if not AgentClass:
            return agent_key, {
                "agent_name": agent_key,
                "findings": f"Agent '{agent_key}' not found in registry.",
                "confidence": 0.0,
                "tokens_used": 0,
                "error": "NOT_FOUND",
            }
        agent = AgentClass()
        output = await agent.execute(query, memory_slices[agent_key])
        return agent_key, output.model_dump()

    start_time = time.time()

    # asyncio.gather — all agents run in parallel
    results = await asyncio.gather(
        *[_run_single_agent(k) for k in agents_to_deploy],
        return_exceptions=True,
    )

    latency_ms = (time.time() - start_time) * 1000

    # Collect outputs
    agent_outputs: Dict[str, Any] = {}
    total_tokens = 0
    errors = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
            continue
        key, output = result
        agent_outputs[key] = output
        total_tokens += output.get("tokens_used", 0)

    return {
        "agent_outputs": agent_outputs,
        "memory_slices": memory_slices,
        "total_tokens": state.get("total_tokens", 0) + total_tokens,
        "latency_ms": round(latency_ms, 2),
        "errors": state.get("errors", []) + errors,
    }


# ── Node 5: Synthesis ─────────────────────────────────────────────────────────
async def synthesis_node(state: DynamoState) -> Dict:
    """
    Merges all agent outputs into one structured research report.
    Adds synthesis LLM tokens to the total token count.
    """
    synthesizer = SynthesisAgent()
    result = await synthesizer.synthesize(
        query=state["query"],
        agent_outputs=state.get("agent_outputs", {}),
        policy=state.get("selected_policy", "unknown"),
    )

    synth_tokens = result.get("synthesis_tokens", 0)

    return {
        "final_report": result["report"],
        "confidence_score": result["confidence"],
        "total_tokens": state.get("total_tokens", 0) + synth_tokens,
    }
