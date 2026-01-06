"""
Lead Generation Web Agent - Main Streamlit Dashboard
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
    page_title="Lead Generation Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    .lead-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .hot-lead {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .warm-lead {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .cold-lead {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'db_initialized' not in st.session_state:
        init_db()
        st.session_state.db_initialized = True
    
    if 'leads_loaded' not in st.session_state:
        st.session_state.leads_loaded = False


def get_score_emoji(score: float) -> str:
    """Get emoji for score"""
    if score >= 80:
        return "🟢"
    elif score >= 50:
        return "🟡"
    else:
        return "⚪"


def get_score_category(score: float) -> str:
    """Get category for score"""
    if score >= 80:
        return "Hot Lead"
    elif score >= 50:
        return "Warm Lead"
    else:
        return "Cold Lead"


def get_score_class(score: float) -> str:
    """Get CSS class for score"""
    if score >= 80:
        return "hot-lead"
    elif score >= 50:
        return "warm-lead"
    else:
        return "cold-lead"


def scrape_pubmed_leads(query: str = None):
    """Scrape leads from PubMed"""
    search_terms = [query] if query else PUBMED_KEYWORDS
    with st.spinner(f"Searching PubMed for papers related to: {', '.join(search_terms)}..."):
        scraper = PubMedScraper()
        scorer = PropensityScorer()
        email_finder = EmailFinder()
        
        # Search for papers
        paper_ids = scraper.search_papers(search_terms, months_back=24, max_results=100)
        
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
            
            # Generate LinkedIn URL (Search Link)
            linkedin_url = email_finder.generate_linkedin_url(lead_data['name'], lead_data['company'])
            lead_data['linkedin_url'] = linkedin_url
            
            # Generate conference suggestions
            publications = lead_data.get('publications', [])
            conferences = email_finder.suggest_conferences(lead_data.get('title', ''), publications)
            lead_data['conference_participation'] = conferences
            
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
                st.warning(f"Could not add lead {lead_data['name']}: {e}")
        
        db.close()
        
        st.success(f"Successfully added {added_count} leads to the database!")
        st.session_state.leads_loaded = True


def display_leads_table(leads: list):
    """Display leads in a table format"""
    if not leads:
        st.info("No leads found. Try scraping PubMed or adjusting your filters.")
        return
    
    # Convert to DataFrame
    data = []
    
    # Sort leads by score (just in case they aren't already) but they typically are from the DB query
    # Then take only top 500
    sorted_leads = sorted(leads, key=lambda x: x.total_score, reverse=True)[:500]
    
    for lead in sorted_leads:
        # Parse publications
        pub_count = 0
        if lead.publications:
            try:
                pubs = json.loads(lead.publications)
                pub_count = len(pubs)
            except:
                pass
        
        # Construct Platform URL (e.g., PubMed search)
        platform_url = "https://pubmed.ncbi.nlm.nih.gov/"
        if lead.data_source == 'PubMed':
             platform_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={lead.name.replace(' ', '+')}"
        
        # Format conferences with link if available
        conferences = lead.conference_participation or 'N/A'
        conference_link = conferences
        if conferences != 'N/A':
             # Create a broad search link for the person and these conferences
             import urllib.parse
             query = f"{lead.name} {lead.company} {conferences} conference attendance"
             encoded_query = urllib.parse.quote(query)
             conference_link = f"https://www.google.com/search?q={encoded_query}"

        # Format link for action (research)
        research_link = f"https://www.google.com/search?q={lead.name} {lead.company} {lead.title} contact"
        
        data.append({
            'Rank': len(data) + 1,
            'Probability': f"{lead.total_score:.1f}",  # Removed emoji for cleaner look
            'Name': lead.name,
            'Title': lead.title,
            'Company': lead.company,
            'Location': lead.person_location or 'Unknown',
            'HQ': lead.company_hq or 'Unknown',  # Added HQ column
            'Email': lead.email or 'N/A',
            'LinkedIn': lead.linkedin_url or 'N/A',
            'Action': research_link,  # Use search link as action for now
            'ID': lead.id
        })
    
    df = pd.DataFrame(data)
    
    # Display table with requested columns
    st.dataframe(
        df.drop('ID', axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="%d"),
            "Probability": st.column_config.ProgressColumn(
                "Probability",
                help="Propensity Score (0-100)",
                format="%.1f",
                min_value=0,
                max_value=100,
            ),
            "LinkedIn": st.column_config.LinkColumn("LinkedIn"),
            "Action": st.column_config.LinkColumn("Action"),
            "Email": st.column_config.LinkColumn("Email")
        }
    )
    
    # Export button with custom styling
    # Create export DF without internal columns
    export_df = df.drop('ID', axis=1)
    csv = export_df.to_csv(index=False).encode('utf-8-sig')
    
    # Custom styled download button
    st.markdown("""
    <style>
    .stDownloadButton > button {
        width: 100%;
        background-color: transparent;
        color: white;
        border: 2px solid #404040;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stDownloadButton > button:hover {
        background-color: #2d2d2d;
        border-color: #505050;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Download Qualified Leads (CSV)",
        data=csv,
        file_name=f"qualified_leads_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )


def display_lead_details(lead: Lead):
    """Display detailed view of a single lead"""
    st.subheader(f"{lead.name}")
    
    # Score card
    score_class = get_score_class(lead.total_score)
    st.markdown(f"""
    <div class="lead-card {score_class}">
        <h3>{get_score_emoji(lead.total_score)} {lead.total_score:.1f}/100 - {get_score_category(lead.total_score)}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Basic info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Title:**", lead.title)
        st.write("**Company:**", lead.company)
        st.write("**Email:**", lead.email or "N/A")
        st.write("**Location:**", lead.person_location or "Unknown")
    
    with col2:
        st.write("**Funding Stage:**", lead.funding_stage or "Unknown")
        st.write("**Company HQ:**", lead.company_hq or "Unknown")
        st.write("**Data Source:**", lead.data_source)
        st.write("**LinkedIn:**", lead.linkedin_url or "N/A")
    
    # Score breakdown
    st.subheader("Score Breakdown")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Role Fit", f"{lead.role_fit_score:.1f}/30")
    with col2:
        st.metric("Company Intent", f"{lead.company_intent_score:.1f}/20")
    with col3:
        st.metric("Technographic", f"{lead.technographic_score:.1f}/25")
    with col4:
        st.metric("Location", f"{lead.location_score:.1f}/10")
    with col5:
        st.metric("Scientific Intent", f"{lead.scientific_intent_score:.1f}/40")
    
    # Publications
    if lead.publications:
        st.subheader("Publications")
        try:
            pubs = json.loads(lead.publications)
            for pub in pubs:
                st.write(f"- **{pub.get('title', 'N/A')}** ({pub.get('year', 'N/A')})")
                if 'pubmed_id' in pub:
                    st.write(f"  PubMed ID: {pub['pubmed_id']}")
        except:
            st.write(lead.publications)
    
    # Notes
    if lead.notes:
        st.subheader("Notes")
        st.write(lead.notes)


def main():
    """Main application"""
    init_session_state()
    
    # Header
    st.title("🎯 Lead Generation Dashboard")
    st.markdown("**Intelligent lead identification and ranking for 3D in-vitro models**")
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        
        st.divider()
        
        # Filters
        st.header("Filters")
        
        score_range = st.slider(
            "Score Range",
            min_value=0.0,
            max_value=100.0,
            value=(0.0, 100.0),
            step=5.0
        )
        
        search_term = st.text_input("Search (Name, Title, Company, Location) - Press Enter to search")
        
        # Live Scrape Option
        if search_term and st.button(f"🔍 Scrape '{search_term}'", use_container_width=True):
             scrape_pubmed_leads(search_term)
        
        st.divider()
        
        # Stats
        st.header("Statistics")
        db = SessionLocal()
        repo = LeadRepository(db)
        all_leads = repo.get_all_leads()
        
        total_leads = len(all_leads)
        hot_leads = len([l for l in all_leads if l.total_score >= 80])
        warm_leads = len([l for l in all_leads if 50 <= l.total_score < 80])
        cold_leads = len([l for l in all_leads if l.total_score < 50])
        
        st.metric("Total Leads", total_leads)
        st.metric("🟢 Hot Leads", hot_leads)
        st.metric("🟡 Warm Leads", warm_leads)
        st.metric("⚪ Cold Leads", cold_leads)
        
        db.close()
    
    # Main content
    tab1, tab2 = st.tabs(["📊 All Leads", "🔍 Lead Details"])
    
    with tab1:
        # Get filtered leads
        db = SessionLocal()
        repo = LeadRepository(db)
        
        leads = repo.search_leads(
            search_term=search_term if search_term else None,
            min_score=score_range[0],
            max_score=score_range[1]
        )
        
        st.subheader(f"Leads ({len(leads)} found)")
        display_leads_table(leads)
        
        db.close()
    
    with tab2:
        # Lead selector
        db = SessionLocal()
        repo = LeadRepository(db)
        all_leads = repo.get_all_leads()
        
        if all_leads:
            lead_options = {f"{lead.name} - {lead.company}": lead.id for lead in all_leads}
            selected_lead_name = st.selectbox("Select a lead", list(lead_options.keys()))
            
            if selected_lead_name:
                lead_id = lead_options[selected_lead_name]
                lead = repo.get_lead(lead_id)
                
                if lead:
                    display_lead_details(lead)
        else:
            st.info("No leads available. Scrape PubMed to get started!")
        
        db.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        st.error(f"Application Error: {e}")
        st.code(traceback.format_exc())
