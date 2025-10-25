import unittest
from unittest.mock import patch
from wound_care_advisor.wound_care import WoundCareAdvisor, WoundCareResponse

class TestWoundCareAdvisor(unittest.TestCase):

    def setUp(self):
        self.advisor = WoundCareAdvisor(api_key="dummy-key")

    @patch.object(WoundCareAdvisor, "_call_gemini")
    def test_success_high_confidence(self, mock_call_gemini):
        mock_call_gemini.return_value = '''
        {
            "immediate_steps": ["Clean gently"],
            "do_not": ["Don't rub"],
            "warnings": ["Fever"],
            "urgency_level": "moderate",
            "estimated_safe_wait_time": "1-2 hours",
            "confidence_note": "High confidence"
        }
        '''
        result = self.advisor.generate_care_instructions("Abrasions", 0.96)
        self.assertIsInstance(result, WoundCareResponse)
        self.assertTrue(result.classification_confidence > 0.9)
        self.assertEqual(result.wound_type, "Abrasions")
        self.assertEqual(result.urgency_level, "moderate")
        self.assertIn("disclaimer", result.dict())

    @patch.object(WoundCareAdvisor, "_call_gemini")
    def test_fallback_on_invalid_json(self, mock_call_gemini):
        mock_call_gemini.return_value = "not a json"
        result = self.advisor.generate_care_instructions("Burns", 0.7)
        self.assertIsInstance(result, WoundCareResponse)
        self.assertEqual(result.wound_type, "Burns")
        self.assertEqual(result.urgency_level, "moderate")
        self.assertEqual(result.raw_response, "not a json")

    @patch.object(WoundCareAdvisor, "_call_gemini")
    def test_missing_fields(self, mock_call_gemini):
        # Missing 'warnings', test Pydantic's error handling and fallback
        mock_call_gemini.return_value = '''
        {
            "immediate_steps": ["Clean gently"],
            "do_not": ["Don't scratch"],
            "urgency_level": "moderate",
            "estimated_safe_wait_time": "1 hour",
            "confidence_note": "High confidence"
        }
        '''
        result = self.advisor.generate_care_instructions("Bruises", 0.8)
        self.assertIsInstance(result, WoundCareResponse)
        self.assertEqual(result.wound_type, "Bruises")
        self.assertTrue(isinstance(result, WoundCareResponse))

    def test_unknown_wound_type(self):
        with self.assertRaises(ValueError):
            self.advisor.generate_care_instructions("Unknown", 0.85)

    def test_serialization(self):
        # Use fallback to check .dict() and .json()
        with patch.object(WoundCareAdvisor, "_call_gemini", return_value="bad"):
            result = self.advisor.generate_care_instructions("Burns", 0.91)
            as_dict = result.dict()
            as_json = result.json()
            self.assertIn("wound_type", as_dict)
            self.assertIn("immediate_steps", as_dict)
            self.assertIn("Burns", as_json)

if __name__ == "__main__":
    unittest.main()
