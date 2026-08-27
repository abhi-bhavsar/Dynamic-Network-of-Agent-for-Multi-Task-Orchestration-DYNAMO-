from enum import Enum


class PolicyType(str, Enum):
    """
    The four spawning policies in DYNAMO's policy space Π.
    The PSE module selects one (or composes multiple) at runtime.
    """
    ON_DEMAND    = "on_demand"      # Agents created fresh per query. No pre-warming.
    POOL_BASED   = "pool_based"     # Pre-warmed agents served from a ready pool.
    PREDICTIVE   = "predictive"     # Pre-provision likely agents from session history.
    HIERARCHICAL = "hierarchical"   # Spawn sub-orchestrators for complex nested tasks.
    COMPOSITE    = "composite"      # Mixed policy — when query features are ambiguous.


POLICY_DESCRIPTIONS = {
    PolicyType.ON_DEMAND:    "Zero idle overhead. Best for novel, low-frequency, diverse queries.",
    PolicyType.POOL_BASED:   "Near-zero spawn latency. Best for time-critical, predictable queries.",
    PolicyType.PREDICTIVE:   "Proactive provisioning. Best for recurring session query patterns.",
    PolicyType.HIERARCHICAL: "Recursive decomposition. Best for C≥4, deeply complex novel queries.",
    PolicyType.COMPOSITE:    "Weighted hybrid of multiple policies for ambiguous query profiles.",
}

# Complexity score → agent count mapping
COMPLEXITY_TO_AGENTS = {
    1: ["deploy_market"],
    2: ["deploy_market", "deploy_sentiment"],
    3: ["deploy_market", "deploy_sentiment", "deploy_fundamental"],
    4: ["deploy_market", "deploy_sentiment", "deploy_fundamental", "deploy_risk"],
    5: ["deploy_market", "deploy_sentiment", "deploy_fundamental", "deploy_risk", "deploy_macro"],
}
