from typing import Dict, Any, List


# Relevance keyword map — each agent only gets context containing its keywords
AGENT_RELEVANCE_MAP: Dict[str, List[str]] = {
    "deploy_market":      ["query", "ticker", "symbol", "price", "stock", "market",
                           "volume", "trading", "technical", "chart", "momentum"],
    "deploy_sentiment":   ["query", "news", "sentiment", "analyst", "rating", "opinion",
                           "media", "social", "buzz", "perception", "coverage"],
    "deploy_fundamental": ["query", "earnings", "revenue", "eps", "ratio", "balance",
                           "cash", "debt", "equity", "filing", "sec", "income"],
    "deploy_risk":        ["query", "risk", "volatility", "beta", "var", "downside",
                           "hedge", "exposure", "liquidity", "concentration"],
    "deploy_macro":       ["query", "gdp", "inflation", "interest", "fed", "macro",
                           "economic", "currency", "rate", "policy", "trade"],
}


class MemorySlicer:
    """
    Implements Memory Slicing: M(aᵢ) ⊆ GlobalContext

    Each spawned agent receives only the context keys relevant to its domain.
    This prevents context window flooding and reduces cross-agent contamination.

    Math: M(aᵢ) = { k ∈ G : Relevance(k, role(aᵢ)) ≥ θ }
    Here we use keyword-matching as the relevance function (fast, no embedding needed).
    """

    def slice(
        self,
        global_context: Dict[str, Any],
        agent_key: str,
    ) -> Dict[str, Any]:
        """Return a filtered subset of global_context relevant to agent_key."""
        relevant_kws = AGENT_RELEVANCE_MAP.get(agent_key, list(global_context.keys()))

        sliced: Dict[str, Any] = {}

        for ctx_key, ctx_value in global_context.items():
            # Always keep query — every agent needs it
            if ctx_key == "query":
                sliced[ctx_key] = ctx_value
                continue

            # Keep if context key is in the relevance list
            if ctx_key.lower() in relevant_kws:
                sliced[ctx_key] = ctx_value
                continue

            # Keep if context value string contains a relevant keyword
            if isinstance(ctx_value, str):
                if any(kw in ctx_value.lower() for kw in relevant_kws):
                    sliced[ctx_key] = ctx_value

        # Inject agent identity so LLM knows its role
        sliced["agent_role"] = agent_key.replace("deploy_", "") + "_specialist"

        return sliced

    def slice_ratio(self, global_context: Dict, agent_key: str) -> float:
        """
        Returns |M(aᵢ)| / |GlobalContext| — the slice compression ratio.
        Lower = more aggressive slicing = less context flooding.
        Used in benchmarking to measure memory slicing effectiveness.
        """
        if not global_context:
            return 1.0
        sliced = self.slice(global_context, agent_key)
        return len(sliced) / len(global_context)


# Module-level singleton
memory_slicer = MemorySlicer()
