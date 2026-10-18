import unittest
from backend.memory.slicer import MemorySlicer, AGENT_RELEVANCE_MAP


class TestMemorySlicer(unittest.TestCase):
    def setUp(self):
        self.slicer = MemorySlicer()

    def test_memory_slicer_preserves_query(self):
        global_context = {
            "query": "Analyze Tesla's debt and price action",
            "ticker": "TSLA",
            "price": "$250.00",
            "debt": "$5B",
            "gdp": "2.5%",
        }
        
        market_slice = self.slicer.slice(global_context, "deploy_market")
        self.assertIn("query", market_slice)
        self.assertEqual(market_slice["query"], global_context["query"])
        self.assertIn("agent_role", market_slice)
        self.assertEqual(market_slice["agent_role"], "market_specialist")

    def test_memory_slicing_relevance(self):
        global_context = {
            "query": "What is the Fed rate policy?",
            "macro": "Fed held interest rates steady",
            "price": "AAPL $180",
        }
        
        macro_slice = self.slicer.slice(global_context, "deploy_macro")
        self.assertIn("macro", macro_slice)
        self.assertNotIn("price", macro_slice)

    def test_slice_compression_ratio(self):
        global_context = {
            "query": "Quick stock check",
            "unrelated_1": "something",
            "unrelated_2": "something else",
            "price": "100",
        }
        ratio = self.slicer.slice_ratio(global_context, "deploy_market")
        self.assertTrue(0.0 < ratio <= 1.0)


if __name__ == "__main__":
    unittest.main()
