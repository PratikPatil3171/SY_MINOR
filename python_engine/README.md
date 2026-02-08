# Career Recommendation Engine - Phase 1

This directory contains the Python-based career recommendation engine using **SBERT + FAISS + Simple Scoring**.

## 🎯 Overview

The recommendation engine provides personalized career suggestions based on:
- Student's academic performance
- Interest areas (coding, design, math, etc.)
- Aptitude scores (quantitative, logical, verbal, etc.)
- Career aspirations (free text)

## 🏗️ Architecture

### Components

1. **Preprocessor** (`preprocessor.py`)
   - Cleans and normalizes student form data
   - Converts raw inputs to standardized 0-10 scales
   - Builds query text for embedding generation

2. **Embedding Generator** (`embedding_generator.py`)
   - Uses SBERT (all-MiniLM-L6-v2) for text embeddings
   - Generates embeddings for all careers (cached)
   - Generates embedding for student queries

3. **Career Retriever** (`career_retriever.py`)
   - Uses FAISS for fast similarity search
   - Retrieves top-K similar careers based on cosine similarity
   - Indexes and caches career embeddings

4. **Scorer** (`scorer.py`)
   - Combines SBERT similarity with aptitude & interest matching
   - Formula: `0.6 * similarity + 0.2 * aptitude + 0.2 * interest`
   - Returns ranked list of careers with scores

5. **Explainer** (`explainer.py`)
   - Generates human-readable explanations
   - Explains why each career was recommended
   - Provides match strength and detailed reasons

6. **Recommendation Engine** (`recommendation_engine.py`)
   - Main orchestrator that combines all components
   - End-to-end pipeline from raw data to recommendations

7. **Flask API** (`app.py`)
   - REST API server for frontend integration
   - Endpoints for recommendations and career data

## 📊 Scoring System

Each career receives three scores:

### 1. Similarity Score (60% weight)
- Based on SBERT cosine similarity between student's aspirations and career description
- Measures semantic alignment of goals and career requirements

### 2. Aptitude Score (20% weight)
- Matches student's aptitude test results with career requirements
- Different careers require different aptitude combinations:
  - Technical careers: High technical + logical + quantitative
  - Design careers: High creative + technical
  - Commerce careers: High commerce + quantitative
  - People-focused: High verbal + creative

### 3. Interest Score (20% weight)
- Matches student's interests with career domains
- Maps interests (coding, design, math, etc.) to career requirements

### Final Score
```
Total Score = 0.6 × Similarity + 0.2 × Aptitude + 0.2 × Interest
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd python_engine
pip install -r requirements.txt
```

This will install:
- `flask` - Web API framework
- `flask-cors` - CORS support
- `sentence-transformers` - SBERT embeddings
- `faiss-cpu` - Fast similarity search
- `numpy` - Numerical operations
- `pandas` - Data manipulation
- `scikit-learn` - ML utilities

### First-time Setup

On first run, the engine will:
1. Download SBERT model (~80MB)
2. Load careers from `../data/careers.csv`
3. Generate embeddings for all careers
4. Build FAISS index
5. Cache everything for future use

**Note:** First run takes 1-2 minutes. Subsequent runs are instant (uses cache).

## 📁 File Structure

```
python_engine/
├── preprocessor.py           # Student data preprocessing
├── embedding_generator.py    # SBERT embedding generation
├── career_retriever.py       # FAISS similarity search
├── scorer.py                 # Career scoring logic
├── explainer.py             # Explanation generation
├── recommendation_engine.py  # Main orchestrator
├── app.py                   # Flask API server
├── test_engine.py           # Test script
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── cache/                  # Auto-generated cache
    ├── career_embeddings.npy
    ├── career_data.csv
    ├── faiss_index.bin
    └── career_ids.npy
```

## 🧪 Testing

### Test the Engine Locally

```bash
cd python_engine
python test_engine.py
```

This will:
- Initialize the recommendation engine
- Test with sample Science student data
- Test with sample Commerce student data
- Display detailed recommendations with explanations

### Expected Output

```
==================================================
TOP 3 RECOMMENDATIONS
==================================================

1. Software Developer (Score: 9.2/10)
   Match: Excellent Match
   Software Developer is highly recommended based on your profile.

2. Data Scientist (Score: 8.7/10)
   Match: Very Good Match
   Data Scientist is strongly recommended based on your profile.

3. Machine Learning Engineer (Score: 8.5/10)
   Match: Very Good Match
   Machine Learning Engineer is strongly recommended based on your profile.
```

## 🌐 Running the API Server

### Start the Flask Server

```bash
cd python_engine
python app.py
```

Server will start on `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
GET http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Career Recommendation API",
  "version": "1.0.0"
}
```

#### 2. Get Recommendations (Full)
```bash
POST http://localhost:5000/api/recommend
Content-Type: application/json

{
  "email": "student@example.com",
  "name": "John Doe",
  "stream": "Science",
  "classLevel": "12th",
  "marks10th": 85,
  "marks12th": 88,
  "mathsPercent": 90,
  "sciencePercent": 88,
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
  "dreamText": "I want to build software that helps people..."
}
```

Response includes detailed recommendations with explanations.

#### 3. Get Recommendations (Summary)
```bash
POST http://localhost:5000/api/recommend/summary?top_n=5
```

Returns simplified top 5 recommendations (less data).

#### 4. Get All Careers
```bash
GET http://localhost:5000/api/careers
```

Returns all available careers from the database.

## 🔧 Configuration

### Environment Variables

- `PYTHON_PORT` - API server port (default: 5000)

### Customization

#### Change Top-K Retrieval
In `app.py`, modify the `top_k` parameter:
```python
result = engine.get_recommendations(form_data, top_k=10)  # Change to 15, 20, etc.
```

#### Adjust Scoring Weights
In `scorer.py`, modify the scoring formula:
```python
total_score = (
    0.6 * similarity_score +  # Change weights here
    0.2 * aptitude_score +
    0.2 * interest_score
)
```

#### Change SBERT Model
In `embedding_generator.py`, change the model:
```python
self.model = SentenceTransformer("all-mpnet-base-v2")  # Larger, more accurate
```

Available models:
- `all-MiniLM-L6-v2` (default) - Fast, 384-dim
- `all-mpnet-base-v2` - More accurate, 768-dim, slower
- `paraphrase-multilingual-MiniLM-L12-v2` - Multilingual support

## 📈 Performance

- **First Load:** 1-2 minutes (downloads model + generates embeddings)
- **Cached Load:** <5 seconds
- **Per Request:** <100ms (with warm cache)
- **Memory:** ~500MB (model + embeddings)

## 🔄 Integration with Node.js Frontend

The Flask API runs separately from the Node.js server. Integration steps:

1. Start Python API server (port 5000)
2. Start Node.js server (port 3000)
3. Node.js makes HTTP requests to Python API

Example Node.js integration:
```javascript
// In your Node.js server
const axios = require('axios');

app.post('/api/get-career-recommendations', async (req, res) => {
  try {
    const studentData = req.body;
    
    // Call Python API
    const response = await axios.post(
      'http://localhost:5000/api/recommend',
      studentData
    );
    
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

## 🐛 Troubleshooting

### Model Download Fails
If SBERT model download fails, manually download:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### FAISS Installation Issues
If FAISS fails to install:
```bash
pip install faiss-cpu --no-cache-dir
```

For GPU support (optional):
```bash
pip install faiss-gpu
```

### Port Already in Use
Change the port:
```bash
PYTHON_PORT=5001 python app.py
```

### Careers CSV Not Found
Ensure `careers.csv` is in the `data/` directory:
```
Personalized/
  data/
    careers.csv  ← Must be here
  python_engine/
    app.py
```

## 📝 Next Steps (Phase 2)

Future enhancements:
- Train LightGBM model for better scoring
- Add collaborative filtering
- Include user feedback loop
- Implement A/B testing framework
- Add caching layer (Redis)
- Deploy to cloud (AWS/Azure)

## 📄 License

MIT

## 👨‍💻 Author

Career Advisor Team
