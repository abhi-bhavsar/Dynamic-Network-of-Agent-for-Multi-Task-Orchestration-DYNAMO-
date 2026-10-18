import unittest
from backend.pse.policies import PolicyType, COMPLEXITY_TO_AGENTS
from backend.pse.policy_selector import PolicySelector


class TestPolicySelector(unittest.TestCase):
    def setUp(self):
        self.selector = PolicySelector()

    def test_policy_selection_hierarchical(self):
        features = {"N": 0.8, "U": 0.4, "C": 5.0, "R": 0.1}
        policy = self.selector.select_policy(features)
        self.assertEqual(policy, PolicyType.HIERARCHICAL)
        agents = self.selector.select_agents(features, policy)
        self.assertEqual(len(agents), 5)

    def test_policy_selection_pool_based(self):
        features = {"N": 0.2, "U": 0.8, "C": 2.0, "R": 0.2}
        policy = self.selector.select_policy(features)
        self.assertEqual(policy, PolicyType.POOL_BASED)

    def test_policy_selection_on_demand(self):
        features = {"N": 0.85, "U": 0.3, "C": 1.0, "R": 0.0}
        policy = self.selector.select_policy(features)
        self.assertEqual(policy, PolicyType.ON_DEMAND)
        agents = self.selector.select_agents(features, policy)
        self.assertIn("deploy_market", agents)

    def test_complexity_agent_mapping(self):
        self.assertEqual(len(COMPLEXITY_TO_AGENTS[1]), 1)
        self.assertEqual(len(COMPLEXITY_TO_AGENTS[5]), 5)


if __name__ == "__main__":
    unittest.main()
