"""
Simple API test script
Tests the Flask API endpoints
"""
import requests
import json
import sys


def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:5000/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API server")
        print("Make sure the Flask server is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_recommendation():
    """Test recommendation endpoint"""
    print("\n" + "="*60)
    print("Testing Recommendation Endpoint")
    print("="*60)
    
    # Load sample request
    with open("sample_request.json", "r") as f:
        student_data = json.load(f)
    
    print(f"Sending request for student: {student_data['name']}")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/recommend",
            json=student_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                print(f"\n✓ Success! Received {len(data['recommendations'])} recommendations")
                print("\nTop 3 Recommendations:")
                
                for i, career in enumerate(data['recommendations'][:3], 1):
                    print(f"\n{i}. {career['title']}")
                    print(f"   Score: {career['total_score']}/10")
                    print(f"   Match: {career['explanation']['match_strength']}")
                    print(f"   Summary: {career['explanation']['summary']}")
                
                return True
            else:
                print(f"❌ API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API server")
        print("Make sure the Flask server is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_summary():
    """Test summary endpoint"""
    print("\n" + "="*60)
    print("Testing Summary Endpoint")
    print("="*60)
    
    with open("sample_request.json", "r") as f:
        student_data = json.load(f)
    
    try:
        response = requests.post(
            "http://localhost:5000/api/recommend/summary?top_n=5",
            json=student_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Success! Received {len(data['recommendations'])} recommendations")
            
            for i, career in enumerate(data['recommendations'], 1):
                print(f"\n{i}. {career['title']} (Score: {career['total_score']}/10)")
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_careers():
    """Test get all careers endpoint"""
    print("\n" + "="*60)
    print("Testing Get All Careers Endpoint")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:5000/api/careers")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Success! Retrieved {data['total']} careers")
            print("\nSample careers:")
            for career in data['careers'][:5]:
                print(f"  - {career['career_id']}: {career['title']}")
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CAREER RECOMMENDATION API - TEST SUITE")
    print("="*60)
    print("\nMake sure the Flask server is running before testing!")
    print("Start server with: python app.py")
    
    input("\nPress Enter to start tests...")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Get All Careers", test_careers()))
    results.append(("Full Recommendation", test_recommendation()))
    results.append(("Summary Recommendation", test_summary()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
