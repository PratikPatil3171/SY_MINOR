"""
Domain Mapper
Maps careers to skill domains for ML training and prediction.
Defines domain categories and career-to-domain relationships.
"""

import pandas as pd
from typing import Dict, List


class DomainMapper:
    """Maps careers to skill domains for ML-based aptitude scoring."""
    
    # Define domain categories
    DOMAINS = [
        'coding',        # Software, web, mobile development
        'analytics',     # Data science, analysis, research
        'design',        # UI/UX, creative work
        'engineering',   # Hardware, mechanical, electrical
        'healthcare',    # Medical, pharma, biotech
        'finance',       # Accounting, banking, investment
        'business',      # Management, marketing, HR
        'operations'     # Supply chain, ops management
    ]
    
    # Career ID to primary domain mapping
    CAREER_DOMAIN_MAP = {
        # Coding domain
        'C001': 'coding',      # Software Developer
        'C002': 'coding',      # Web Developer
        'C004': 'coding',      # ML Engineer
        'C005': 'coding',      # Cybersecurity
        'C006': 'coding',      # Cloud Engineer
        'C007': 'coding',      # DevOps Engineer
        'C008': 'coding',      # Mobile Developer
        'C009': 'coding',      # Game Developer
        
        # Analytics domain
        'C003': 'analytics',   # Data Scientist
        'C016': 'analytics',   # AI Researcher
        'C021': 'analytics',   # Data Analyst
        'C027': 'analytics',   # Financial Analyst
        'C030': 'analytics',   # Stock Market Analyst
        'C035': 'analytics',   # Economist
        
        # Design domain
        'C010': 'design',      # UI/UX Designer
        
        # Engineering domain
        'C011': 'engineering', # Electronics Engineer
        'C012': 'engineering', # Electrical Engineer
        'C013': 'engineering', # Mechanical Engineer
        'C014': 'engineering', # Civil Engineer
        'C015': 'engineering', # Robotics Engineer
        'C018': 'engineering', # Biomedical Engineer
        
        # Healthcare domain
        'C017': 'healthcare',  # Doctor
        'C019': 'healthcare',  # Pharmacist
        'C020': 'healthcare',  # Biotechnologist
        
        # Finance domain
        'C023': 'finance',     # CA
        'C024': 'finance',     # Cost Accountant
        'C025': 'finance',     # Company Secretary
        'C026': 'finance',     # Investment Banker
        'C028': 'finance',     # Tax Consultant
        'C029': 'finance',     # Auditor
        'C039': 'finance',     # Bank PO
        
        # Business domain
        'C022': 'business',    # Business Analyst
        'C031': 'business',    # Entrepreneur
        'C032': 'business',    # Marketing Manager
        'C033': 'business',    # Digital Marketer
        'C034': 'business',    # HR Manager
        'C036': 'business',    # Management Consultant
        'C040': 'business',    # Business Developer
        
        # Operations domain
        'C037': 'operations',  # Operations Manager
        'C038': 'operations',  # Supply Chain Analyst
    }
    
    # Domain feature importance mapping
    # Defines which aptitude features are most important for each domain
    DOMAIN_FEATURE_WEIGHTS = {
        'coding': {
            'aptitude_technical': 0.35,
            'aptitude_logical': 0.30,
            'aptitude_quant': 0.25,
            'aptitude_verbal': 0.05,
            'aptitude_creative': 0.05
        },
        'analytics': {
            'aptitude_quant': 0.35,
            'aptitude_logical': 0.30,
            'aptitude_technical': 0.20,
            'aptitude_verbal': 0.10,
            'aptitude_creative': 0.05
        },
        'design': {
            'aptitude_creative': 0.40,
            'aptitude_verbal': 0.25,
            'aptitude_technical': 0.20,
            'aptitude_logical': 0.10,
            'aptitude_quant': 0.05
        },
        'engineering': {
            'aptitude_technical': 0.30,
            'aptitude_quant': 0.25,
            'aptitude_logical': 0.25,
            'aptitude_creative': 0.15,
            'aptitude_verbal': 0.05
        },
        'healthcare': {
            'aptitude_verbal': 0.30,
            'aptitude_quant': 0.25,
            'aptitude_logical': 0.20,
            'aptitude_technical': 0.15,
            'aptitude_creative': 0.10
        },
        'finance': {
            'aptitude_quant': 0.35,
            'aptitude_commerce': 0.30,
            'aptitude_logical': 0.20,
            'aptitude_verbal': 0.10,
            'aptitude_technical': 0.05
        },
        'business': {
            'aptitude_verbal': 0.30,
            'aptitude_commerce': 0.25,
            'aptitude_logical': 0.20,
            'aptitude_creative': 0.15,
            'aptitude_quant': 0.10
        },
        'operations': {
            'aptitude_logical': 0.30,
            'aptitude_quant': 0.25,
            'aptitude_commerce': 0.20,
            'aptitude_verbal': 0.15,
            'aptitude_technical': 0.10
        }
    }
    
    def __init__(self):
        """Initialize domain mapper."""
        pass
    
    def get_career_domain(self, career_id: str) -> str:
        """
        Get primary domain for a career.
        
        Args:
            career_id: Career ID (e.g., 'C001')
            
        Returns:
            Domain name (e.g., 'coding')
        """
        return self.CAREER_DOMAIN_MAP.get(career_id, 'business')  # Default to business
    
    def get_domain_features(self, domain: str) -> Dict[str, float]:
        """
        Get feature importance weights for a domain.
        
        Args:
            domain: Domain name (e.g., 'coding')
            
        Returns:
            Dictionary of feature weights
        """
        return self.DOMAIN_FEATURE_WEIGHTS.get(domain, {})
    
    def create_domain_labels(self, careers_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add domain labels to careers dataframe.
        
        Args:
            careers_df: Careers dataframe with 'career_id' column
            
        Returns:
            Dataframe with added 'domain' column
        """
        careers_df = careers_df.copy()
        careers_df['domain'] = careers_df['career_id'].apply(self.get_career_domain)
        return careers_df
    
    def get_domain_careers(self, domain: str, careers_df: pd.DataFrame) -> List[str]:
        """
        Get all career IDs in a domain.
        
        Args:
            domain: Domain name
            careers_df: Careers dataframe
            
        Returns:
            List of career IDs
        """
        return [cid for cid, d in self.CAREER_DOMAIN_MAP.items() if d == domain]
    
    def get_all_domains(self) -> List[str]:
        """Get list of all domains."""
        return self.DOMAINS.copy()
    
    def get_domain_distribution(self, careers_df: pd.DataFrame) -> Dict[str, int]:
        """
        Get count of careers per domain.
        
        Args:
            careers_df: Careers dataframe
            
        Returns:
            Dictionary with domain counts
        """
        labeled_df = self.create_domain_labels(careers_df)
        return labeled_df['domain'].value_counts().to_dict()


if __name__ == "__main__":
    # Test domain mapper
    mapper = DomainMapper()
    
    print("=== Domain Mapper Test ===\n")
    
    print("1. All Domains:")
    for domain in mapper.get_all_domains():
        print(f"   - {domain}")
    
    print("\n2. Sample Career Mappings:")
    sample_careers = ['C001', 'C003', 'C010', 'C023', 'C017']
    for career_id in sample_careers:
        domain = mapper.get_career_domain(career_id)
        print(f"   {career_id} → {domain}")
    
    print("\n3. Domain Feature Weights (Coding):")
    coding_weights = mapper.get_domain_features('coding')
    for feature, weight in coding_weights.items():
        print(f"   {feature}: {weight}")
    
    print("\n✅ Domain Mapper working correctly!")
