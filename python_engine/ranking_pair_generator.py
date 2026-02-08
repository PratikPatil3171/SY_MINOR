"""
Ranking Pair Generator
Generates (student, career) pairs with features and relevance labels for LightGBM ranking.
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from domain_mapper import DomainMapper


class RankingPairGenerator:
    """
    Generates training pairs for learning-to-rank.
    Each pair = (student, career) with features and relevance label.
    """
    
    def __init__(self, students_csv: str, careers_csv: str):
        """
        Initialize pair generator.
        
        Args:
            students_csv: Path to FakeStudents.csv
            careers_csv: Path to careers.csv
        """
        self.students_csv = students_csv
        self.careers_csv = careers_csv
        self.domain_mapper = DomainMapper()
        
        # Load data
        self.students_df = None
        self.careers_df = None
        
    def load_data(self):
        """Load student and career data."""
        print("Loading data...")
        self.students_df = pd.read_csv(self.students_csv)
        self.careers_df = pd.read_csv(self.careers_csv)
        
        # Add domain labels
        self.careers_df = self.domain_mapper.create_domain_labels(self.careers_df)
        
        print(f"✓ Loaded {len(self.students_df)} students")
        print(f"✓ Loaded {len(self.careers_df)} careers")
    
    def calculate_relevance_score(
        self,
        student: pd.Series,
        career: pd.Series,
        is_best_match: bool
    ) -> int:
        """
        Calculate relevance score (0-3) for a (student, career) pair.
        
        Args:
            student: Student row
            career: Career row
            is_best_match: Whether this is the student's best career
            
        Returns:
            Relevance score:
            - 3: Highly relevant (best match + domain match)
            - 2: Relevant (domain match or similar aptitudes)
            - 1: Somewhat relevant (some alignment)
            - 0: Not relevant (poor fit)
        """
        # Start with base score
        if is_best_match:
            return 3  # Best match always gets highest score
        
        # Get domains
        student_best_career_id = student.get('best_career_id')
        best_career = self.careers_df[self.careers_df['career_id'] == student_best_career_id]
        
        if len(best_career) == 0:
            # Fallback if best career not found
            return self._calculate_aptitude_alignment(student, career)
        
        student_domain = best_career.iloc[0].get('domain', 'unknown')
        career_domain = career.get('domain', 'unknown')
        
        # Same domain as best career = relevant
        if student_domain == career_domain:
            return 2
        
        # Check aptitude alignment
        return self._calculate_aptitude_alignment(student, career)
    
    def _calculate_aptitude_alignment(self, student: pd.Series, career: pd.Series) -> int:
        """
        Calculate alignment based on aptitudes.
        
        Returns:
            1 or 0 based on aptitude fit
        """
        career_domain = career.get('domain', 'unknown')
        domain_weights = self.domain_mapper.get_domain_features(career_domain)
        
        # Calculate weighted aptitude score
        total_score = 0
        for feature, weight in domain_weights.items():
            student_apt = student.get(feature, 0)
            if pd.isna(student_apt):
                student_apt = 50  # Neutral for missing values
            total_score += student_apt * weight
        
        # High aptitude fit = somewhat relevant
        if total_score >= 70:
            return 1
        else:
            return 0
    
    def calculate_similarity_score(self, student: pd.Series, career: pd.Series) -> float:
        """
        Calculate semantic similarity between student and career.
        Uses simple keyword matching as proxy for SBERT similarity.
        
        Args:
            student: Student row
            career: Career row
            
        Returns:
            Similarity score (0-1)
        """
        # Get student interests
        student_interests = str(student.get('interests', '')).lower().split(',')
        student_interests = [i.strip() for i in student_interests if i.strip()]
        
        # Get career interests and skills
        career_text = ' '.join([
            str(career.get('suitable_interests', '')),
            str(career.get('required_skills', '')),
            str(career.get('title', ''))
        ]).lower()
        
        # Count matches
        matches = sum(1 for interest in student_interests if interest in career_text)
        
        if len(student_interests) == 0:
            return 0.5  # Neutral
        
        # Normalize to 0-1
        similarity = matches / len(student_interests)
        return min(similarity, 1.0)
    
    def calculate_stream_match(self, student: pd.Series, career: pd.Series) -> int:
        """
        Check if student stream matches career requirements.
        
        Returns:
            1 if match, 0 if no match
        """
        student_stream = student.get('stream', '').lower()
        career_stream_tag = career.get('stream_tag', '').lower()
        
        if 'both' in career_stream_tag:
            return 1
        
        if student_stream in career_stream_tag:
            return 1
        
        return 0
    
    def generate_pairs(self) -> pd.DataFrame:
        """
        Generate all (student, career) pairs with features and labels.
        
        Returns:
            DataFrame with columns:
            - student_id
            - career_id
            - features (similarity, aptitudes, etc.)
            - relevance (0-3)
            - group (student_id for grouping)
        """
        print("\nGenerating ranking pairs...")
        
        pairs = []
        
        for _, student in self.students_df.iterrows():
            student_id = student['student_id']
            best_career_id = student.get('best_career_id')
            
            # For each career, create a pair
            for _, career in self.careers_df.iterrows():
                career_id = career['career_id']
                is_best = (career_id == best_career_id)
                
                # Calculate relevance
                relevance = self.calculate_relevance_score(student, career, is_best)
                
                # Calculate features
                similarity = self.calculate_similarity_score(student, career)
                stream_match = self.calculate_stream_match(student, career)
                
                # Get aptitude scores
                apt_quant = student.get('aptitude_quant', 0)
                apt_logical = student.get('aptitude_logical', 0)
                apt_verbal = student.get('aptitude_verbal', 0)
                apt_creative = student.get('aptitude_creative', 0)
                apt_technical = student.get('aptitude_technical', 0)
                apt_commerce = student.get('aptitude_commerce', 0)
                
                # Handle missing values
                if pd.isna(apt_quant): apt_quant = 0
                if pd.isna(apt_logical): apt_logical = 0
                if pd.isna(apt_verbal): apt_verbal = 0
                if pd.isna(apt_creative): apt_creative = 0
                if pd.isna(apt_technical): apt_technical = 0
                if pd.isna(apt_commerce): apt_commerce = 0
                
                # Get marks
                marks_10th = student.get('marks_10th', 0) if not pd.isna(student.get('marks_10th')) else 0
                marks_12th = student.get('marks_12th', 0) if not pd.isna(student.get('marks_12th')) else marks_10th
                
                # Domain alignment
                career_domain = career.get('domain', 'unknown')
                student_best_career = self.careers_df[self.careers_df['career_id'] == best_career_id]
                student_domain = student_best_career.iloc[0].get('domain', 'unknown') if len(student_best_career) > 0 else 'unknown'
                domain_match = 1 if career_domain == student_domain else 0
                
                # Create pair
                pair = {
                    'student_id': student_id,
                    'career_id': career_id,
                    'group': student_id,  # Group by student for ranking
                    'relevance': relevance,
                    
                    # Features
                    'similarity': similarity,
                    'stream_match': stream_match,
                    'domain_match': domain_match,
                    
                    'apt_quant': apt_quant,
                    'apt_logical': apt_logical,
                    'apt_verbal': apt_verbal,
                    'apt_creative': apt_creative,
                    'apt_technical': apt_technical,
                    'apt_commerce': apt_commerce,
                    
                    'marks_10th': marks_10th,
                    'marks_12th': marks_12th,
                    
                    # Composite features
                    'avg_aptitude': np.mean([apt_quant, apt_logical, apt_verbal, apt_creative, apt_technical, apt_commerce]),
                    'tech_score': apt_technical * 0.5 + apt_logical * 0.3 + apt_quant * 0.2,
                    'business_score': apt_commerce * 0.5 + apt_verbal * 0.3 + apt_logical * 0.2,
                    'creative_score': apt_creative * 0.6 + apt_verbal * 0.4,
                }
                
                pairs.append(pair)
        
        pairs_df = pd.DataFrame(pairs)
        
        print(f"✓ Generated {len(pairs_df)} pairs")
        print(f"  Students: {len(self.students_df)}")
        print(f"  Careers: {len(self.careers_df)}")
        print(f"  Pairs per student: {len(self.careers_df)}")
        
        # Show relevance distribution
        print("\nRelevance distribution:")
        for score in sorted(pairs_df['relevance'].unique()):
            count = len(pairs_df[pairs_df['relevance'] == score])
            pct = count / len(pairs_df) * 100
            print(f"  Score {score}: {count:4d} pairs ({pct:5.1f}%)")
        
        return pairs_df
    
    def save_pairs(self, pairs_df: pd.DataFrame, output_dir: str = 'data'):
        """
        Save ranking pairs to CSV.
        
        Args:
            pairs_df: Pairs dataframe
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'ranking_pairs.csv')
        pairs_df.to_csv(output_path, index=False)
        
        print(f"\n✓ Saved ranking pairs to {output_path}")
        return output_path


if __name__ == "__main__":
    # Test pair generation
    students_csv = "../data/FakeStudents.csv"
    careers_csv = "../data/careers.csv"
    
    generator = RankingPairGenerator(students_csv, careers_csv)
    generator.load_data()
    
    # Generate pairs
    pairs_df = generator.generate_pairs()
    
    # Save
    generator.save_pairs(pairs_df)
    
    # Show sample
    print("\n" + "="*70)
    print("Sample pairs (first student):")
    print("="*70)
    sample = pairs_df[pairs_df['student_id'] == 'S001'].sort_values('relevance', ascending=False)
    print(sample[['career_id', 'relevance', 'similarity', 'domain_match', 'tech_score']].head(5))
