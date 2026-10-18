import unittest
from backend.pse.feature_extractor import FeatureExtractor


class TestFeatureExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = FeatureExtractor()

    def test_feature_extractor_dimensions(self):
        features = self.extractor.compute("What is the current stock price of AAPL?")
        self.assertIn("N", features)
        self.assertIn("U", features)
        self.assertIn("C", features)
        self.assertIn("R", features)
        
        self.assertTrue(0.0 <= features["N"] <= 1.0)
        self.assertTrue(0.0 <= features["U"] <= 1.0)
        self.assertTrue(1.0 <= features["C"] <= 5.0)
        self.assertTrue(0.0 <= features["R"] <= 1.0)

    def test_urgency_detection(self):
        urgent_features = self.extractor.compute("What is the real-time live price today right now?")
        normal_features = self.extractor.compute("Explain the history of banking.")
        self.assertGreater(urgent_features["U"], normal_features["U"])

    def test_complexity_detection(self):
        simple = self.extractor.compute("TSLA price")
        complex_query = self.extractor.compute(
            "Comprehensive in-depth deep dive analysis comparing Apple vs Microsoft vs Google across portfolio sectors"
        )
        self.assertGreater(complex_query["C"], simple["C"])


if __name__ == "__main__":
    unittest.main()
