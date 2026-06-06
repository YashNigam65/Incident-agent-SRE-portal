# config.py
import os
from dotenv import load_dotenv

# Load variables from the .env file into Python's environment
load_dotenv()

# Safely fetch the API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Double-check that the key loaded properly
if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY not found! Please check your .env file.")