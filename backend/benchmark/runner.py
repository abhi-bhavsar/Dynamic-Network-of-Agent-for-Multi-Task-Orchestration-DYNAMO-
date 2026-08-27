"""
Static Baseline Runner — always spawns all 5 agents sequentially.
Used as the comparison baseline for the IEEE benchmarking study.
"""
import asyncio
import time
from typing import Dict, Any

from ..agents.market_agent import MarketDataAgent
from ..agents.sentiment_agent import SentimentAgent
from ..agents.fundamental_agent import FundamentalAgent
from ..agents.risk_agent import RiskAgent
from ..agents.macro_agent import MacroAgent
from ..synthesis.synthesizer import SynthesisAgent

ALL_AGENTS = [
    MarketDataAgent,
    SentimentAgent,
    FundamentalAgent,
    RiskAgent,
    MacroAgent,
]


async def run_static_baseline(query: str) -> Dict[str, Any]:
    """
    Runs ALL 5 agents regardless of query complexity (static pipeline).
    Each agent gets the FULL global context — no memory slicing.
    This simulates the worst-case static MAS for benchmarking comparison.
    """
    global_context = {"query": query, "agent_role": "all_agents"}

    async def _run(AgentClass):
        agent = AgentClass()
        output = await agent.execute(query, global_context)  # Full context, no slicing
        return AgentClass.name, output.model_dump()

    # Run all 5 concurrently (static parallel — same cardinality every time)
    results = await asyncio.gather(*[_run(A) for A in ALL_AGENTS], return_exceptions=True)

    agent_outputs = {}
    total_tokens = 0

    for r in results:
        if isinstance(r, Exception):
            continue
        key, output = r
        agent_outputs[key] = output
        total_tokens += output.get("tokens_used", 0)

    # Synthesize static outputs
    synthesizer = SynthesisAgent()
    synthesis = await synthesizer.synthesize(query, agent_outputs, policy="static_baseline")
    total_tokens += synthesis.get("synthesis_tokens", 0)

    return {
        "agent_outputs": agent_outputs,
        "total_tokens": total_tokens,
        "agents_used": list(agent_outputs.keys()),
        "report": synthesis.get("report", ""),
        "policy": "static_baseline",
    }
