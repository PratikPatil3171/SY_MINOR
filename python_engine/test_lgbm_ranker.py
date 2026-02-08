"""
Test LightGBM Ranking Model
Tests the trained LightGBM ranker with sample students.
"""

import os
import sys
import pandas as pd
import numpy as np
from lgbm_ranker import LGBMRankerModel


def test_lgbm_ranker():
    """Test LightGBM ranker with sample students."""
    
    print("="*70)
    print(" "*20 + "LightGBM RANKER TESTING")
    print("="*70)
    print()
    
    # Check if model exists
    model_dir = 'models'
    model_path = os.path.join(model_dir, 'lgbm_ranker.txt')
    
    if not os.path.exists(model_path):
        print("❌ LightGBM model not found!")
        print("   Please run: python train_lgbm.py")
        return False
    
    # Load model
    print("Loading LightGBM model...")
    ranker = LGBMRankerModel(model_dir=model_dir)
    ranker.load_model()
    print("✓ Model loaded\n")
    
    # Load careers for reference
    careers_df = pd.read_csv("../data/careers.csv")
    
    # Test cases - sample students
    test_students = [
        {
            "name": "Coding Expert",
            "features": {
                'similarity': 0.85,
                'stream_match': 1,
                'domain_match': 1,
                'apt_quant': 95,
                'apt_logical': 94,
                'apt_verbal': 80,
                'apt_creative': 60,
                'apt_technical': 96,
                'apt_commerce': 50,
                'marks_10th': 92,
                'marks_12th': 90,
                'avg_aptitude': 79.17,
                'tech_score': 88.3,
                'business_score': 58.2,
                'creative_score': 68.0
            },
            "expected_top": ["Software Developer", "Machine Learning Engineer", "Data Scientist"]
        },
        {
            "name": "Finance Specialist",
            "features": {
                'similarity': 0.80,
                'stream_match': 1,
                'domain_match': 1,
                'apt_quant': 90,
                'apt_logical': 88,
                'apt_verbal': 82,
                'apt_creative': 70,
                'apt_technical': 78,
                'apt_commerce': 96,
                'marks_10th': 87,
                'marks_12th': 89,
                'avg_aptitude': 84.0,
                'tech_score': 79.0,
                'business_score': 85.0,
                'creative_score': 75.0
            },
            "expected_top": ["Chartered Accountant", "Investment Banker", "Financial Analyst"]
        },
        {
            "name": "Creative Designer",
            "features": {
                'similarity': 0.75,
                'stream_match': 1,
                'domain_match': 1,
                'apt_quant': 70,
                'apt_logical': 75,
                'apt_verbal': 85,
                'apt_creative': 95,
                'apt_technical': 78,
                'apt_commerce': 60,
                'marks_10th': 78,
                'marks_12th': 79,
                'avg_aptitude': 77.17,
                'tech_score': 74.0,
                'business_score': 69.0,
                'creative_score': 91.0
            },
            "expected_top": ["UI/UX Designer", "Game Developer", "Digital Marketing"]
        }
    ]
    
    print("="*70)
    print("Testing LightGBM ranking predictions:")
    print("="*70)
    print()
    
    for student in test_students:
        print(f"Student: {student['name']}")
        print("-" * 70)
        
        # Create feature matrix for all careers
        n_careers = len(careers_df)
        feature_matrix = np.zeros((n_careers, len(ranker.feature_columns)))
        
        # Fill in student features for each career
        base_features = student['features']
        for i in range(n_careers):
            for j, col in enumerate(ranker.feature_columns):
                feature_matrix[i, j] = base_features.get(col, 0)
        
        # Predict scores
        scores = ranker.predict(feature_matrix)
        
        # Get top 5 careers
        top_indices = np.argsort(scores)[::-1][:5]
        
        print("\nTop 5 Predicted Careers:")
        for rank, idx in enumerate(top_indices, 1):
            career = careers_df.iloc[idx]
            score = scores[idx]
            marker = "✓" if career['title'] in student['expected_top'] else " "
            print(f"  {rank}. {marker} {career['title']:35s} (score: {score:.4f})")
        
        print(f"\nExpected in top careers: {', '.join(student['expected_top'])}")
        print()
    
    # Feature importance
    print("="*70)
    print("Model Feature Importance:")
    print("="*70)
    importance = ranker.get_feature_importance()
    print(importance.head(10).to_string(index=False))
    
    # Model metrics
    print("\n" + "="*70)
    print("Model Performance Metrics:")
    print("="*70)
    for metric, value in ranker.metrics.items():
        print(f"  {metric}: {value}")
    
    print("\n" + "="*70)
    print("✅ LightGBM ranker testing complete!")
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = test_lgbm_ranker()
    sys.exit(0 if success else 1)
