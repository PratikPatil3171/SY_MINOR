"""
Simple Scoring System
Combines SBERT similarity with aptitude and interest matching
"""
import numpy as np


class CareerScorer:
    """Scores careers based on multiple factors"""
    
    def __init__(self, careers_df):
        """
        Initialize scorer with career data
        
        Args:
            careers_df: DataFrame with career information
        """
        self.careers_df = careers_df
        
        # Define career-to-skills mapping for aptitude matching
        # Maps career_id to required aptitudes
        self.career_aptitudes = self._build_aptitude_mapping()
        self.career_interests = self._build_interest_mapping()
    
    def _build_aptitude_mapping(self):
        """
        Build mapping of careers to required aptitudes
        Returns dict: {career_id: {"quant": weight, "logical": weight, ...}}
        """
        mapping = {}
        
        for _, career in self.careers_df.iterrows():
            career_id = career["career_id"]
            title = career["title"].lower()
            skills = career.get("required_skills", "").lower()
            
            # Default weights
            weights = {
                "quant": 0,
                "logical": 0,
                "verbal": 0,
                "creative": 0,
                "technical": 0,
                "commerce": 0
            }
            
            # Technical/Engineering careers
            if any(x in title for x in ["software", "developer", "engineer", "data scientist", "ml", "ai", "cloud", "devops", "cybersecurity"]):
                weights["technical"] = 0.4
                weights["logical"] = 0.3
                weights["quant"] = 0.2
                weights["verbal"] = 0.1
            
            # Design careers
            elif any(x in title for x in ["designer", "ui", "ux", "game"]):
                weights["creative"] = 0.5
                weights["technical"] = 0.2
                weights["logical"] = 0.2
                weights["verbal"] = 0.1
            
            # Data/Analytics careers
            elif any(x in title for x in ["data", "analyst", "research"]):
                weights["quant"] = 0.4
                weights["logical"] = 0.3
                weights["technical"] = 0.2
                weights["verbal"] = 0.1
            
            # Commerce/Finance careers
            elif any(x in title for x in ["accountant", "finance", "banker", "tax", "audit", "economist"]):
                weights["commerce"] = 0.4
                weights["quant"] = 0.3
                weights["logical"] = 0.2
                weights["verbal"] = 0.1
            
            # Business/Management careers
            elif any(x in title for x in ["manager", "consultant", "entrepreneur", "business", "hr", "marketing"]):
                weights["verbal"] = 0.3
                weights["logical"] = 0.2
                weights["commerce"] = 0.2
                weights["creative"] = 0.2
                weights["quant"] = 0.1
            
            # Medical/Healthcare careers
            elif any(x in title for x in ["doctor", "medical", "biomedical", "pharmacist", "biotech"]):
                weights["logical"] = 0.3
                weights["verbal"] = 0.3
                weights["quant"] = 0.2
                weights["technical"] = 0.2
            
            # Default for others
            else:
                weights["logical"] = 0.3
                weights["verbal"] = 0.3
                weights["quant"] = 0.2
                weights["technical"] = 0.2
            
            mapping[career_id] = weights
        
        return mapping
    
    def _build_interest_mapping(self):
        """
        Build mapping of careers to interest areas
        Returns dict: {career_id: {"coding": weight, "design": weight, ...}}
        """
        mapping = {}
        
        for _, career in self.careers_df.iterrows():
            career_id = career["career_id"]
            title = career["title"].lower()
            interests_str = career.get("suitable_interests", "").lower()
            
            # Default weights
            weights = {
                "coding": 0,
                "design": 0,
                "math": 0,
                "science": 0,
                "business": 0,
                "people": 0,
                "creative": 0
            }
            
            # Coding-heavy careers
            if any(x in title or x in interests_str for x in ["software", "developer", "programming", "coding", "app"]):
                weights["coding"] = 0.5
                weights["math"] = 0.2
                weights["science"] = 0.2
                weights["creative"] = 0.1
            
            # Design careers
            elif any(x in title or x in interests_str for x in ["designer", "ui", "ux", "design"]):
                weights["design"] = 0.5
                weights["creative"] = 0.3
                weights["coding"] = 0.2
            
            # Data/Math careers
            elif any(x in title or x in interests_str for x in ["data", "scientist", "analyst", "math", "statistics"]):
                weights["math"] = 0.4
                weights["coding"] = 0.3
                weights["science"] = 0.2
                weights["business"] = 0.1
            
            # Engineering careers
            elif any(x in title for x in ["engineer", "mechanical", "electrical", "civil"]):
                weights["science"] = 0.4
                weights["math"] = 0.3
                weights["coding"] = 0.2
                weights["creative"] = 0.1
            
            # Business careers
            elif any(x in title or x in interests_str for x in ["business", "entrepreneur", "marketing", "sales"]):
                weights["business"] = 0.5
                weights["people"] = 0.3
                weights["creative"] = 0.2
            
            # People-focused careers
            elif any(x in title or x in interests_str for x in ["hr", "manager", "consultant", "teacher"]):
                weights["people"] = 0.5
                weights["business"] = 0.3
                weights["creative"] = 0.2
            
            # Science/Medical careers
            elif any(x in title for x in ["doctor", "medical", "biotech", "pharmacist"]):
                weights["science"] = 0.5
                weights["math"] = 0.2
                weights["people"] = 0.2
                weights["coding"] = 0.1
            
            # Default
            else:
                weights["math"] = 0.2
                weights["science"] = 0.2
                weights["business"] = 0.2
                weights["people"] = 0.2
                weights["creative"] = 0.2
            
            mapping[career_id] = weights
        
        return mapping
    
    def calculate_aptitude_score(self, student_profile, career_id):
        """
        Calculate aptitude match score (0-10)
        
        Args:
            student_profile: Dict with student aptitude scores
            career_id: Career ID
        
        Returns:
            float: Aptitude score (0-10)
        """
        if career_id not in self.career_aptitudes:
            return 5.0  # Default neutral score
        
        weights = self.career_aptitudes[career_id]
        
        # Calculate weighted average
        score = (
            weights["quant"] * student_profile.get("apt_quant", 0) +
            weights["logical"] * student_profile.get("apt_logical", 0) +
            weights["verbal"] * student_profile.get("apt_verbal", 0) +
            weights["creative"] * student_profile.get("apt_creative", 0) +
            weights["technical"] * student_profile.get("apt_technical", 0) +
            weights["commerce"] * student_profile.get("apt_commerce", 0)
        )
        
        return score
    
    def calculate_interest_score(self, student_profile, career_id):
        """
        Calculate interest match score (0-10)
        
        Args:
            student_profile: Dict with student interest scores
            career_id: Career ID
        
        Returns:
            float: Interest score (0-10)
        """
        if career_id not in self.career_interests:
            return 5.0  # Default neutral score
        
        weights = self.career_interests[career_id]
        
        # Calculate weighted average
        score = (
            weights["coding"] * student_profile.get("coding_interest", 0) +
            weights["design"] * student_profile.get("design_interest", 0) +
            weights["math"] * student_profile.get("math_interest", 0) +
            weights["science"] * student_profile.get("science_interest", 0) +
            weights["business"] * student_profile.get("business_interest", 0) +
            weights["people"] * student_profile.get("people_interest", 0) +
            weights["creative"] * student_profile.get("creative_interest", 0)
        )
        
        return score
    
    def calculate_total_score(self, student_profile, career_id, sbert_similarity):
        """
        Calculate total score combining SBERT similarity, aptitude, and interests
        
        Formula: 0.6 * similarity + 0.2 * aptitude + 0.2 * interest
        
        Args:
            student_profile: Dict with student data
            career_id: Career ID
            sbert_similarity: SBERT cosine similarity (0-1)
        
        Returns:
            float: Total score (0-10)
        """
        # Convert SBERT similarity to 0-10 scale
        similarity_score = sbert_similarity * 10
        
        # Calculate component scores
        aptitude_score = self.calculate_aptitude_score(student_profile, career_id)
        interest_score = self.calculate_interest_score(student_profile, career_id)
        
        # Weighted combination
        total_score = (
            0.6 * similarity_score +
            0.2 * aptitude_score +
            0.2 * interest_score
        )
        
        return total_score
    
    def score_candidates(self, student_profile, candidate_career_ids, candidate_similarities):
        """
        Score all candidate careers and return sorted results
        
        Args:
            student_profile: Dict with student data
            candidate_career_ids: List of career IDs
            candidate_similarities: List of SBERT similarities
        
        Returns:
            List of dicts with scored careers, sorted by total_score (descending)
        """
        results = []
        
        for career_id, similarity in zip(candidate_career_ids, candidate_similarities):
            # Calculate scores
            total_score = self.calculate_total_score(student_profile, career_id, similarity)
            aptitude_score = self.calculate_aptitude_score(student_profile, career_id)
            interest_score = self.calculate_interest_score(student_profile, career_id)
            
            # Get career details
            career_row = self.careers_df[self.careers_df["career_id"] == career_id].iloc[0]
            
            results.append({
                "career_id": career_id,
                "title": career_row["title"],
                "description": career_row["description"],
                "required_skills": career_row.get("required_skills", ""),
                "suitable_interests": career_row.get("suitable_interests", ""),
                "education_path": career_row.get("education_path", ""),
                "stream_tag": career_row.get("stream_tag", ""),
                "total_score": round(total_score, 2),
                "similarity_score": round(similarity * 10, 2),
                "aptitude_score": round(aptitude_score, 2),
                "interest_score": round(interest_score, 2),
                "sbert_similarity": round(similarity, 4)
            })
        
        # Sort by total score (descending)
        results.sort(key=lambda x: x["total_score"], reverse=True)
        
        return results
