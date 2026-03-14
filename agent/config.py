"""
config.py
---------
Centralized configuration manager for NeuraX.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv(override=True)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
FRONTEND_DIR = BASE_DIR / "frontend"

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model Settings
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

# Application Settings
WORKLOAD_HARD_CAP = 90.0
# Standard percentage increment per day of effort
WORKLOAD_INCREMENT_PER_DAY = 5.0 
