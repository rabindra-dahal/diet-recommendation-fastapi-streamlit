"""Module provisioning configurations, environmental keys, and cached GenAI API instances."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("System Missing CRITICAL Environment Token: GEMINI_API_KEY!")

# Initialize single official GenAI interface footprint
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
