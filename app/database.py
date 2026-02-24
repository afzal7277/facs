# from urllib.parse import quote_plus
# from app.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# encoded_password = quote_plus(DB_PASSWORD)

# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@127.0.0.1:3306/{DB_NAME}"

# engine = create_engine(DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()