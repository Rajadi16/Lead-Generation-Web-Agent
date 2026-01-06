"""
3D In-Vitro Lead Qualification Dashboard
Matches the reference design with dark theme and professional layout
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from database import init_db, SessionLocal, Lead, LeadRepository
from scrapers.pubmed_scraper import PubMedScraper
from scoring.propensity_scorer import PropensityScorer
from enrichment.email_finder import EmailFinder
from config import PUBMED_KEYWORDS

# Page configuration
st.set_page_config(
    page_title="3D In-Vitro Lead Qualification Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme custom CSS matching reference design
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    h1 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        color: #a0a0a0;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Table styling */
    .dataframe {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 4px;
    }
    
    .stButton>button:hover {
        background-color: #3d3d3d;
        border-color: #505050;
    }
    
    /* Download button styling */
    .stDownloadButton>button {
        background-color: #4a4a4a;
        color: #ffffff;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'db_initialized' not in st.session_state:
        init_db()
        st.session_state.db_initialized = True


def scrape_pubmed_leads():
    """Scrape leads from PubMed"""
    with st.spinner("Searching PubMed for relevant papers..."):
        scraper = PubMedScraper()
        scorer = PropensityScorer()
        email_finder = EmailFinder()
        
        # Search for papers
        paper_ids = scraper.search_papers(PUBMED_KEYWORDS, months_back=24, max_results=100)
        
        if not paper_ids:
            st.error("No papers found matching the criteria")
            return
        
        st.info(f"Found {len(paper_ids)} papers")
        
        # Fetch paper details
        papers = scraper.fetch_paper_details(paper_ids)
        st.info(f"Fetched details for {len(papers)} papers")
        
        # Extract leads
        leads = scraper.extract_leads_from_papers(papers)
        st.info(f"Extracted {len(leads)} unique leads")
        
        # Enrich and score leads
        db = SessionLocal()
        repo = LeadRepository(db)
        
        added_count = 0
        for lead_data in leads:
            # Generate email
            email = email_finder.generate_email(lead_data['name'], lead_data['company'])
            lead_data['email'] = email
            
            # Convert publications to JSON string
            if 'publications' in lead_data:
                lead_data['publications'] = json.dumps(lead_data['publications'])
            
            # Calculate scores
            scores = scorer.calculate_total_score(lead_data)
            lead_data.update(scores)
            
            # Add to database
            try:
                repo.create_lead(lead_data)
                added_count += 1
            except Exception as e:
                pass
        
        db.close()
        
        st.success(f"Successfully added {added_count} leads to the database!")


def display_leads_dashboard(leads: list):
    """Display leads in dashboard format matching reference design"""
    if not leads:
        st.info("No leads found. Try scraping PubMed or adjusting your filters.")
        return
    
    # Prepare data for table
    data = []
    for idx, lead in enumerate(leads, 1):
        # Determine work mode based on location
        work_mode = "Remote" if lead.person_location and lead.company_hq and lead.person_location != lead.company_hq else "Onsite"
        
        data.append({
            'rank': idx,
            'probability_score': int(lead.total_score),
            'name': lead.name,
            'title': lead.title,
            'company': lead.company,
            'person_location': lead.person_location or 'Unknown',
            'company_hq': lead.company_hq or lead.person_location or 'Unknown',
            'work_mode': work_mode,
            'email': lead.email or 'N/A'
        })
    
    df = pd.DataFrame(data)
    
    # Display table with custom styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "rank": st.column_config.NumberColumn("rank", width="small"),
            "probability_score": st.column_config.NumberColumn("probability_score", width="small"),
            "name": st.column_config.TextColumn("name", width="medium"),
            "title": st.column_config.TextColumn("title", width="large"),
            "company": st.column_config.TextColumn("company", width="medium"),
            "person_location": st.column_config.TextColumn("person_location", width="medium"),
            "company_hq": st.column_config.TextColumn("company_hq", width="medium"),
            "work_mode": st.column_config.TextColumn("work_mode", width="small"),
            "email": st.column_config.TextColumn("email", width="medium")
        }
    )
    
    # Download button
    st.markdown("<br>", unsafe_allow_html=True)
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Qualified Leads (CSV)",
        data=csv,
        file_name=f"qualified_leads_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


def main():
    """Main application"""
    init_session_state()
    
    # Header
    st.markdown("# 3D In-Vitro Lead Qualification Dashboard")
    st.markdown('<p class="subtitle">This dashboard identifies, enriches, and ranks life-science professionals based on their probability of working with 3D in-vitro models.</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        
        # Search filters
        search_text = st.text_input(
            "Search (Name, Title, Company, Location)",
            placeholder="Type to search..."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Minimum probability score slider
        min_score = st.slider(
            "Minimum Probability Score",
            min_value=0,
            max_value=100,
            value=0,
            step=5
        )
        
        st.divider()
        
        # Scrape button
        if st.button("🔍 Scrape PubMed", use_container_width=True):
            scrape_pubmed_leads()
            st.rerun()
    
    # Get filtered leads
    db = SessionLocal()
    repo = LeadRepository(db)
    
    # Apply filters
    if search_text:
        leads = repo.search_leads(
            name=search_text,
            company=search_text,
            location=search_text,
            min_score=min_score
        )
    else:
        leads = repo.search_leads(min_score=min_score)
    
    # Display dashboard
    display_leads_dashboard(leads)
    
    db.close()


if __name__ == "__main__":
    main()
