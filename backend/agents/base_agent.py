from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel
import json


class AgentOutput(BaseModel):
    """Structured output returned by every specialist agent."""
    agent_name: str
    findings: str
    confidence: float = 0.80
    tokens_used: int = 0
    error: str = ""


class BaseAgent(ABC):
    """
    Abstract base class for all DYNAMO specialist agents.

    Each agent:
    - Has a unique name and domain description
    - Receives a task string + memory slice (filtered context)
    - Calls the Groq LLM asynchronously
    - Returns a structured AgentOutput
    """

    name: str = "base_agent"
    description: str = "Generic specialist agent."
    domain_keywords: list = []

    def __init__(self):
        from ..core.llm import get_chat_llm
        from ..core.config import settings
        self.llm = get_chat_llm()
        self.settings = settings

    @abstractmethod
    async def execute(self, task: str, memory_slice: Dict[str, Any]) -> AgentOutput:
        """Execute the agent on a given task with a filtered memory slice."""
        pass

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, a specialist AI agent. {self.description}\n\n"
            "Instructions:\n"
            "- Provide factual, structured analysis relevant to the task.\n"
            "- Be concise. Focus on your domain only.\n"
            "- End your response with: Confidence: X.XX (a float between 0.00 and 1.00)\n"
            "- Do not invent data. If unsure, state your uncertainty clearly."
        )

    async def _call_llm(self, task: str, memory_slice: Dict[str, Any]) -> tuple[str, int]:
        """Async LLM call via LangChain ChatGroq."""
        from langchain_core.messages import HumanMessage, SystemMessage

        context_str = json.dumps(memory_slice, indent=2, default=str)
        messages = [
            SystemMessage(content=self._system_prompt()),
            HumanMessage(content=f"Task: {task}\n\nContext:\n{context_str}")
        ]

        try:
            response = await self.llm.ainvoke(messages)
            content = response.content

            # Extract token usage
            tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = response.usage_metadata.get("total_tokens", 0)

            return content, tokens

        except Exception as e:
            return f"[ERROR] Agent {self.name} failed: {str(e)}", 0

    def _parse_confidence(self, text: str) -> float:
        """Extract confidence float from the LLM's response text."""
        import re
        pattern = r"[Cc]onfidence[:\s]+([01]\.\d{1,2})"
        match = re.search(pattern, text)
        if match:
            try:
                return min(1.0, max(0.0, float(match.group(1))))
            except ValueError:
                pass
        return 0.80  # default
