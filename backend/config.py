import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/care_coordinator')

# Patient API
PATIENT_API_URL = os.getenv('PATIENT_API_URL', 'http://localhost:5001')

# Flask
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000')