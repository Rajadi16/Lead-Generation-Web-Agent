"""
Database models and operations for Lead Generation Web Agent
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Lead(Base):
    """Lead model representing a potential customer"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    email = Column(String, index=True)
    linkedin_url = Column(String)
    phone = Column(String)
    
    # Company Information
    company = Column(String, nullable=False, index=True)
    company_size = Column(String)
    funding_stage = Column(String)
    funding_amount = Column(String)
    funding_date = Column(String)
    
    # Location Information
    person_location = Column(String)
    company_hq = Column(String)
    is_remote = Column(String)
    
    # Scientific Profile
    publications = Column(Text)  # JSON string of publications
    recent_publication_count = Column(Integer, default=0)
    conference_participation = Column(Text)  # JSON string
    
    # Technology Signals
    tech_keywords_found = Column(Text)  # JSON string
    
    # Scoring
    role_fit_score = Column(Float, default=0.0)
    company_intent_score = Column(Float, default=0.0)
    technographic_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    scientific_intent_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0, index=True)
    
    # Metadata
    data_source = Column(String)  # PubMed, LinkedIn, Conference, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notes
    notes = Column(Text)


def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LeadRepository:
    """Repository for lead operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_lead(self, lead_data: dict) -> Lead:
        """Create a new lead"""
        lead = Lead(**lead_data)
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Get a lead by ID"""
        return self.db.query(Lead).filter(Lead.id == lead_id).first()
    
    def get_all_leads(self) -> List[Lead]:
        """Get all leads"""
        return self.db.query(Lead).order_by(Lead.total_score.desc()).all()
    
    def search_leads(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        company: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        location: Optional[str] = None,
    ) -> List[Lead]:
        """Search leads with filters"""
        query = self.db.query(Lead)
        
        if name:
            query = query.filter(Lead.name.ilike(f"%{name}%"))
        if title:
            query = query.filter(Lead.title.ilike(f"%{title}%"))
        if company:
            query = query.filter(Lead.company.ilike(f"%{company}%"))
        if min_score is not None:
            query = query.filter(Lead.total_score >= min_score)
        if max_score is not None:
            query = query.filter(Lead.total_score <= max_score)
        if location:
            query = query.filter(
                (Lead.person_location.ilike(f"%{location}%")) |
                (Lead.company_hq.ilike(f"%{location}%"))
            )
        
        return query.order_by(Lead.total_score.desc()).all()
    
    def update_lead(self, lead_id: int, lead_data: dict) -> Optional[Lead]:
        """Update a lead"""
        lead = self.get_lead(lead_id)
        if lead:
            for key, value in lead_data.items():
                setattr(lead, key, value)
            lead.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(lead)
        return lead
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead"""
        lead = self.get_lead(lead_id)
        if lead:
            self.db.delete(lead)
            self.db.commit()
            return True
        return False
    
    def get_leads_by_score_range(self, min_score: float, max_score: float) -> List[Lead]:
        """Get leads within a score range"""
        return self.db.query(Lead).filter(
            Lead.total_score >= min_score,
            Lead.total_score <= max_score
        ).order_by(Lead.total_score.desc()).all()


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
