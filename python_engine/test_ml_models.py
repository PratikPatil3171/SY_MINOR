"""
Test ML Models
Tests the trained ML models with sample students.
"""

import os
import sys
import pandas as pd
from ml_domain_classifier import MLDomainClassifier
from ml_scorer import MLCareerScorer


def test_ml_models():
    """Test ML models with various student profiles."""
    
    print("="*70)
    print(" "*20 + "ML MODEL TESTING")
    print("="*70)
    print()
    
    # Check if models exist
    model_dir = 'models'
    if not os.path.exists(os.path.join(model_dir, 'domain_regression_model.pkl')):
        print("❌ ML models not found!")
        print("   Please run: python train_models.py")
        return False
    
    # Load models
    print("Loading ML models...")
    classifier = MLDomainClassifier(model_dir=model_dir)
    classifier.load_models()
    print("✓ Models loaded\n")
    
    # Load careers for scorer
    careers_df = pd.read_csv("../data/careers.csv")
    scorer = MLCareerScorer(careers_df, classifier, use_ml=True)
    
    # Test cases
    test_students = [
        {
            "name": "Coding Prodigy",
            "aptitudes": {
                'quant': 95,
                'logical': 94,
                'verbal': 80,
                'creative': 60,
                'technical': 96,
                'commerce': 50
            },
            "expected_domain": "coding"
        },
        {
            "name": "Data Science Enthusiast",
            "aptitudes": {
                'quant': 98,
                'logical': 95,
                'verbal': 83,
                'creative': 70,
                'technical': 90,
                'commerce': 55
            },
            "expected_domain": "analytics"
        },
        {
            "name": "Creative Designer",
            "aptitudes": {
                'quant': 70,
                'logical': 75,
                'verbal': 85,
                'creative': 95,
                'technical': 78,
                'commerce': 60
            },
            "expected_domain": "design"
        },
        {
            "name": "Finance Expert",
            "aptitudes": {
                'quant': 90,
                'logical': 85,
                'verbal': 80,
                'creative': 65,
                'technical': 70,
                'commerce': 94
            },
            "expected_domain": "finance"
        },
        {
            "name": "Business Leader",
            "aptitudes": {
                'quant': 80,
                'logical': 82,
                'verbal': 92,
                'creative': 85,
                'technical': 65,
                'commerce': 88
            },
            "expected_domain": "business"
        },
        {
            "name": "Healthcare Aspirant",
            "aptitudes": {
                'quant': 82,
                'logical': 85,
                'verbal': 88,
                'creative': 70,
                'technical': 75,
                'commerce': 60
            },
            "expected_domain": "healthcare"
        }
    ]
    
    print("="*70)
    print("Testing ML predictions on sample students:")
    print("="*70)
    print()
    
    correct_predictions = 0
    
    for student in test_students:
        print(f"Student: {student['name']}")
        print("-" * 70)
        
        # Get ML insights
        insights = scorer.get_ml_insights(student['aptitudes'])
        
        predicted_domain = insights['primary_domain']
        confidence = insights['confidence']
        expected = student['expected_domain']
        
        is_correct = predicted_domain == expected
        if is_correct:
            correct_predictions += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"{status} Predicted Domain: {predicted_domain} (confidence: {confidence:.1%})")
        print(f"  Expected Domain:  {expected}")
        
        print(f"\n  Top 3 Domain Scores:")
        for item in insights['top_3_domains']:
            marker = "→" if item['domain'] == expected else " "
            print(f"  {marker} {item['domain']:12s} {item['score']:.1f}/100")
        
        print(f"\n  Aptitude Scores:")
        for key, value in student['aptitudes'].items():
            print(f"    {key:12s} {value}/100")
        
        print()
    
    # Summary
    accuracy = (correct_predictions / len(test_students)) * 100
    
    print("="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    print(f"Total tests: {len(test_students)}")
    print(f"Correct predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("\n✅ Models performing well!")
    elif accuracy >= 60:
        print("\n⚠️ Models need improvement. Consider retraining with more data.")
    else:
        print("\n❌ Models performing poorly. Retrain with better data.")
    
    print()
    
    # Test specific career scoring
    print("="*70)
    print("Testing career-specific aptitude scoring:")
    print("="*70)
    print()
    
    test_careers = ['C001', 'C003', 'C010', 'C023', 'C032']
    sample_student = test_students[0]['aptitudes']  # Coding prodigy
    
    print("Sample Student: Coding Prodigy")
    print("Testing aptitude scores for different careers:\n")
    
    for career_id in test_careers:
        career = careers_df[careers_df['career_id'] == career_id].iloc[0]
        score = scorer.calculate_aptitude_score_ml(sample_student, career_id)
        domain = career.get('domain', 'N/A')
        print(f"  {career_id} {career['title']:30s} [{domain:12s}] → {score:.2f}/10")
    
    print()
    print("="*70)
    print("✅ ML model testing complete!")
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = test_ml_models()
    sys.exit(0 if success else 1)
