WOUND CARE ADVISOR MODULE
This module provides first-aid wound care instruction generation using a LLM (Google Gemini) based on wound classification results.

FEATURES:
Accepts a wound type and confidence score (from your AI/image classifier)

Generates plain-language, first aid steps in JSON using Google Gemini

Wraps outputs in a Pydantic model for validation

Falls back gracefully to generic care if the API fails or quota is exceeded

FILES & STRUCTURE:
wound_care_advisor/
│
├── wound_care.py # core module with class and logic
├── wound_care_test.py # unittest module
init.py # (empty or informative)
└── secrets.env # (

SETUP & USAGE:
PREREQUISITES

Python 3.9+

A Google Gemini API key (get at https://aistudio.google.com/app/apikey)

Install dependencies:
pip install google-generativeai pydantic python-dotenv

YOUR API KEY

Create a file named secrets.env in this folder (add to .gitignore!):
GOOGLE_API_KEY=your_actual_google_generative_api_key_here

EXAMPLE USAGE
from wound_care_advisor.wound_care import WoundCareAdvisor

advisor = WoundCareAdvisor()
result = advisor.generate_care_instructions("Cut", 0.92, "2 inch laceration, mild bleeding")
Or run your main test script:
HOW TO TEST:
From the repository/project root, run:

python -m unittest wound_care_advisor.wound_care_test

This will run all automated unit tests, including parsing, error fallback, and output model validation.

Tips:

Your secrets.env file must be present to run live API tests!

Tests will not send API calls if the Gemini call is mocked (how most unittests are written).

TROUBLESHOOTING:
If you get ModuleNotFoundError for google.generativeai, install with pip install in the same Python env you run code.

If wound_care_advisor can't be found, be sure you're running in the repo/project root and have an init.py in the folder.

For env/key errors, check secrets.env and permissions or update the path in load_dotenv().

NOTES:
ALL advice is for demonstration/development only -- not a substitute for actual medical care.

This code is suitable for hackathons, demos, and as a real-world development starting point.