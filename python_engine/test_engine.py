"""
Test script for the recommendation engine
Tests with sample student data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommendation_engine import RecommendationEngine


def test_recommendation_engine():
    """Test the recommendation engine with sample data"""
    
    print("\n" + "="*70)
    print("TESTING CAREER RECOMMENDATION ENGINE")
    print("="*70)
    
    # Initialize engine
    careers_csv = os.path.join(os.path.dirname(__file__), "..", "data", "careers.csv")
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    
    engine = RecommendationEngine(careers_csv, cache_dir=cache_dir)
    
    # Sample student data (similar to FakeStudents.csv - S001)
    sample_student = {
        "email": "test.student@example.com",
        "name": "Test Student",
        "stream": "Science",
        "classLevel": "12th",
        "marks10th": 92,
        "marks12th": 90,
        "mathsPercent": 95,
        "sciencePercent": 93,
        "commercePercent": None,
        "englishPercent": 88,
        "csItPercent": 94,
        "interests": {
            "coding": 5,  # Scale 1-5
            "design": 2,
            "math": 5,
            "science": 4,
            "business": 2,
            "people": 2,
            "creative": 3
        },
        "aptitude": {
            "quantitative": 9.5,  # Scale 0-10
            "logical": 9.4,
            "verbal": 8.0,
            "creative": 6.0,
            "technical": 9.6,
            "commerce": 5.0
        },
        "dreamText": "I want to work at a top tech company building scalable software used by millions. I love coding and problem solving."
    }
    
    # Get recommendations
    result = engine.get_recommendations(sample_student, top_k=10)
    
    # Display results
    print("\n" + "="*70)
    print("DETAILED RECOMMENDATIONS")
    print("="*70)
    
    for i, career in enumerate(result["recommendations"], 1):
        print(f"\n{'='*70}")
        print(f"RANK #{i}: {career['title']}")
        print(f"{'='*70}")
        print(f"Career ID: {career['career_id']}")
        print(f"Overall Score: {career['total_score']}/10")
        print(f"Match Strength: {career['explanation']['match_strength']}")
        print(f"\nDescription: {career['description']}")
        print(f"\nScores Breakdown:")
        print(f"  • Similarity Score:  {career['similarity_score']}/10 (SBERT match)")
        print(f"  • Aptitude Score:    {career['aptitude_score']}/10")
        print(f"  • Interest Score:    {career['interest_score']}/10")
        print(f"\nExplanation:")
        print(f"  {career['explanation']['summary']}")
        
        if career['explanation']['key_reasons']:
            print(f"\nKey Reasons:")
            for reason in career['explanation']['key_reasons']:
                print(f"  • {reason}")
        
        if career['explanation']['aptitude_match']:
            print(f"\nAptitude Match:")
            for reason in career['explanation']['aptitude_match']:
                print(f"  • {reason}")
        
        if career['explanation']['interest_match']:
            print(f"\nInterest Match:")
            for reason in career['explanation']['interest_match']:
                print(f"  • {reason}")
        
        if career['explanation']['academic_fit']:
            print(f"\nAcademic Fit:")
            for reason in career['explanation']['academic_fit']:
                print(f"  • {reason}")
        
        print(f"\nRequired Skills: {career['required_skills']}")
        print(f"Education Path: {career['education_path']}")
    
    print("\n" + "="*70)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")


def test_commerce_student():
    """Test with a commerce student"""
    
    print("\n" + "="*70)
    print("TESTING WITH COMMERCE STUDENT")
    print("="*70)
    
    careers_csv = os.path.join(os.path.dirname(__file__), "..", "data", "careers.csv")
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    
    engine = RecommendationEngine(careers_csv, cache_dir=cache_dir)
    
    # Commerce student data
    commerce_student = {
        "email": "commerce.student@example.com",
        "name": "Commerce Student",
        "stream": "Commerce",
        "classLevel": "12th",
        "marks10th": 87,
        "marks12th": 89,
        "mathsPercent": 82,
        "sciencePercent": None,
        "commercePercent": 90,
        "englishPercent": 88,
        "csItPercent": 75,
        "interests": {
            "coding": 1,
            "design": 2,
            "math": 4,
            "science": 2,
            "business": 5,
            "people": 4,
            "creative": 3
        },
        "aptitude": {
            "quantitative": 8.2,
            "logical": 8.4,
            "verbal": 7.8,
            "creative": 6.0,
            "technical": 7.0,
            "commerce": 9.4
        },
        "dreamText": "I dream of becoming a top chartered accountant and starting my own firm. I love working with numbers and finance."
    }
    
    result = engine.get_recommendations(commerce_student, top_k=5)
    
    print("\nTop 5 Recommendations:")
    for i, career in enumerate(result["recommendations"][:5], 1):
        print(f"\n{i}. {career['title']} (Score: {career['total_score']}/10)")
        print(f"   {career['explanation']['summary']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Run tests
    test_recommendation_engine()
    print("\n\n")
    test_commerce_student()
