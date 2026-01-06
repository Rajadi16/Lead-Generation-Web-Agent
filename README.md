# Lead Generation Web Agent

An intelligent web agent that identifies, enriches, and ranks potential leads for companies selling 3D in-vitro models to pharmaceutical and biotech researchers.

## How It Works

### Stage 1: Identification (Lead Discovery)

The system automatically discovers potential leads by:

**✅ Currently Implemented:**
- **PubMed/NCBI Scraping**: Searches for researchers who have published papers in relevant areas:
  - Toxicology and drug safety
  - 3D cell culture and organoids
  - Liver disease and hepatotoxicity
  - In vitro testing methods
  - DILI (Drug-Induced Liver Injury)
- **Author Extraction**: Automatically extracts researcher names, affiliations, companies, and locations from publications
- **Publication Tracking**: Records recent publications (last 24 months) for scientific intent scoring
- **Result**: Successfully identified **1,217 qualified leads** from PubMed

**❌ NOT Implemented (Why):**

> [!IMPORTANT]
> **LinkedIn Sales Navigator Integration**: Not implemented due to API costs and compliance requirements.
> - **Why**: LinkedIn's official API (via Proxycurl) costs $0.01-0.02 per profile (~$10-20 for 1,000 leads)
> - **Why**: Requires paid API subscription and careful compliance with LinkedIn's Terms of Service
> - **Alternative**: Current implementation uses PubMed which provides high-quality scientific leads without API costs
> - **Future**: Can be added with Proxycurl API integration if budget allows

> [!IMPORTANT]
> **Conference Attendee Lists (SOT, AACR, ISSX)**: Not implemented due to data access limitations.
> - **Why**: Conference websites typically don't provide public APIs for attendee data
> - **Why**: Attendee lists are often behind registration walls or require manual collection
> - **Why**: Web scraping conference sites may violate terms of service
> - **Future**: Can be implemented with manual data collection or if conferences provide API access

> [!IMPORTANT]
> **Job Title Filtering**: Partially implemented.
> - **Current**: Assigns default "Research Scientist" title to all PubMed authors
> - **Why**: PubMed doesn't include job titles in publication metadata
> - **Why**: Would require LinkedIn enrichment to get actual titles like "Director of Toxicology"
- **Future**: Can be enhanced with LinkedIn API or manual title validation

**🔄 Planned Enhancements:**
- LinkedIn Sales Navigator integration for targeted profile searches (Director of Toxicology, Head of Preclinical Safety, etc.)
- Conference attendee list scraping (SOT - Society of Toxicology, AACR, ISSX)
- Job title filtering and validation from LinkedIn profiles

### Stage 2: Enrichment

**✅ Currently Implemented:**
- Email address generation using common patterns (firstname.lastname@company.com)
- Company and location extraction from affiliations

**🔄 Planned:**
- Email verification via Hunter.io or similar APIs
- LinkedIn profile enrichment via Proxycurl
- Funding data from Crunchbase/PitchBook

### Stage 3: Scoring & Ranking

**✅ Fully Implemented:**
- 5-factor propensity scoring algorithm (0-100 scale)
- Automatic categorization: Hot (80-100), Warm (50-79), Cold (0-49)
- Scoring based on: Role fit, Company intent, Technographic signals, Location, Scientific activity

## Features

- 🔍 **Automated Lead Discovery**: Scrapes PubMed for researchers publishing in relevant areas
- 📊 **Intelligent Scoring**: Multi-factor propensity scoring algorithm (0-100 scale)
- 🎯 **Lead Categorization**: Hot (80-100), Warm (50-79), Cold (0-49) leads
- 📧 **Email Generation**: Automatic email address generation from names and companies
- 🌍 **Location Intelligence**: Geographic hub scoring for key biotech locations
- 📈 **Interactive Dashboard**: Streamlit-based web interface with search, filter, and export
- 💾 **Data Export**: Export leads to CSV or Excel format

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional):
```bash
# .env
PUBMED_EMAIL=your-email@example.com
```

4. Initialize the database:
```bash
python database.py
```

## Usage

### Running the Dashboard

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Using the Dashboard

1. **Scrape PubMed**: Click the "🔍 Scrape PubMed" button in the sidebar to collect leads
2. **Filter Leads**: Use the sidebar filters to narrow down leads by score, name, company, or location
3. **View Details**: Switch to the "Lead Details" tab to see comprehensive information about each lead
4. **Export Data**: Download leads as CSV or Excel from the "All Leads" tab

### Testing Components

Test the PubMed scraper:
```bash
python scrapers/pubmed_scraper.py
```

Test the scoring algorithm:
```bash
python scoring/propensity_scorer.py
```

Test the email finder:
```bash
python enrichment/email_finder.py
```

## Scoring Methodology

The propensity scoring algorithm evaluates leads across 5 dimensions:

### 1. Role Fit (Max 30 points)
- Job title keywords: toxicology, safety, hepatic, liver, 3D, in vitro
- Seniority level: Director, Head, VP, Principal, Scientist

### 2. Company Intent (Max 20 points)
- Funding stage and recency (Series A/B in last 12 months = highest)
- NIH grant presence
- Company maturity indicators

### 3. Technographic Signals (Max 25 points)
- Company website mentions: 3D models, NAMs, liver disease
- Job postings for in vitro roles
- Technology stack indicators

### 4. Location Hub (Max 10 points)
- Boston/Cambridge, MA: 10 points
- San Francisco Bay Area: 10 points
- Basel, Switzerland: 10 points
- Cambridge/Oxford, UK: 10 points
- San Diego, CA: 8 points
- Other locations: 3 points

### 5. Scientific Intent (Max 40 points)
- Publications in last 12 months: 40 points
- Publications 12-24 months ago: 25 points
- 3D cell culture papers: 30 points
- Conference presentations: 35 points

**Total possible**: 125 points (normalized to 0-100 scale)

## Project Structure

```
intern/
├── app.py                          # Main Streamlit dashboard
├── config.py                       # Configuration and settings
├── database.py                     # Database models and operations
├── requirements.txt                # Python dependencies
├── scrapers/
│   ├── __init__.py
│   └── pubmed_scraper.py          # PubMed/NCBI scraper
├── enrichment/
│   ├── __init__.py
│   └── email_finder.py            # Email generation
├── scoring/
│   ├── __init__.py
│   └── propensity_scorer.py       # Scoring algorithm
├── templates/
│   └── linkedin_import_template.csv
└── README.md
```

## Data Sources & Target Criteria

### Currently Implemented (MVP)

**PubMed/NCBI Database:**
- ✅ Searches for researchers publishing in:
  - Toxicology, hepatotoxicity, liver disease
  - 3D cell culture, organoids, spheroids
  - In vitro testing, NAMs (New Approach Methodologies)
  - Drug-induced liver injury (DILI)
- ✅ Extracts: Author names, affiliations, companies, locations
- ✅ Tracks publication recency and relevance
- ✅ Limitation: Does not filter by job title (assigns default "Research Scientist")

**Email Generation:**
- ✅ Pattern-based generation (firstname.lastname@company.com)
- ❌ Not verified (recommendation: verify before outreach)

### Future Enhancements

**LinkedIn Sales Navigator Integration:**
- 🔄 Target specific job titles:
  - Director of Toxicology
  - Head of Preclinical Safety
  - VP of Research
  - Principal Scientist - In Vitro
- 🔄 Company size and industry filters
- 🔄 Via Proxycurl API (paid service, compliant with LinkedIn ToS)

**Conference Attendee Lists:**
- 🔄 SOT (Society of Toxicology) speaker/attendee lists
- 🔄 AACR (American Association for Cancer Research)
- 🔄 ISSX (International Society for the Study of Xenobiotics)

**Additional Data Sources:**
- 🔄 **Funding Databases**: Crunchbase, PitchBook for company intent signals
- 🔄 **NIH RePORTER**: Grant recipient data for academic researchers
- 🔄 **Email Verification**: Hunter.io, Clearbit, RocketReach APIs

## Configuration

Edit `config.py` to customize:

- Target job titles
- PubMed search keywords
- Geographic location scores
- Scoring weights and thresholds
- API keys for paid services

## API Integration Guide

### Adding Hunter.io for Email Finding

1. Get API key from [Hunter.io](https://hunter.io)
2. Add to `.env`: `HUNTER_API_KEY=your_key`
3. Update `enrichment/email_finder.py` to use the API

### Adding Proxycurl for LinkedIn Data

1. Get API key from [Proxycurl](https://nubela.co/proxycurl)
2. Add to `.env`: `PROXYCURL_API_KEY=your_key`
3. Create `scrapers/linkedin_scraper.py` using the API

## MVP Deliverable

This implementation provides:

✅ **50-100 sample leads** from PubMed  
✅ **Working scoring algorithm** with 5-factor analysis  
✅ **Searchable dashboard** with filters and sorting  
✅ **Export functionality** (CSV and Excel)  
✅ **Documentation** of methodology and usage  

## Compliance & Best Practices

- **PubMed**: Uses official Entrez API with rate limiting
- **Email Generation**: Pattern-based, recommend verification before outreach
- **GDPR**: Consider compliance when targeting EU leads
- **LinkedIn**: Use official APIs (Proxycurl) to comply with ToS

## Troubleshooting

### Database Issues
```bash
# Reset database
rm leads.db
python database.py
```

### PubMed Connection Issues
- Ensure you have internet connection
- Check `PUBMED_EMAIL` is set in config or `.env`
- NCBI may rate-limit requests - the scraper includes delays

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Future Roadmap

1. **Enhanced Data Collection**
   - Conference website scrapers
   - Funding database integration
   - LinkedIn automation via Proxycurl

2. **Advanced Enrichment**
   - Email verification APIs
   - Company intelligence APIs
   - Social media profile linking

3. **Improved Scoring**
   - Machine learning-based scoring
   - Custom scoring weights per campaign
   - A/B testing of scoring models

4. **CRM Integration**
   - Salesforce connector
   - HubSpot integration
   - Email campaign automation

## License

This project is provided as-is for educational and commercial use.

## Contact

For questions or support, contact: akash@euprime.org

---

**Built with**: Python, Streamlit, Biopython, SQLAlchemy, Pandas
