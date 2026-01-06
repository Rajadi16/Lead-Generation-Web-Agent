"""
Email finder and generator for lead enrichment
"""
import re
from typing import Optional, List


class EmailFinder:
    """Generate and validate email addresses"""
    
    def __init__(self):
        self.common_patterns = [
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first_initial}{last}@{domain}",
            "{first}_{last}@{domain}",
        ]
    
    def generate_email(self, name: str, company: str, domain: Optional[str] = None) -> str:
        """
        Generate most likely email address based on name and company
        """
        if not name or not company:
            return ""
        
        # Parse name
        parts = self._parse_name(name)
        if not parts:
            return ""
        
        first = parts['first'].lower()
        last = parts['last'].lower()
        first_initial = first[0] if first else ""
        
        # Get or generate domain
        if not domain:
            domain = self._generate_domain(company)
        
        # Try most common pattern first
        email = f"{first}.{last}@{domain}"
        
        return email
    
    def generate_all_patterns(self, name: str, company: str, domain: Optional[str] = None) -> List[str]:
        """
        Generate all common email patterns for a person
        """
        if not name or not company:
            return []
        
        parts = self._parse_name(name)
        if not parts:
            return []
        
        first = parts['first'].lower()
        last = parts['last'].lower()
        first_initial = first[0] if first else ""
        
        if not domain:
            domain = self._generate_domain(company)
        
        emails = []
        for pattern in self.common_patterns:
            email = pattern.format(
                first=first,
                last=last,
                first_initial=first_initial,
                domain=domain
            )
            emails.append(email)
        
        return emails
    
    def _parse_name(self, name: str) -> Optional[dict]:
        """Parse full name into first and last name"""
        # Remove titles
        name = re.sub(r'\b(Dr|Prof|Mr|Ms|Mrs)\.?\s+', '', name, flags=re.IGNORECASE)
        
        parts = name.strip().split()
        
        if len(parts) < 2:
            return None
        
        # Handle middle names/initials
        if len(parts) == 2:
            return {'first': parts[0], 'last': parts[1]}
        else:
            # Take first and last, ignore middle
            return {'first': parts[0], 'last': parts[-1]}
    
    def _generate_domain(self, company: str) -> str:
        """
        Generate domain from company name
        This is a simple heuristic - in production, use a company domain lookup service
        """
        # Clean company name
        company = company.lower()
        
        # Remove common suffixes
        company = re.sub(r'\s+(inc|corp|corporation|ltd|limited|llc|gmbh)\.?$', '', company, flags=re.IGNORECASE)
        
        # Remove special characters
        company = re.sub(r'[^a-z0-9\s]', '', company)
        
        # Take first word or combine first two words
        words = company.split()
        if words:
            if len(words) == 1:
                domain = words[0]
            else:
                # For multi-word companies, try to create a reasonable domain
                domain = words[0]
        else:
            domain = "example"
        
        return f"{domain}.com"
    
    def validate_email_format(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def generate_linkedin_url(self, name: str) -> str:
        """
        Generate LinkedIn profile URL from name
        Format: https://www.linkedin.com/in/firstname-lastname
        """
        if not name:
            return ""
        
        # Parse name
        parts = self._parse_name(name)
        if not parts:
            return ""
        
        first = parts['first'].lower()
        last = parts['last'].lower()
        
        # Create LinkedIn-style URL slug
        linkedin_slug = f"{first}-{last}"
        
        # Remove any special characters
        linkedin_slug = re.sub(r'[^a-z0-9-]', '', linkedin_slug)
        
        return f"https://www.linkedin.com/in/{linkedin_slug}"
    
    def suggest_conferences(self, title: str, publications: list = None) -> str:
        """
        Suggest relevant conferences based on job title and publications
        Returns comma-separated list of likely conferences
        """
        conferences = []
        
        # Convert title to lowercase for matching
        title_lower = title.lower() if title else ""
        
        # Check publications for keywords
        pub_text = ""
        if publications:
            for pub in publications:
                if isinstance(pub, dict):
                    pub_text += pub.get('title', '').lower() + " "
        
        # Combine title and publication text for keyword matching
        combined_text = title_lower + " " + pub_text
        
        # Toxicology conferences
        if any(keyword in combined_text for keyword in ['toxicology', 'toxicologist', 'safety', 'dili', 'liver']):
            conferences.append('SOT (Society of Toxicology)')
        
        # Cancer research conferences
        if any(keyword in combined_text for keyword in ['cancer', 'oncology', 'tumor', 'carcinoma']):
            conferences.append('AACR (American Association for Cancer Research)')
        
        # Drug metabolism conferences
        if any(keyword in combined_text for keyword in ['metabolism', 'pharmacokinetics', 'xenobiotic']):
            conferences.append('ISSX (International Society for the Study of Xenobiotics)')
        
        # 3D cell culture / organoid conferences
        if any(keyword in combined_text for keyword in ['3d', 'organoid', 'spheroid', 'organ-on-chip', 'in vitro']):
            conferences.append('Organ-on-Chip World Summit')
            conferences.append('3D Cell Culture Conference')
        
        # Liver disease conferences
        if any(keyword in combined_text for keyword in ['hepat', 'liver', 'cirrhosis']):
            conferences.append('AASLD (American Association for the Study of Liver Diseases)')
        
        # Default if no specific match
        if not conferences:
            conferences.append('SOT (Society of Toxicology)')
        
        return ', '.join(conferences[:3])  # Return top 3 most relevant


def main():
    """Test email finder"""
    finder = EmailFinder()
    
    test_cases = [
        ("Dr. Jane Smith", "BioTech Innovations"),
        ("John Doe", "Pharma Corp"),
        ("Alice M. Johnson", "Liver Research Institute"),
    ]
    
    print("=== Email Finder Test ===\n")
    
    for name, company in test_cases:
        print(f"Name: {name}")
        print(f"Company: {company}")
        
        primary_email = finder.generate_email(name, company)
        print(f"Primary Email: {primary_email}")
        
        all_patterns = finder.generate_all_patterns(name, company)
        print(f"All Patterns: {', '.join(all_patterns)}")
        print()


if __name__ == "__main__":
    main()
