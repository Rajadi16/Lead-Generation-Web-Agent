"""
PubMed scraper for finding researchers in toxicology and 3D cell culture
"""
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from Bio import Entrez
from config import PUBMED_KEYWORDS, get_settings

settings = get_settings()
Entrez.email = settings.PUBMED_EMAIL


class PubMedScraper:
    """Scraper for PubMed/NCBI database"""
    
    def __init__(self, email: str = None):
        if email:
            Entrez.email = email
    
    def search_papers(
        self,
        keywords: List[str],
        months_back: int = 24,
        max_results: int = 100
    ) -> List[str]:
        """
        Search PubMed for papers matching keywords
        Returns list of PubMed IDs
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Format dates for PubMed
        date_range = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[pdat]"
        
        # Build query
        query_parts = [f'"{keyword}"' for keyword in keywords]
        query = f"({' OR '.join(query_parts)}) AND {date_range}"
        
        print(f"Searching PubMed with query: {query}")
        
        try:
            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record["IdList"]
            print(f"Found {len(id_list)} papers")
            return id_list
            
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict]:
        """
        Fetch detailed information for papers
        Returns list of paper details with authors
        """
        if not pubmed_ids:
            return []
        
        papers = []
        
        try:
            # Fetch details in batches of 20
            batch_size = 20
            for i in range(0, len(pubmed_ids), batch_size):
                batch = pubmed_ids[i:i + batch_size]
                
                handle = Entrez.efetch(
                    db="pubmed",
                    id=batch,
                    rettype="medline",
                    retmode="xml"
                )
                records = Entrez.read(handle)
                handle.close()
                
                for record in records['PubmedArticle']:
                    paper_info = self._parse_paper_record(record)
                    if paper_info:
                        papers.append(paper_info)
                
                # Be nice to NCBI servers
                time.sleep(0.5)
            
            print(f"Fetched details for {len(papers)} papers")
            return papers
            
        except Exception as e:
            print(f"Error fetching paper details: {e}")
            return []
    
    def _parse_paper_record(self, record) -> Optional[Dict]:
        """Parse a PubMed record into structured data"""
        try:
            article = record['MedlineCitation']['Article']
            
            # Extract title
            title = article.get('ArticleTitle', '')
            
            # Extract publication date
            pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', '')
            month = pub_date.get('Month', '01')
            
            # Extract authors
            authors = []
            author_list = article.get('AuthorList', [])
            
            for author in author_list:
                if 'LastName' in author and 'ForeName' in author:
                    name = f"{author['ForeName']} {author['LastName']}"
                    
                    # Extract affiliation
                    affiliation = ""
                    if 'AffiliationInfo' in author and author['AffiliationInfo']:
                        affiliation = author['AffiliationInfo'][0].get('Affiliation', '')
                    
                    authors.append({
                        'name': name,
                        'affiliation': affiliation,
                        'is_corresponding': False  # Could be enhanced
                    })
            
            # Extract abstract keywords
            abstract = article.get('Abstract', {}).get('AbstractText', [])
            if isinstance(abstract, list):
                abstract_text = ' '.join([str(a) for a in abstract])
            else:
                abstract_text = str(abstract)
            
            return {
                'title': title,
                'year': year,
                'month': month,
                'authors': authors,
                'abstract': abstract_text[:500],  # First 500 chars
                'pubmed_id': record['MedlineCitation']['PMID']
            }
            
        except Exception as e:
            print(f"Error parsing paper record: {e}")
            return None
    
    def extract_leads_from_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Extract potential leads from paper author lists
        Focus on corresponding authors and those with relevant affiliations
        """
        leads = []
        seen_names = set()
        
        for paper in papers:
            for author in paper['authors']:
                name = author['name']
                
                # Skip if we've already seen this person
                if name in seen_names:
                    continue
                
                affiliation = author['affiliation']
                
                # Skip if no affiliation
                if not affiliation:
                    continue
                
                # Extract company from affiliation
                company = self._extract_company_from_affiliation(affiliation)
                
                # Extract location from affiliation
                location = self._extract_location_from_affiliation(affiliation)
                
                lead = {
                    'name': name,
                    'title': 'Research Scientist',  # Default, will be enriched
                    'company': company,
                    'person_location': location,
                    'company_hq': location,
                    'publications': [{
                        'title': paper['title'],
                        'year': paper['year'],
                        'pubmed_id': paper['pubmed_id']
                    }],
                    'recent_publication_count': 1,
                    'data_source': 'PubMed',
                }
                
                leads.append(lead)
                seen_names.add(name)
        
        print(f"Extracted {len(leads)} unique leads from papers")
        return leads
    
    def _extract_company_from_affiliation(self, affiliation: str) -> str:
        """Extract company/institution name from affiliation string"""
        # Simple extraction - take first part before comma
        parts = affiliation.split(',')
        if parts:
            company = parts[0].strip()
            # Remove common prefixes
            for prefix in ['Department of', 'Division of', 'Center for', 'Institute of']:
                if company.startswith(prefix):
                    # Try to get the institution name from later parts
                    if len(parts) > 1:
                        return parts[1].strip()
            return company
        return "Unknown"
    
    def _extract_location_from_affiliation(self, affiliation: str) -> str:
        """Extract location from affiliation string"""
        # Look for common location patterns
        parts = affiliation.split(',')
        
        # Usually location is in the last few parts
        for part in reversed(parts):
            part = part.strip()
            # Check if it looks like a location (contains state/country)
            if any(indicator in part.upper() for indicator in ['USA', 'UK', 'MA', 'CA', 'SWITZERLAND', 'BOSTON', 'CAMBRIDGE']):
                return part
        
        # Return last part as fallback
        if parts:
            return parts[-1].strip()
        
        return "Unknown"


def main():
    """Test the PubMed scraper"""
    scraper = PubMedScraper()
    
    # Search for papers
    print("Searching PubMed for relevant papers...")
    paper_ids = scraper.search_papers(PUBMED_KEYWORDS, months_back=24, max_results=50)
    
    if paper_ids:
        # Fetch paper details
        print("\nFetching paper details...")
        papers = scraper.fetch_paper_details(paper_ids)
        
        # Extract leads
        print("\nExtracting leads from papers...")
        leads = scraper.extract_leads_from_papers(papers)
        
        # Display sample leads
        print(f"\n=== Sample Leads (showing first 5) ===")
        for i, lead in enumerate(leads[:5], 1):
            print(f"\n{i}. {lead['name']}")
            print(f"   Company: {lead['company']}")
            print(f"   Location: {lead['person_location']}")
            print(f"   Publications: {lead['recent_publication_count']}")
        
        return leads
    else:
        print("No papers found")
        return []


if __name__ == "__main__":
    main()
