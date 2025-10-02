from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ezapp.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")






