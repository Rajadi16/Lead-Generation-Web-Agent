"""
Configuration management for Lead Generation Web Agent
"""
import os
from typing import Dict, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./leads.db"
    
    # API Keys (optional for MVP)
    PUBMED_EMAIL: str = "your-email@example.com"  # Required for PubMed API
    HUNTER_API_KEY: str = ""  # Optional: Hunter.io for email finding
    CLEARBIT_API_KEY: str = ""  # Optional: Clearbit for company data
    PROXYCURL_API_KEY: str = ""  # Optional: Proxycurl for LinkedIn data
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Target Job Titles
TARGET_JOB_TITLES = [
    "Director of Toxicology",
    "Head of Preclinical Safety",
    "VP of Safety Assessment",
    "Head of Hepatic Research",
    "Director of DMPK",
    "Research Scientist - In Vitro Models",
    "Principal Scientist - Toxicology",
    "Toxicologist",
    "Safety Assessment",
    "Hepatic Research",
]

# PubMed Search Keywords
PUBMED_KEYWORDS = [
    "Drug-Induced Liver Injury",
    "DILI",
    "3D cell culture",
    "hepatic spheroids",
    "organ-on-chip",
    "NAM models",
    "in vitro toxicology",
    "hepatotoxicity",
    "liver organoids",
]

# Geographic Hubs and Scores
LOCATION_SCORES: Dict[str, int] = {
    "Boston": 10,
    "Cambridge, MA": 10,
    "San Francisco": 10,
    "Bay Area": 10,
    "Basel": 10,
    "Cambridge, UK": 10,
    "Oxford": 10,
    "San Diego": 8,
    "Other": 3,
}

# Scoring Weights
SCORING_WEIGHTS = {
    "role_fit": {
        "max_points": 30,
        "keywords": {
            "toxicology": 30,
            "safety": 30,
            "hepatic": 25,
            "liver": 25,
            "3d": 30,
            "in vitro": 30,
            "director": 20,
            "head": 20,
            "vp": 20,
            "scientist": 10,
        }
    },
    "company_intent": {
        "max_points": 20,
        "series_a_b_recent": 20,
        "series_c_plus": 15,
        "nih_grant": 15,
        "bootstrapped": 5,
    },
    "technographic": {
        "max_points": 25,
        "3d_models_mention": 15,
        "nams_mention": 10,
        "liver_disease_focus": 15,
        "job_posting": 20,
    },
    "location_hub": {
        "max_points": 10,
    },
    "scientific_intent": {
        "max_points": 40,
        "publication_recent": 40,  # Last 12 months
        "publication_older": 25,   # 12-24 months
        "3d_culture_paper": 30,
        "conference_presenter": 35,
    }
}

# Total possible score before normalization
TOTAL_POSSIBLE_SCORE = 125

# Conference URLs
CONFERENCE_URLS = {
    "SOT": "https://www.toxicology.org",
    "AACR": "https://www.aacr.org",
    "ISSX": "https://www.issx.org",
}

# Company Technology Keywords
TECH_KEYWORDS = [
    "3D models",
    "3D cell culture",
    "organoids",
    "spheroids",
    "organ-on-chip",
    "NAMs",
    "alternative methods",
    "in vitro",
    "microphysiological systems",
]

# Funding Stages
FUNDING_STAGES = [
    "Seed",
    "Series A",
    "Series B",
    "Series C",
    "Series D+",
    "IPO",
    "Public",
    "Bootstrapped",
    "Unknown",
]


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
