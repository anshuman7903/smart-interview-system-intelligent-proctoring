import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file

# Gemini API key (free at aistudio.google.com)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")

# MongoDB connection string (free at mongodb.com/atlas)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "smart_interview"

# Interview settings
MAX_QUESTIONS = 10
TIME_PER_QUESTION = 120  # seconds

# Supported domains
DOMAINS = ["Technical (Python)", "Technical (DSA)", "Finance", "Medical", "HR/Behavioral"]
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]