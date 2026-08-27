from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage


SYNTHESIS_SYSTEM_PROMPT = """You are DYNAMO's Synthesis Agent — the final layer of the pipeline.
Your job is to merge findings from multiple specialist agents into one coherent research report.

Rules:
- Integrate insights across all agents — do not repeat agent names as headers.
- Resolve any contradictions by noting them explicitly.
- Structure your response exactly as follows:

## Executive Summary
[2-3 sentence high-level answer to the original query]

## Key Findings
[Integrated bullet points — synthesized, not just listed]

## Detailed Analysis
[Paragraph-form synthesis across all domains covered]

## Risk & Caveats
[Any uncertainty, data gaps, or contradictions flagged]

## Conclusion
[1-2 sentence recommendation or outlook]

End with: Overall Confidence: X.XX"""


class SynthesisAgent:
    """
    Merges all agent outputs using confidence-weighted synthesis.
    Called as the final node in the LangGraph pipeline.
    """

    def __init__(self):
        from ..core.llm import get_chat_llm
        self.llm = get_chat_llm(temperature=0.2, max_tokens=2048)

    async def synthesize(
        self,
        query: str,
        agent_outputs: Dict[str, Any],
        policy: str,
    ) -> Dict[str, Any]:
        if not agent_outputs:
            return {"report": "No agent outputs available to synthesize.", "confidence": 0.0}

        # Build findings block from all agents
        findings_block = ""
        confidences = []
        total_tokens = 0

        for agent_key, output in agent_outputs.items():
            if isinstance(output, dict):
                findings = output.get("findings", "")
                conf = output.get("confidence", 0.8)
                tokens = output.get("tokens_used", 0)
            else:
            	findings = str(output)
            	conf = 0.8
            	tokens = 0

            if findings and not findings.startswith("[ERROR]"):
                label = agent_key.replace("deploy_", "").replace("_", " ").title()
                findings_block += f"\n[{label} Agent]\n{findings}\n"
                confidences.append(conf)
                total_tokens += tokens

        if not findings_block.strip():
            return {"report": "All agents returned errors. No synthesis possible.", "confidence": 0.0}

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        messages = [
            SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Original Query: {query}\n"
                f"Spawning Policy Used: {policy}\n"
                f"Agents Activated: {len(agent_outputs)}\n\n"
                f"Agent Findings:\n{findings_block}\n\n"
                "Synthesize the above into a structured research report."
            )),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            report = response.content

            # Try to extract overall confidence from synthesis output
            import re
            match = re.search(r"[Oo]verall [Cc]onfidence[:\s]+([01]\.\d{1,2})", report)
            if match:
                avg_confidence = float(match.group(1))

            synth_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                synth_tokens = response.usage_metadata.get("total_tokens", 0)
            total_tokens += synth_tokens

        except Exception as e:
            report = f"Synthesis error: {str(e)}\n\n**Raw Findings:**\n{findings_block}"

        return {
            "report": report,
            "confidence": round(min(1.0, max(0.0, avg_confidence)), 3),
            "synthesis_tokens": total_tokens,
        }
