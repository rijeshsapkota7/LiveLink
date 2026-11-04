from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///databse.db",connect_args={"check_same_thread": False})

Base = declarative_base()

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = LocalSession()

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()