from typing import TypedDict, List, Dict, Any, Optional


class DynamoState(TypedDict):
    """
    The complete state object that flows through every LangGraph node.
    Each node receives this dict and returns a partial dict to update it.
    """

    # ── Input ──────────────────────────────────────
    query: str                          # Raw user query
    session_history: List[str]          # Past queries in this session

    # ── PSE (Policy-Selective Execution) ───────────
    feature_vector: Dict[str, float]    # {N, U, C, R} scores
    selected_policy: str                # One of PolicyType values

    # ── Orchestration ──────────────────────────────
    spawn_manifest: Dict[str, Any]      # {agents, policy, complexity, reasoning}
    memory_slices: Dict[str, List[str]] # {agent_key: [relevant_context_keys]}

    # ── Agent Execution ────────────────────────────
    agent_outputs: Dict[str, Any]       # {agent_key: AgentOutput dict}

    # ── Synthesis ──────────────────────────────────
    final_report: str                   # Merged markdown report
    confidence_score: float             # Weighted average confidence

    # ── Telemetry ──────────────────────────────────
    total_tokens: int                   # Total LLM tokens consumed
    latency_ms: float                   # Agent execution wall-clock time
    metadata: Dict[str, Any]            # Extra debug info
    errors: List[str]                   # Any non-fatal errors
