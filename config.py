import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    OPENROUTESERVICE_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")
    NEAREST_PARKING_MAX_RESULTS = 3
    NEAREST_PARKING_PROFILE = "driving-car"