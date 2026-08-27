from typing import Dict, Any
from .base_agent import BaseAgent, AgentOutput


class MacroAgent(BaseAgent):
    name = "deploy_macro"
    description = (
        "You specialize in macroeconomic analysis: GDP growth, inflation, "
        "interest rates, central bank policy (Fed, RBI, ECB), currency strength, "
        "global trade conditions, commodity prices, and sector-macro linkages."
    )
    domain_keywords = ["gdp", "inflation", "interest", "fed", "macro", "economic", "currency"]

    async def execute(self, task: str, memory_slice: Dict[str, Any]) -> AgentOutput:
        findings, tokens = await self._call_llm(task, memory_slice)
        return AgentOutput(
            agent_name=self.name,
            findings=findings,
            confidence=self._parse_confidence(findings),
            tokens_used=tokens,
        )
