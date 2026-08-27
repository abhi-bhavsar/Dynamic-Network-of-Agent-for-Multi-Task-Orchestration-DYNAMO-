"""
DYNAMO LangGraph StateGraph

Pipeline:
  START
    ↓
  feature_extraction   [sync]  — computes F(Q)
    ↓
  pse                  [sync]  — selects policy Φ(F(Q))
    ↓
  orchestrator         [async] — generates SpawnManifest via Groq+Instructor
    ↓
  agent_execution      [async] — runs agents via asyncio.gather()
    ↓
  synthesis            [async] — merges outputs into final report
    ↓
  END
"""

from langgraph.graph import StateGraph, END
from .state import DynamoState
from .nodes import (
    feature_extraction_node,
    pse_node,
    orchestrator_node,
    agent_execution_node,
    synthesis_node,
)


def build_dynamo_graph():
    """Builds and compiles the DYNAMO LangGraph StateGraph."""
    graph = StateGraph(DynamoState)

    # Register nodes
    graph.add_node("feature_extraction", feature_extraction_node)
    graph.add_node("pse",                pse_node)
    graph.add_node("orchestrator",       orchestrator_node)
    graph.add_node("agent_execution",    agent_execution_node)
    graph.add_node("synthesis",          synthesis_node)

    # Wire edges
    graph.set_entry_point("feature_extraction")
    graph.add_edge("feature_extraction", "pse")
    graph.add_edge("pse",                "orchestrator")
    graph.add_edge("orchestrator",       "agent_execution")
    graph.add_edge("agent_execution",    "synthesis")
    graph.add_edge("synthesis",          END)

    return graph.compile()


# Singleton — compiled once at import time, reused across all requests
dynamo_graph = build_dynamo_graph()


def get_empty_state(query: str, session_history: list = None) -> DynamoState:
    """Helper to build a clean initial state for any incoming query."""
    return DynamoState(
        query=query,
        session_history=session_history or [],
        feature_vector={},
        selected_policy="",
        spawn_manifest={},
        memory_slices={},
        agent_outputs={},
        final_report="",
        confidence_score=0.0,
        total_tokens=0,
        latency_ms=0.0,
        metadata={},
        errors=[],
    )
