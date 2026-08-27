from typing import Dict, Any
from .base_agent import BaseAgent, AgentOutput


class SentimentAgent(BaseAgent):
    name = "deploy_sentiment"
    description = (
        "You specialize in sentiment and news analysis: financial news sentiment, "
        "social media buzz, analyst ratings, earnings call tone, media coverage, "
        "and public perception of companies or markets."
    )
    domain_keywords = ["news", "sentiment", "rating", "analyst", "opinion", "media", "buzz"]

    async def execute(self, task: str, memory_slice: Dict[str, Any]) -> AgentOutput:
        findings, tokens = await self._call_llm(task, memory_slice)
        return AgentOutput(
            agent_name=self.name,
            findings=findings,
            confidence=self._parse_confidence(findings),
            tokens_used=tokens,
        )
