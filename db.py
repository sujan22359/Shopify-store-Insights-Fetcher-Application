import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ---------- Load Environment Variables ----------
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "shopifydb")

# ---------- Database URL using pymysql ----------
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ---------- SQLAlchemy Setup ----------
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- Table Model ----------
class BrandInsights(Base):
    __tablename__ = "brand_insights"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)  # JSON stored as text

# ---------- Initialize DB ----------
def init_db():
    Base.metadata.create_all(bind=engine)

# ---------- Save or Update Brand Data ----------
def save_brand_data(brand_name: str, data: dict):
    session = SessionLocal()
    try:
        existing = session.query(BrandInsights).filter_by(brand_name=brand_name).first()
        if existing:
            existing.data = json.dumps(data)
        else:
            new_brand = BrandInsights(brand_name=brand_name, data=json.dumps(data))
            session.add(new_brand)
        session.commit()
    finally:
        session.close()

# ---------- Fetch All Brands ----------
def get_all_brands():
    session = SessionLocal()
    try:
        rows = session.query(BrandInsights.id, BrandInsights.brand_name).all()
        return [{"id": r.id, "brand_name": r.brand_name} for r in rows]
    finally:
        session.close()

# ---------- Fetch Brand by ID ----------
def get_brand_by_id(brand_id: int):
    session = SessionLocal()
    try:
        row = session.query(BrandInsights).filter_by(id=brand_id).first()
        if row:
            return json.loads(row.data)
        return None
    finally:
        session.close()
