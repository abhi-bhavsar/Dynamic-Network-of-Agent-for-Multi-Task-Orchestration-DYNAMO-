from typing import Dict, List
from .policies import PolicyType, COMPLEXITY_TO_AGENTS


class PolicySelector:
    """
    Implements the PSE decision function:
        Φ : F(Q) → π ∈ Π

    Rules are evaluated in priority order:
        1. HIERARCHICAL  — complex novel queries needing recursive decomposition
        2. POOL_BASED    — urgent + recurring queries needing pre-warmed agents
        3. PREDICTIVE    — recurring non-urgent queries where history predicts agents
        4. ON_DEMAND     — novel simple queries; zero overhead preferred
        5. COMPOSITE     — mixed signals; no single rule dominates
    """

    def select_policy(self, features: Dict[str, float]) -> PolicyType:
        N = features["N"]
        U = features["U"]
        C = int(features["C"])
        R = features["R"]

        # Priority 1: High complexity + novel → hierarchical decomposition
        if C >= 4 and N >= 0.5:
            return PolicyType.HIERARCHICAL

        # Priority 2: Known pattern + urgent → pool (pre-warmed, fast)
        if N < 0.4 and U >= 0.7:
            return PolicyType.POOL_BASED

        # Priority 3: Recurring + not urgent → predictive pre-provisioning
        if R >= 0.6 and U < 0.7:
            return PolicyType.PREDICTIVE

        # Priority 4: Novel + simple + not urgent → pure on-demand (zero overhead)
        if N >= 0.7 and C <= 2 and U < 0.6:
            return PolicyType.ON_DEMAND

        # Priority 5: Mixed signals → composite
        return PolicyType.COMPOSITE

    def select_agents(self, features: Dict[str, float], policy: PolicyType) -> List[str]:
        """
        Maps complexity score C to the agent subset S(Q) ⊆ A.
        For COMPOSITE, adds one extra agent to hedge between policies.
        """
        C = int(features["C"])
        agents = COMPLEXITY_TO_AGENTS.get(C, COMPLEXITY_TO_AGENTS[3])

        # HIERARCHICAL: always use full suite
        if policy == PolicyType.HIERARCHICAL:
            agents = COMPLEXITY_TO_AGENTS[5]

        # COMPOSITE: bump up one complexity tier to hedge
        elif policy == PolicyType.COMPOSITE and C < 5:
            agents = COMPLEXITY_TO_AGENTS.get(C + 1, agents)

        return agents

    def get_policy_explanation(self, features: Dict, policy: PolicyType) -> str:
        N, U = features["N"], features["U"]
        C, R = int(features["C"]), features["R"]
        return (
            f"Selected {policy.value.upper()} policy. "
            f"Query profile: Novelty={N:.2f}, Urgency={U:.2f}, "
            f"Complexity={C}/5, Recurrence={R:.2f}."
        )


# Module-level singleton
policy_selector = PolicySelector()
