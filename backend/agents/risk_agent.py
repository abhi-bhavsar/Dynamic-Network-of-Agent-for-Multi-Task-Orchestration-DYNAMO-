from typing import Dict, Any
from .base_agent import BaseAgent, AgentOutput


class RiskAgent(BaseAgent):
    name = "deploy_risk"
    description = (
        "You specialize in financial risk assessment: volatility (beta, VaR), "
        "downside risk, concentration risk, liquidity risk, sector exposure, "
        "geopolitical risk, regulatory risk, and hedging strategies."
    )
    domain_keywords = ["risk", "volatility", "beta", "var", "downside", "hedge", "exposure"]

    async def execute(self, task: str, memory_slice: Dict[str, Any]) -> AgentOutput:
        findings, tokens = await self._call_llm(task, memory_slice)
        return AgentOutput(
            agent_name=self.name,
            findings=findings,
            confidence=self._parse_confidence(findings),
            tokens_used=tokens,
        )
