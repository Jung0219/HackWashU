import os
import json
from typing import List, Optional
import google.generativeai as genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load API key from secrets.env at startup
load_dotenv("secrets.env") 
api_key = os.getenv("GOOGLE_API_KEY")

class WoundCareResponse(BaseModel):
    """
    A Pydantic model defining the validated structure for wound care instructions.
    """
    immediate_steps: List[str]
    do_not: List[str]
    warnings: List[str]
    urgency_level: str
    estimated_safe_wait_time: str
    confidence_note: str
    wound_type: str
    classification_confidence: float
    disclaimer: str
    raw_response: Optional[str] = None

class WoundCareAdvisor:
    """
    Generates temporary wound care advice based on AI wound image classification,
    using Google Gemini models to produce structured first aid JSON instructions.
    """

    WOUND_CONTEXT = {
        "Abrasions": "Superficial skin scraping or rubbing injury",
        "Bruises": "Contusion with bleeding under the skin",
        "Cut": "Laceration or incision through the skin",
        "Ingrown_nails": "Nail growing into the surrounding skin tissue",
        "Stab_wounds": "Penetrating injury from a sharp object",
        "Burns": "Tissue damage caused by heat, chemicals, or radiation",
        "Foot_ulcers": "Open sores on the foot, often due to poor circulation or diabetes",
        "Laseration": "Deep cut or tear in the skin or flesh",
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Configures the Google Gemini API client.

        Args:
            api_key (str): API key for Google Gemini. If None, pulls from environment.
        """
        genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel('gemini-2.5-flash')

    def generate_care_instructions(
        self,
        wound_type: str,
        confidence: float,
        additional_context: Optional[str] = None
    ) -> WoundCareResponse:
        """
        Generates structured wound care instructions using Gemini and parses result.

        Args:
            wound_type (str): Type of wound as classified by the AI model.
            confidence (float): Model confidence score (0 to 1).
            additional_context (str, optional): Extra info for the prompt.

        Returns:
            WoundCareResponse: Validated wound care instruction object.

        Raises:
            ValueError: If wound_type is not among supported types.
        """
        if wound_type not in self.WOUND_CONTEXT:
            raise ValueError(f"Unknown wound type: {wound_type}")

        prompt = self._build_prompt(wound_type, confidence, additional_context)
        response = self._call_gemini(prompt)
        return self._parse_response(response, wound_type, confidence)

    def _build_prompt(
        self,
        wound_type: str,
        confidence: float,
        context: Optional[str]
    ) -> str:
        """
        Constructs an LLM prompt tailored to the wound type and model confidence.

        Args:
            wound_type (str): The wound class.
            confidence (float): Model confidence score.
            context (str, optional): Extra runtime context for the prompt.

        Returns:
            str: Formatted prompt for Gemini.
        """
        wound_description = self.WOUND_CONTEXT[wound_type]
        confidence_pct = f"{confidence * 100:.1f}%"
        confidence_level = (
            "high confidence classification"
            if confidence >= 0.90
            else "lower confidence classification - send warning to user to seek professional medical opinion promptly"
        )

        prompt = f"""You are a medical first aid assistant. A wound image has been analyzed by an AI classifier.

Classification Results:
- Wound Type: {wound_type} ({wound_description})
- Classification Confidence: {confidence_pct} ({confidence_level})
{f'- Additional Context: {context}' if context else ''}

The patient has received hospital recommendations and needs TEMPORARY first aid instructions while traveling to the hospital.

{"Note: The lower confidence score suggests the wound image may be unclear or ambiguous. Provide general care instructions for this wound type, with extra emphasis on seeking professional evaluation and a warning that the classification and advice CAN be mistaken." if confidence < 0.65 else ""}

Provide clear, concise first aid instructions in JSON format with these fields:
1. "immediate_steps": Array of 3-5 immediate actions to take (prioritized)
2. "do_not": Array of 2-3 things to AVOID doing
3. "warnings": Array of 1-2 critical warning signs to watch for
4. "urgency_level": "low", "moderate", "high", or "emergency"
5. "estimated_safe_wait_time": Approximate time before hospital visit becomes urgent
6. "confidence_note": Brief note about the classification confidence (if relevant). If confidence is < 90%, include a warning about potential misclassification and to seek a medical professionals opinion. 

Keep instructions simple, actionable, and appropriate for non-medical personnel.
Focus on temporary care only - emphasize that hospital care is essential.

Return ONLY valid JSON, no additional text."""
        return prompt

    def _call_gemini(self, prompt: str) -> str:
        """
        Calls Gemini to generate a JSON-formatted wound care recommendation.

        Args:
            prompt (str): The prompt built by _build_prompt.

        Returns:
            str: The raw text response from Gemini.

        Note:
            In unittests, this method should be patched/mocked.
        """
        response = self.client.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1600,
                "response_mime_type": "application/json"
            }
        )
        return response.text

    def _parse_response(
        self,
        response: str,
        wound_type: str,
        confidence: float
    ) -> WoundCareResponse:
        """
        Converts Gemini's raw response to a validated WoundCareResponse object.

        Args:
            response (str): The LLM's JSON output.
            wound_type (str): The wound type for context.
            confidence (float): Model's confidence score.

        Returns:
            WoundCareResponse: Structured and validated result model.
        """
        try:
            parsed = json.loads(response)
            parsed['wound_type'] = wound_type
            parsed['classification_confidence'] = round(confidence, 3)
            parsed['disclaimer'] = "This is temporary guidance only. Seek professional medical care immediately."
            return WoundCareResponse(**parsed)
        except (json.JSONDecodeError, ValueError, TypeError):
            # Fallback: provide generic first aid when LLM output is invalid
            fallback = {
                "wound_type": wound_type,
                "classification_confidence": round(confidence, 3),
                "immediate_steps": [
                    "Clean the wound gently", "Apply pressure if bleeding", "Cover with clean bandage"
                ],
                "do_not": [
                    "Don't apply ice directly", "Don't use alcohol on open wounds"
                ],
                "warnings": ["Watch for increased pain, swelling, or fever"],
                "urgency_level": "moderate",
                "estimated_safe_wait_time": "Seek care within 2-4 hours",
                "confidence_note": "Classification confidence was moderate - seek professional assessment",
                "raw_response": response,
                "disclaimer": "This is temporary guidance only. Seek professional medical care immediately."
            }
            return WoundCareResponse(**fallback)

# Example test runner - for demonstration purposes, can be uncommented for quick tests.
"""
if __name__ == "__main__":
    advisor = WoundCareAdvisor(api_key=api_key)
    res = advisor.generate_care_instructions("Cut", 0.92, "Test run for output")
    print(res)
"""
