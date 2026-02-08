"""
ML-Enhanced Scoring System
Combines SBERT similarity with ML-predicted domain aptitude scores
"""
import numpy as np
import os
from typing import Dict, Optional


class MLCareerScorer:
    """
    ML-enhanced career scorer.
    Uses ML model predictions for domain fit scores instead of rule-based aptitude matching.
    """
    
    def __init__(self, careers_df, ml_classifier=None, use_ml=True):
        """
        Initialize ML scorer with career data.
        
        Args:
            careers_df: DataFrame with career information
            ml_classifier: MLDomainClassifier instance (optional)
            use_ml: Whether to use ML predictions (falls back to rules if False)
        """
        self.careers_df = careers_df
        self.ml_classifier = ml_classifier
        self.use_ml = use_ml and ml_classifier is not None
        
        # Load domain mapper for career-to-domain mapping
        from domain_mapper import DomainMapper
        self.domain_mapper = DomainMapper()
        
        # Add domain labels to careers
        if 'domain' not in self.careers_df.columns:
            self.careers_df = self.domain_mapper.create_domain_labels(self.careers_df)
        
        # Fallback: rule-based aptitude mapping (used if ML not available)
        if not self.use_ml:
            from scorer import CareerScorer
            self.fallback_scorer = CareerScorer(careers_df)
        
        print(f"MLCareerScorer initialized (ML mode: {self.use_ml})")
    
    def calculate_aptitude_score_ml(self, student_profile: Dict, career_id: str) -> float:
        """
        Calculate aptitude score using ML domain predictions.
        
        Args:
            student_profile: Dict with aptitude scores
            career_id: Career ID
            
        Returns:
            Aptitude match score (0-10)
        """
        if not self.use_ml:
            # Fallback to rule-based scoring
            return self.fallback_scorer.calculate_aptitude_score(student_profile, career_id)
        
        # Get career's primary domain
        career_domain = self.domain_mapper.get_career_domain(career_id)
        
        # Predict domain fit scores using ML
        domain_scores = self.ml_classifier.predict_domain_scores(student_profile)
        
        # Get fit score for this career's domain
        domain_fit = domain_scores.get(career_domain, 50)  # 0-100 scale
        
        # Convert to 0-10 scale
        aptitude_score = domain_fit / 10.0
        
        return aptitude_score
    
    def calculate_interest_score(self, student_profile: Dict, career_id: str) -> float:
        """
        Calculate interest match score.
        
        Args:
            student_profile: Dict with 'interests' field
            career_id: Career ID
            
        Returns:
            Interest match score (0-10)
        """
        # Get career interests
        career = self.careers_df[self.careers_df["career_id"] == career_id].iloc[0]
        career_interests = career.get("suitable_interests", "").lower().split(",")
        career_interests = [i.strip() for i in career_interests if i.strip()]
        
        if not career_interests:
            return 5.0  # Neutral score
        
        # Get student interests
        student_interests = student_profile.get("interests", "").lower().split(",")
        student_interests = [i.strip() for i in student_interests if i.strip()]
        
        if not student_interests:
            return 5.0  # Neutral score
        
        # Calculate overlap
        matches = 0
        for student_interest in student_interests:
            for career_interest in career_interests:
                if (student_interest in career_interest or 
                    career_interest in student_interest):
                    matches += 1
                    break
        
        # Convert to 0-10 scale
        max_possible = min(len(student_interests), len(career_interests))
        if max_possible == 0:
            return 5.0
        
        score = (matches / max_possible) * 10
        return min(score, 10.0)
    
    def calculate_total_score(
        self,
        similarity_score: float,
        aptitude_score: float,
        interest_score: float,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate total weighted score.
        
        Args:
            similarity_score: SBERT similarity (0-1)
            aptitude_score: Aptitude match (0-10)
            interest_score: Interest match (0-10)
            weights: Optional custom weights (default: 0.6, 0.2, 0.2)
            
        Returns:
            Total score (0-10)
        """
        if weights is None:
            weights = {
                "similarity": 0.6,
                "aptitude": 0.2,
                "interest": 0.2
            }
        
        # Normalize similarity to 0-10 scale
        sim_score = similarity_score * 10
        
        total = (
            weights["similarity"] * sim_score +
            weights["aptitude"] * aptitude_score +
            weights["interest"] * interest_score
        )
        
        return round(total, 2)
    
    def score_candidates(
        self,
        student_profile: Dict,
        candidate_careers: list,
        similarity_scores: list
    ) -> list:
        """
        Score all candidate careers.
        
        Args:
            student_profile: Dict with student data (aptitudes, interests)
            candidate_careers: List of career IDs to score
            similarity_scores: List of SBERT similarity scores (parallel to candidate_careers)
            
        Returns:
            List of scored careers with details
        """
        scored_careers = []
        
        for i, career_id in enumerate(candidate_careers):
            # Get similarity score from parallel list
            sim_score = similarity_scores[i] if i < len(similarity_scores) else 0.0
            
            # Calculate aptitude score (using ML if available)
            apt_score = self.calculate_aptitude_score_ml(student_profile, career_id)
            
            # Calculate interest score
            int_score = self.calculate_interest_score(student_profile, career_id)
            
            # Calculate total score
            total_score = self.calculate_total_score(sim_score, apt_score, int_score)
            
            # Get career info
            career = self.careers_df[self.careers_df["career_id"] == career_id].iloc[0]
            
            scored_careers.append({
                "career_id": career_id,
                "title": career["title"],
                "total_score": total_score,
                "similarity_score": round(sim_score, 3),
                "aptitude_score": round(apt_score, 2),
                "interest_score": round(int_score, 2),
                "domain": career.get("domain", "unknown"),
                "description": career.get("description", ""),
                "required_skills": career.get("required_skills", ""),
                "education_path": career.get("education_path", "")
            })
        
        # Sort by total score (descending)
        scored_careers.sort(key=lambda x: x["total_score"], reverse=True)
        
        return scored_careers
    
    def get_ml_insights(self, student_profile: Dict) -> Dict:
        """
        Get ML model insights for a student.
        
        Args:
            student_profile: Dict with aptitude scores
            
        Returns:
            Dictionary with ML predictions and insights
        """
        if not self.use_ml:
            return {"ml_enabled": False, "message": "ML predictions not available"}
        
        # Get domain scores
        domain_scores = self.ml_classifier.predict_domain_scores(student_profile)
        
        # Get primary domain prediction
        primary_domain, confidence = self.ml_classifier.predict_primary_domain(student_profile)
        
        # Sort domains by fit score
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "ml_enabled": True,
            "primary_domain": primary_domain,
            "confidence": round(confidence, 3),
            "domain_scores": {k: round(v, 2) for k, v in domain_scores.items()},
            "top_3_domains": [
                {"domain": d, "score": round(s, 2)} 
                for d, s in sorted_domains[:3]
            ],
            "strength_areas": [d for d, s in sorted_domains if s >= 70]
        }


# Backward compatibility: keep original scorer available
from scorer import CareerScorer

__all__ = ['MLCareerScorer', 'CareerScorer']


if __name__ == "__main__":
    # Test ML scorer
    import pandas as pd
    from ml_domain_classifier import MLDomainClassifier
    
    print("=== ML Career Scorer Test ===\n")
    
    # Load careers
    careers_df = pd.read_csv("../data/careers.csv")
    
    # Try to load ML model
    ml_classifier = MLDomainClassifier(model_dir='models')
    
    try:
        ml_classifier.load_models()
        print("✓ ML models loaded\n")
        use_ml = True
    except FileNotFoundError:
        print("⚠ ML models not found, using rule-based fallback\n")
        use_ml = False
        ml_classifier = None
    
    # Initialize scorer
    scorer = MLCareerScorer(careers_df, ml_classifier, use_ml=use_ml)
    
    # Test student
    sample_student = {
        'quant': 95,
        'logical': 94,
        'verbal': 80,
        'creative': 60,
        'technical': 96,
        'commerce': 50,
        'interests': 'coding, problem solving, competitive programming'
    }
    
    # Test scoring
    print("Testing aptitude scoring:")
    test_careers = ['C001', 'C003', 'C023', 'C010']
    for career_id in test_careers:
        score = scorer.calculate_aptitude_score_ml(sample_student, career_id)
        career = careers_df[careers_df['career_id'] == career_id].iloc[0]
        print(f"  {career_id} ({career['title']}): {score:.2f}/10")
    
    # Get ML insights
    if use_ml:
        print("\n" + "="*50)
        print("ML Insights:")
        insights = scorer.get_ml_insights(sample_student)
        print(f"  Primary Domain: {insights['primary_domain']} (confidence: {insights['confidence']:.1%})")
        print(f"  Top 3 Domains:")
        for item in insights['top_3_domains']:
            print(f"    - {item['domain']}: {item['score']}/100")
