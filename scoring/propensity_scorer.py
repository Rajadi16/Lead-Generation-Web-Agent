"""
Propensity scoring algorithm for lead ranking
"""
from typing import Dict, List
import json
from config import SCORING_WEIGHTS, TOTAL_POSSIBLE_SCORE, LOCATION_SCORES


class PropensityScorer:
    """Calculate propensity scores for leads"""
    
    def __init__(self):
        self.weights = SCORING_WEIGHTS
        self.total_possible = TOTAL_POSSIBLE_SCORE
    
    def calculate_total_score(self, lead_data: Dict) -> Dict[str, float]:
        """
        Calculate all component scores and total score
        Returns dict with individual scores and total
        """
        scores = {
            'role_fit_score': self.calculate_role_fit_score(lead_data.get('title', '')),
            'company_intent_score': self.calculate_company_intent_score(lead_data),
            'technographic_score': self.calculate_technographic_score(lead_data),
            'location_score': self.calculate_location_score(lead_data.get('person_location', '')),
            'scientific_intent_score': self.calculate_scientific_intent_score(lead_data),
        }
        
        # Calculate raw total
        raw_total = sum(scores.values())
        
        # Normalize to 0-100 scale
        scores['total_score'] = min((raw_total / self.total_possible) * 100, 100)
        
        return scores
    
    def calculate_role_fit_score(self, title: str) -> float:
        """
        Calculate role fit score based on job title
        Max points: 30
        """
        if not title:
            return 0.0
        
        title_lower = title.lower()
        score = 0.0
        keywords = self.weights['role_fit']['keywords']
        
        # Check for each keyword (take max, not sum, to avoid double counting)
        keyword_scores = []
        
        if 'toxicology' in title_lower or 'toxicologist' in title_lower:
            keyword_scores.append(keywords['toxicology'])
        if 'safety' in title_lower:
            keyword_scores.append(keywords['safety'])
        if 'hepatic' in title_lower:
            keyword_scores.append(keywords['hepatic'])
        if 'liver' in title_lower:
            keyword_scores.append(keywords['liver'])
        if '3d' in title_lower:
            keyword_scores.append(keywords['3d'])
        if 'in vitro' in title_lower or 'in-vitro' in title_lower:
            keyword_scores.append(keywords['in vitro'])
        
        # Add base score for topic match
        if keyword_scores:
            score += max(keyword_scores)
        
        # Add seniority bonus
        if any(term in title_lower for term in ['director', 'head', 'vp', 'vice president', 'chief']):
            score += keywords['director']
        elif 'principal' in title_lower:
            score += keywords['director'] * 0.8  # Slightly less than director
        elif 'scientist' in title_lower:
            score += keywords['scientist']
        
        return min(score, self.weights['role_fit']['max_points'])
    
    def calculate_company_intent_score(self, lead_data: Dict) -> float:
        """
        Calculate company intent score based on funding and grants
        Max points: 20
        """
        score = 0.0
        funding_stage = lead_data.get('funding_stage', '').lower()
        funding_date = lead_data.get('funding_date', '')
        
        # Check funding stage and recency
        if funding_stage in ['series a', 'series b']:
            # Check if recent (within 12 months)
            if self._is_recent_funding(funding_date, months=12):
                score += self.weights['company_intent']['series_a_b_recent']
            else:
                score += self.weights['company_intent']['series_a_b_recent'] * 0.5
        
        elif funding_stage in ['series c', 'series d', 'series d+', 'ipo', 'public']:
            score += self.weights['company_intent']['series_c_plus']
        
        elif funding_stage == 'bootstrapped':
            score += self.weights['company_intent']['bootstrapped']
        
        # Check for NIH grants (would be in notes or separate field)
        notes = lead_data.get('notes', '').lower()
        if 'nih' in notes or 'grant' in notes:
            score += self.weights['company_intent']['nih_grant']
        
        return min(score, self.weights['company_intent']['max_points'])
    
    def calculate_technographic_score(self, lead_data: Dict) -> float:
        """
        Calculate technographic signals score
        Max points: 25
        """
        score = 0.0
        
        # Parse tech keywords found
        tech_keywords = lead_data.get('tech_keywords_found', '')
        if isinstance(tech_keywords, str) and tech_keywords:
            try:
                tech_keywords = json.loads(tech_keywords)
            except:
                tech_keywords = []
        
        if not isinstance(tech_keywords, list):
            tech_keywords = []
        
        tech_keywords_lower = [k.lower() for k in tech_keywords]
        
        # Check for specific technology mentions
        if any('3d model' in k or '3d cell' in k for k in tech_keywords_lower):
            score += self.weights['technographic']['3d_models_mention']
        
        if any('nam' in k or 'alternative method' in k for k in tech_keywords_lower):
            score += self.weights['technographic']['nams_mention']
        
        if any('liver' in k or 'hepat' in k for k in tech_keywords_lower):
            score += self.weights['technographic']['liver_disease_focus']
        
        # Check company name for indicators
        company = lead_data.get('company', '').lower()
        if any(term in company for term in ['liver', 'hepat', 'organ', 'organoid', 'biotech']):
            score += 5  # Bonus for relevant company focus
        
        return min(score, self.weights['technographic']['max_points'])
    
    def calculate_location_score(self, location: str) -> float:
        """
        Calculate location hub score
        Max points: 10
        """
        if not location:
            return LOCATION_SCORES['Other']
        
        location_lower = location.lower()
        
        # Check for each hub
        for hub, score in LOCATION_SCORES.items():
            if hub.lower() in location_lower:
                return score
        
        # Special cases
        if 'san francisco' in location_lower or 'sf' in location_lower or 'palo alto' in location_lower:
            return LOCATION_SCORES['Bay Area']
        
        if 'ma' in location_lower or 'massachusetts' in location_lower:
            # Could be Boston area
            return LOCATION_SCORES['Boston']
        
        return LOCATION_SCORES['Other']
    
    def calculate_scientific_intent_score(self, lead_data: Dict) -> float:
        """
        Calculate scientific intent score based on publications and conferences
        Max points: 40
        """
        score = 0.0
        
        # Parse publications
        publications = lead_data.get('publications', '')
        if isinstance(publications, str) and publications:
            try:
                publications = json.loads(publications)
            except:
                publications = []
        
        if not isinstance(publications, list):
            publications = []
        
        # Score based on publication recency
        recent_count = 0
        older_count = 0
        has_3d_culture_paper = False
        
        current_year = 2026
        
        for pub in publications:
            # Safely convert year to int, handling empty strings and invalid values
            year_value = pub.get('year', 0)
            try:
                year = int(year_value) if year_value else 0
            except (ValueError, TypeError):
                year = 0
            
            title = pub.get('title', '').lower()
            
            # Check for 3D culture papers
            if any(term in title for term in ['3d', 'spheroid', 'organoid', 'organ-on-chip']):
                has_3d_culture_paper = True
            
            # Check recency (only if we have a valid year)
            if year > 0:
                if year >= current_year - 1:  # Last 12 months
                    recent_count += 1
                elif year >= current_year - 2:  # 12-24 months
                    older_count += 1
        
        # Add points for publications
        if recent_count > 0:
            score += self.weights['scientific_intent']['publication_recent']
        elif older_count > 0:
            score += self.weights['scientific_intent']['publication_older']
        
        # Bonus for 3D culture papers
        if has_3d_culture_paper:
            score += self.weights['scientific_intent']['3d_culture_paper']
        
        # Check for conference participation
        conference = lead_data.get('conference_participation', '')
        if conference:
            score += self.weights['scientific_intent']['conference_presenter']
        
        return min(score, self.weights['scientific_intent']['max_points'])
    
    def _is_recent_funding(self, funding_date: str, months: int = 12) -> bool:
        """Check if funding date is within specified months"""
        if not funding_date:
            return False
        
        # Simple check - would need proper date parsing in production
        try:
            # Assuming format like "2025" or "2025-06"
            year = int(funding_date.split('-')[0])
            current_year = 2026
            
            if current_year - year <= 1:
                return True
        except:
            pass
        
        return False
    
    def get_score_category(self, total_score: float) -> str:
        """Get score category (Hot/Warm/Cold)"""
        if total_score >= 80:
            return "Hot Lead"
        elif total_score >= 50:
            return "Warm Lead"
        else:
            return "Cold Lead"
    
    def get_score_color(self, total_score: float) -> str:
        """Get color for score visualization"""
        if total_score >= 80:
            return "🟢"  # Green
        elif total_score >= 50:
            return "🟡"  # Yellow
        else:
            return "⚪"  # Gray


def main():
    """Test the scoring algorithm"""
    scorer = PropensityScorer()
    
    # Test lead 1: High-scoring lead
    test_lead_1 = {
        'name': 'Dr. Jane Smith',
        'title': 'Director of Toxicology',
        'company': 'BioTech Innovations',
        'person_location': 'Boston, MA',
        'funding_stage': 'Series B',
        'funding_date': '2025-06',
        'publications': json.dumps([
            {'title': '3D hepatic spheroids for DILI prediction', 'year': 2025},
            {'title': 'In vitro toxicology methods', 'year': 2024}
        ]),
        'tech_keywords_found': json.dumps(['3D models', 'NAMs', 'liver toxicity']),
        'conference_participation': 'SOT 2025 Speaker',
    }
    
    # Test lead 2: Medium-scoring lead
    test_lead_2 = {
        'name': 'Dr. John Doe',
        'title': 'Research Scientist',
        'company': 'Pharma Corp',
        'person_location': 'San Diego, CA',
        'funding_stage': 'Public',
        'publications': json.dumps([
            {'title': 'Drug metabolism studies', 'year': 2023}
        ]),
    }
    
    # Test lead 3: Low-scoring lead
    test_lead_3 = {
        'name': 'Dr. Alice Johnson',
        'title': 'Postdoctoral Fellow',
        'company': 'University Research Lab',
        'person_location': 'Other',
    }
    
    print("=== Propensity Scoring Test ===\n")
    
    for i, lead in enumerate([test_lead_1, test_lead_2, test_lead_3], 1):
        scores = scorer.calculate_total_score(lead)
        category = scorer.get_score_category(scores['total_score'])
        color = scorer.get_score_color(scores['total_score'])
        
        print(f"{color} Lead {i}: {lead['name']}")
        print(f"   Title: {lead['title']}")
        print(f"   Company: {lead['company']}")
        print(f"   Location: {lead['person_location']}")
        print(f"\n   Scores:")
        print(f"   - Role Fit: {scores['role_fit_score']:.1f}/30")
        print(f"   - Company Intent: {scores['company_intent_score']:.1f}/20")
        print(f"   - Technographic: {scores['technographic_score']:.1f}/25")
        print(f"   - Location: {scores['location_score']:.1f}/10")
        print(f"   - Scientific Intent: {scores['scientific_intent_score']:.1f}/40")
        print(f"\n   TOTAL SCORE: {scores['total_score']:.1f}/100 ({category})")
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()
