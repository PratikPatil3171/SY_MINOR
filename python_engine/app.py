"""
Flask API Server for Career Recommendation Engine
Provides REST API endpoints for the Node.js frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommendation_engine import RecommendationEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize recommendation engine (global - loaded once at startup)
CAREERS_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "careers.csv")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

print("\n" + "="*60)
print("INITIALIZING CAREER RECOMMENDATION API")
print("="*60)

# Check if careers.csv exists
if not os.path.exists(CAREERS_CSV):
    print(f"❌ ERROR: careers.csv not found at: {CAREERS_CSV}")
    print("Please ensure careers.csv is in the data/ directory")
    sys.exit(1)

try:
    engine = RecommendationEngine(CAREERS_CSV, cache_dir=CACHE_DIR)
    print("\n✓ API Server ready to accept requests!")
    print("="*60 + "\n")
except Exception as e:
    print(f"❌ ERROR initializing recommendation engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Career Recommendation API",
        "version": "1.0.0"
    })


@app.route('/api/recommend', methods=['POST'])
def recommend_careers():
    """
    Main recommendation endpoint
    
    Request body:
    {
        "email": "student@example.com",
        "name": "John Doe",
        "stream": "Science",
        "classLevel": "12th",
        "marks10th": 85,
        "marks12th": 88,
        "mathsPercent": 90,
        "sciencePercent": 88,
        "commercePercent": null,
        "englishPercent": 82,
        "csItPercent": 85,
        "interests": {
            "coding": 4,
            "design": 2,
            "math": 5,
            "science": 4,
            "business": 2,
            "people": 3,
            "creative": 3
        },
        "aptitude": {
            "quantitative": 8,
            "logical": 7,
            "verbal": 6,
            "creative": 5,
            "technical": 8,
            "commerce": 3
        },
        "dreamText": "I want to build software..."
    }
    
    Response:
    {
        "success": true,
        "recommendations": [...],
        "student_profile": {...},
        "query_text": "..."
    }
    """
    try:
        # Get request data
        form_data = request.get_json()
        
        if not form_data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Get top_k from query params (default: 10)
        top_k = request.args.get('top_k', 10, type=int)
        top_k = min(max(top_k, 1), 20)  # Clamp between 1-20
        
        # Generate recommendations
        print(f"\n📊 Received recommendation request for: {form_data.get('email', 'Unknown')}")
        result = engine.get_recommendations(form_data, top_k=top_k)
        
        return jsonify({
            "success": True,
            "recommendations": result["recommendations"],
            "student_profile": result["student_profile"],
            "query_text": result["query_text"],
            "total_candidates": result["total_candidates"]
        })
    
    except Exception as e:
        print(f"❌ Error in /api/recommend: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/recommend/summary', methods=['POST'])
def recommend_careers_summary():
    """
    Simplified recommendation endpoint (returns only top 5 with minimal data)
    """
    try:
        form_data = request.get_json()
        
        if not form_data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Get top_n from query params (default: 5)
        top_n = request.args.get('top_n', 5, type=int)
        top_n = min(max(top_n, 1), 10)  # Clamp between 1-10
        
        # Generate recommendations
        result = engine.get_recommendations(form_data, top_k=10)
        
        # Get simplified summary
        summary = engine.get_recommendation_summary(result["recommendations"], top_n=top_n)
        
        return jsonify({
            "success": True,
            "recommendations": summary,
            "total_analyzed": result["total_candidates"]
        })
    
    except Exception as e:
        print(f"❌ Error in /api/recommend/summary: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/careers', methods=['GET'])
def get_all_careers():
    """Get all available careers"""
    try:
        import pandas as pd
        
        careers_df = pd.read_csv(CAREERS_CSV)
        careers_list = careers_df.to_dict('records')
        
        return jsonify({
            "success": True,
            "careers": careers_list,
            "total": len(careers_list)
        })
    
    except Exception as e:
        print(f"❌ Error in /api/careers: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    # Run Flask server
    port = int(os.environ.get('PYTHON_PORT', 5000))
    print(f"\n🚀 Starting Flask server on port {port}...")
    print(f"📍 API Endpoints:")
    print(f"   - GET  http://localhost:{port}/api/health")
    print(f"   - POST http://localhost:{port}/api/recommend")
    print(f"   - POST http://localhost:{port}/api/recommend/summary")
    print(f"   - GET  http://localhost:{port}/api/careers")
    print()
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=False  # Disable reloader to avoid reloading the model twice
    )
