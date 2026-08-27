from typing import Dict, Any
from .base_agent import BaseAgent, AgentOutput


class FundamentalAgent(BaseAgent):
    name = "deploy_fundamental"
    description = (
        "You specialize in fundamental financial analysis: revenue, net income, "
        "EPS, P/E ratio, P/B ratio, debt-to-equity, free cash flow, ROE, ROA, "
        "balance sheet health, SEC filings, and earnings growth trends."
    )
    domain_keywords = ["earnings", "revenue", "eps", "ratio", "balance", "cash", "fundamental"]

    async def execute(self, task: str, memory_slice: Dict[str, Any]) -> AgentOutput:
        findings, tokens = await self._call_llm(task, memory_slice)
        return AgentOutput(
            agent_name=self.name,
            findings=findings,
            confidence=self._parse_confidence(findings),
            tokens_used=tokens,
        )
