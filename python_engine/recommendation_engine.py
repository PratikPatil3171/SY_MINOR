"""
Main Recommendation Engine (Phase 2: ML-Enhanced)
Orchestrates all components to generate career recommendations
Supports both rule-based and ML-based aptitude scoring
"""
import os
from preprocessor import StudentPreprocessor
from embedding_generator import EmbeddingGenerator
from career_retriever import CareerRetriever
from scorer import CareerScorer
from ml_scorer import MLCareerScorer
from explainer import ExplanationGenerator


class RecommendationEngine:
    """Main engine that orchestrates the recommendation pipeline"""
    
    def __init__(self, careers_csv_path, cache_dir="./cache", use_ml=True, model_dir="models"):
        """
        Initialize the recommendation engine
        
        Args:
            careers_csv_path: Path to careers.csv file
            cache_dir: Directory for caching embeddings and indices
            use_ml: Whether to use ML-based scoring (Phase 2)
            model_dir: Directory containing trained ML models
        """
        print("Initializing Recommendation Engine...")
        
        self.cache_dir = cache_dir
        self.model_dir = model_dir
        self.use_ml = use_ml
        
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize components
        self.preprocessor = StudentPreprocessor()
        self.embedding_generator = EmbeddingGenerator(cache_dir=cache_dir)
        
        # Load careers and generate embeddings
        print("Loading career data...")
        careers_df = self.embedding_generator.load_careers_from_csv(careers_csv_path)
        
        print("Generating career embeddings...")
        career_embeddings = self.embedding_generator.generate_career_embeddings(careers_df)
        
        # Build FAISS index
        embedding_dim = self.embedding_generator.get_embedding_dimension()
        self.retriever = CareerRetriever(embedding_dim=embedding_dim, cache_dir=cache_dir)
        
        career_ids = careers_df["career_id"].tolist()
        self.retriever.build_index(career_embeddings, career_ids)
        
        # Initialize scorer (ML-enhanced or rule-based)
        ml_classifier = None
        if use_ml:
            try:
                from ml_domain_classifier import MLDomainClassifier
                ml_classifier = MLDomainClassifier(model_dir=model_dir)
                ml_classifier.load_models()
                print("[OK] ML models loaded successfully")
                self.scorer = MLCareerScorer(careers_df, ml_classifier, use_ml=True)
                self.ml_enabled = True
            except Exception as e:
                print(f"[WARNING] ML models not found, using rule-based scoring: {e}")
                self.scorer = CareerScorer(careers_df)
                self.ml_enabled = False
        else:
            print("Using rule-based scoring (ML disabled)")
            self.scorer = CareerScorer(careers_df)
            self.ml_enabled = False
        
        # Initialize explainer
        self.explainer = ExplanationGenerator()
        
        print("✓ Recommendation Engine initialized successfully!")
    
    def get_recommendations(self, form_data, top_k=10):
        """
        Get career recommendations for a student
        
        Args:
            form_data: Raw form data from student
            top_k: Number of recommendations to return
        
        Returns:
            dict: {
                "student_profile": {...},
                "recommendations": [...],
                "query_text": "..."
            }
        """
        print("\n" + "="*60)
        print("GENERATING CAREER RECOMMENDATIONS")
        print("="*60)
        
        # Step 1: Preprocess student data
        print("\n[1/5] Preprocessing student data...")
        student_profile = self.preprocessor.process_form_data(form_data)
        print(f"✓ Student profile created for: {student_profile.get('name', 'Unknown')}")
        print(f"  - Stream: {student_profile.get('stream')} | Class: {student_profile.get('class_level')}")
        print(f"  - CGPA: {student_profile.get('cgpa', 0):.1f}/10")
        
        # Step 2: Build query text
        print("\n[2/5] Building student query text...")
        query_text = self.preprocessor.build_student_query_text(student_profile)
        print(f"✓ Query text: {query_text[:150]}...")
        
        # Step 3: Generate student embedding
        print("\n[3/5] Generating student embedding...")
        student_embedding = self.embedding_generator.generate_student_embedding(query_text)
        print(f"✓ Embedding generated (dim: {len(student_embedding)})")
        
        # Step 4: Retrieve candidate careers using FAISS
        print(f"\n[4/5] Retrieving top {top_k} similar careers using FAISS...")
        candidate_indices, candidate_similarities = self.retriever.search(student_embedding, top_k=top_k)
        candidate_career_ids = self.retriever.get_career_ids_by_indices(candidate_indices)
        print(f"✓ Retrieved {len(candidate_career_ids)} candidate careers")
        
        # Step 5: Score and rank candidates
        print("\n[5/5] Scoring and ranking careers...")
        scored_careers = self.scorer.score_candidates(
            student_profile,
            candidate_career_ids,
            candidate_similarities
        )
        print(f"✓ Scored {len(scored_careers)} careers")
        
        # Get ML insights if available
        ml_insights = None
        if self.ml_enabled and hasattr(self.scorer, 'get_ml_insights'):
            print("\n[ML] Generating ML domain predictions...")
            ml_insights = self.scorer.get_ml_insights(student_profile)
            print(f"✓ Primary domain: {ml_insights['primary_domain']} (confidence: {ml_insights['confidence']:.1%})")
        
        # Add explanations
        print("\n[6/6] Generating explanations...")
        recommendations = self.explainer.add_explanations_to_recommendations(
            student_profile,
            scored_careers
        )
        print(f"✓ Added explanations to all recommendations")
        
        # Print top 3 recommendations
        print("\n" + "="*60)
        print("TOP 3 RECOMMENDATIONS")
        print("="*60)
        for i, career in enumerate(recommendations[:3], 1):
            print(f"\n{i}. {career['title']} (Score: {career['total_score']}/10)")
            print(f"   Domain: {career.get('domain', 'N/A')}")
            print(f"   Match: {career['explanation']['match_strength']}")
            print(f"   {career['explanation']['summary']}")
        
        print("\n" + "="*60 + "\n")
        
        result = {
            "student_profile": student_profile,
            "recommendations": recommendations,
            "query_text": query_text,
            "total_candidates": len(recommendations),
            "ml_enabled": self.ml_enabled
        }
        
        # Add ML insights to result if available
        if ml_insights:
            result["ml_insights"] = ml_insights
        
        return result
    
    def get_recommendation_summary(self, recommendations, top_n=5):
        """
        Get a simplified summary of top N recommendations
        
        Args:
            recommendations: Full recommendation results
            top_n: Number of top careers to include
        
        Returns:
            list: Simplified recommendation data
        """
        summary = []
        
        for career in recommendations[:top_n]:
            summary.append({
                "career_id": career["career_id"],
                "title": career["title"],
                "description": career["description"],
                "total_score": career["total_score"],
                "match_strength": career["explanation"]["match_strength"],
                "summary": career["explanation"]["summary"],
                "education_path": career["education_path"],
                "required_skills": career["required_skills"]
            })
        
        return summary
