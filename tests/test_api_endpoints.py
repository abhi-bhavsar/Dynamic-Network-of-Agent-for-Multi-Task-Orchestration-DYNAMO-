import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("system"), "DYNAMO")

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("groq_connected", data)

    def test_agents_endpoint(self):
        response = self.client.get("/api/v1/agents")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("agents", data)
        self.assertEqual(len(data["agents"]), 5)

    def test_policies_endpoint(self):
        response = self.client.get("/api/v1/policies")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("policies", data)
        self.assertEqual(len(data["policies"]), 5)

    def test_pse_analyze_endpoint(self):
        response = self.client.post(
            "/api/v1/pse/analyze",
            json={"query": "Real-time stock price for NVDA today now"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("feature_vector", data)
        self.assertIn("selected_policy", data)
        self.assertIn("selected_agents", data)


if __name__ == "__main__":
    unittest.main()
