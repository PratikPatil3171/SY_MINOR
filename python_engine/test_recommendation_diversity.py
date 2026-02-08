"""
Test script to verify ML recommendation system provides personalized recommendations
Tests with 5 different user profiles and compares results
"""
import requests
import json
from datetime import datetime

API_URL = "http://localhost:5000/api/recommend"

# Test User Profiles - Diverse backgrounds
TEST_USERS = [
    {
        "name": "User 1: CS Engineering Student",
        "profile": {
            "email": "test1@example.com",
            "name": "Rahul Sharma",
            "stream": "Science",
            "classLevel": "12th",
            "marks10th": 92,
            "marks12th": 88,
            "cgpaSem": None,
            "interests": {
                "coding": 5,
                "design": 2,
                "math": 5,
                "science": 4,
                "business": 1,
                "people": 2
            },
            "aptitude": {
                "quantitative": 9,
                "logical": 8,
                "verbal": 6
            },
            "skills": ["Python", "Java", "Problem Solving", "Data Structures"],
            "careerDomains": ["Technology", "Engineering"],
            "higherStudies": "Yes",
            "entranceExams": ["JEE", "BITSAT"],
            "workEnvironment": "Office/Lab",
            "workStyles": ["Independent", "Technical"],
            "financialConstraints": "Medium",
            "locationRestrictions": "None",
            "dreamCareer": "I want to become a software engineer and work on AI/ML projects"
        }
    },
    {
        "name": "User 2: Medical Aspirant",
        "profile": {
            "email": "test2@example.com",
            "name": "Priya Patel",
            "stream": "Science",
            "classLevel": "12th",
            "marks10th": 94,
            "marks12th": 91,
            "cgpaSem": None,
            "interests": {
                "coding": 1,
                "design": 2,
                "math": 3,
                "science": 5,
                "business": 1,
                "people": 5
            },
            "aptitude": {
                "quantitative": 7,
                "logical": 7,
                "verbal": 8
            },
            "skills": ["Biology", "Chemistry", "Patient Care", "Communication"],
            "careerDomains": ["Healthcare", "Medicine"],
            "higherStudies": "Yes",
            "entranceExams": ["NEET"],
            "workEnvironment": "Hospital/Clinic",
            "workStyles": ["Team-oriented", "Helping Others"],
            "financialConstraints": "High",
            "locationRestrictions": "None",
            "dreamCareer": "I want to become a doctor and help people, specializing in pediatrics"
        }
    },
    {
        "name": "User 3: Business & Management",
        "profile": {
            "email": "test3@example.com",
            "name": "Arjun Mehta",
            "stream": "Commerce",
            "classLevel": "12th",
            "marks10th": 85,
            "marks12th": 87,
            "cgpaSem": None,
            "interests": {
                "coding": 2,
                "design": 3,
                "math": 3,
                "science": 2,
                "business": 5,
                "people": 5
            },
            "aptitude": {
                "quantitative": 7,
                "logical": 8,
                "verbal": 9
            },
            "skills": ["Leadership", "Communication", "Marketing", "Finance"],
            "careerDomains": ["Business", "Management", "Finance"],
            "higherStudies": "Yes",
            "entranceExams": ["CAT", "GMAT"],
            "workEnvironment": "Corporate Office",
            "workStyles": ["Team-oriented", "Leadership"],
            "financialConstraints": "Medium",
            "locationRestrictions": "Metro cities",
            "dreamCareer": "I want to become a business manager or start my own company"
        }
    },
    {
        "name": "User 4: Creative Designer",
        "profile": {
            "email": "test4@example.com",
            "name": "Sneha Reddy",
            "stream": "Arts",
            "classLevel": "12th",
            "marks10th": 78,
            "marks12th": 82,
            "cgpaSem": None,
            "interests": {
                "coding": 2,
                "design": 5,
                "math": 2,
                "science": 2,
                "business": 3,
                "people": 4
            },
            "aptitude": {
                "quantitative": 5,
                "logical": 6,
                "verbal": 8
            },
            "skills": ["Photoshop", "UI/UX Design", "Creativity", "Visual Arts"],
            "careerDomains": ["Design", "Creative Arts", "Media"],
            "higherStudies": "Maybe",
            "entranceExams": ["NIFT", "NID"],
            "workEnvironment": "Studio/Creative Space",
            "workStyles": ["Creative", "Independent"],
            "financialConstraints": "Low",
            "locationRestrictions": "None",
            "dreamCareer": "I want to become a UX designer or graphic designer for tech companies"
        }
    },
    {
        "name": "User 5: Average Science Student (Undecided)",
        "profile": {
            "email": "test5@example.com",
            "name": "Amit Kumar",
            "stream": "Science",
            "classLevel": "12th",
            "marks10th": 75,
            "marks12th": 72,
            "cgpaSem": None,
            "interests": {
                "coding": 3,
                "design": 2,
                "math": 3,
                "science": 3,
                "business": 3,
                "people": 3
            },
            "aptitude": {
                "quantitative": 6,
                "logical": 6,
                "verbal": 6
            },
            "skills": ["Basic Programming", "Mathematics", "Science"],
            "careerDomains": [],
            "higherStudies": "Maybe",
            "entranceExams": [],
            "workEnvironment": "Flexible",
            "workStyles": ["Team-oriented"],
            "financialConstraints": "High",
            "locationRestrictions": "Home city only",
            "dreamCareer": "Not sure yet, exploring options"
        }
    }
]


def test_recommendation_system():
    """Test the recommendation system with diverse users"""
    
    print("\n" + "="*80)
    print("TESTING ML RECOMMENDATION SYSTEM - DIVERSITY & PERSONALIZATION CHECK")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing with {len(TEST_USERS)} diverse user profiles\n")
    
    results = []
    all_recommendations = {}
    
    for i, test_user in enumerate(TEST_USERS, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(TEST_USERS)}: {test_user['name']}")
        print(f"{'='*80}")
        
        profile = test_user['profile']
        
        # Display user profile summary
        print(f"\n📋 Profile Summary:")
        print(f"  • Stream: {profile['stream']}")
        print(f"  • Marks: 10th={profile['marks10th']}%, 12th={profile['marks12th']}%")
        print(f"  • Interest Strengths: {get_top_interests(profile['interests'])}")
        print(f"  • Aptitude Scores: Q={profile['aptitude']['quantitative']}, "
              f"L={profile['aptitude']['logical']}, V={profile['aptitude']['verbal']}")
        print(f"  • Domains: {', '.join(profile['careerDomains']) if profile['careerDomains'] else 'Not specified'}")
        print(f"  • Dream: {profile['dreamCareer'][:60]}...")
        
        try:
            # Call recommendation API
            print(f"\n🔄 Calling recommendation API...")
            response = requests.post(API_URL, json=profile, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('recommendations'):
                    recommendations = data['recommendations']
                    top_5 = recommendations[:5]
                    
                    print(f"\n✅ SUCCESS: Received {len(recommendations)} recommendations")
                    print(f"\n🎯 Top 5 Career Recommendations:")
                    
                    career_names = []
                    for j, rec in enumerate(top_5, 1):
                        career = rec.get('title', rec.get('career_title', 'Unknown'))
                        score = rec.get('total_score', 0)
                        match_reason = rec.get('explanation', {}).get('summary', 'N/A')[:50]
                        
                        print(f"  {j}. {career}")
                        print(f"     Score: {score:.2f} | Reason: {match_reason}...")
                        
                        career_names.append(career)
                    
                    all_recommendations[test_user['name']] = career_names
                    
                    results.append({
                        "user": test_user['name'],
                        "status": "SUCCESS",
                        "top_5_careers": career_names,
                        "total_recommendations": len(recommendations),
                        "profile": profile
                    })
                else:
                    print(f"\n❌ FAILED: {data.get('error', 'Unknown error')}")
                    results.append({
                        "user": test_user['name'],
                        "status": "FAILED",
                        "error": data.get('error', 'No recommendations returned'),
                        "profile": profile
                    })
            else:
                print(f"\n❌ HTTP ERROR: Status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                results.append({
                    "user": test_user['name'],
                    "status": "HTTP_ERROR",
                    "error": f"Status {response.status_code}",
                    "profile": profile
                })
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ CONNECTION ERROR: Cannot connect to {API_URL}")
            print(f"   Please ensure Python recommendation engine is running on port 5000")
            results.append({
                "user": test_user['name'],
                "status": "CONNECTION_ERROR",
                "error": "Cannot connect to recommendation service",
                "profile": profile
            })
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            results.append({
                "user": test_user['name'],
                "status": "ERROR",
                "error": str(e),
                "profile": profile
            })
    
    # Analysis
    print(f"\n\n{'='*80}")
    print("ANALYSIS: PERSONALIZATION CHECK")
    print(f"{'='*80}\n")
    
    analyze_diversity(all_recommendations, results)
    
    # Save detailed results
    save_test_results(results)
    
    return results


def get_top_interests(interests):
    """Get top 2 interests from interest dict"""
    sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
    top_2 = [f"{name.capitalize()}({score})" for name, score in sorted_interests[:2]]
    return ", ".join(top_2)


def analyze_diversity(all_recommendations, results):
    """Analyze if recommendations are diverse and personalized"""
    
    if len(all_recommendations) < 2:
        print("⚠️  Not enough successful tests to analyze diversity")
        return
    
    # Check if all users got same recommendations
    rec_lists = list(all_recommendations.values())
    
    print("📊 Recommendation Comparison:\n")
    
    # Show top career for each user
    for user_name, careers in all_recommendations.items():
        print(f"  {user_name[:40]:<40} → {careers[0]}")
    
    # Check overlap
    print(f"\n🔍 Diversity Analysis:\n")
    
    # Compare each pair
    overlaps = []
    user_names = list(all_recommendations.keys())
    
    for i in range(len(user_names)):
        for j in range(i+1, len(user_names)):
            user1 = user_names[i]
            user2 = user_names[j]
            careers1 = set(all_recommendations[user1])
            careers2 = set(all_recommendations[user2])
            
            overlap = len(careers1.intersection(careers2))
            overlap_pct = (overlap / 5) * 100
            overlaps.append(overlap_pct)
            
            if overlap == 5:
                print(f"  ⚠️  {overlap}/5 careers match between:")
                print(f"      • {user1[:35]}")
                print(f"      • {user2[:35]}")
                print(f"      → 100% overlap - Possible issue with personalization!")
            elif overlap >= 3:
                print(f"  ⚡ {overlap}/5 careers match between:")
                print(f"      • {user1[:35]}")
                print(f"      • {user2[:35]}")
    
    avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
    
    print(f"\n📈 Average Overlap: {avg_overlap:.1f}%")
    
    if avg_overlap < 40:
        print(f"  ✅ GOOD: Recommendations are personalized (low overlap)")
    elif avg_overlap < 70:
        print(f"  ⚡ MODERATE: Some personalization, but could be better")
    else:
        print(f"  ❌ WARNING: High overlap suggests limited personalization")
    
    # Success rate
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    total = len(results)
    success_rate = (successful / total) * 100
    
    print(f"\n✓ Test Success Rate: {successful}/{total} ({success_rate:.0f}%)")


def save_test_results(results):
    """Save detailed test results to JSON file"""
    
    output_file = "test_recommendation_results.json"
    
    output_data = {
        "test_date": datetime.now().isoformat(),
        "total_tests": len(results),
        "successful_tests": sum(1 for r in results if r['status'] == 'SUCCESS'),
        "failed_tests": sum(1 for r in results if r['status'] != 'SUCCESS'),
        "results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print(f"   Total file size: {len(json.dumps(output_data, indent=2))} bytes")


if __name__ == "__main__":
    print("\n🚀 Starting Recommendation System Test...")
    print("📍 Make sure Python recommendation engine is running on port 5000\n")
    
    try:
        # Quick health check
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Recommendation engine is running!\n")
        else:
            print("⚠️  Recommendation engine responded but with unexpected status\n")
    except:
        print("❌ WARNING: Cannot connect to recommendation engine on port 5000")
        print("   Please start it first: cd python_engine && python app.py\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            exit(1)
    
    results = test_recommendation_system()
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETED")
    print("="*80)
    print("\nCheck 'test_recommendation_results.json' for detailed results")
