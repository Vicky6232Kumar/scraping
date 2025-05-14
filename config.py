import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    EVENTS_URL = 'https://www.conferencealerts.in/ai'
    OPPORTUNITIES_URL = 'https://www.iitk.ac.in/dord/scientific-and-research-staff'
