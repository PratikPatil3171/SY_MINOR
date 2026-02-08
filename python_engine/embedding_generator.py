"""
SBERT Embedding Generator
Generates embeddings for careers and student queries using sentence-transformers
"""
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd


class EmbeddingGenerator:
    """Handles embedding generation using SBERT"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2", cache_dir="./cache"):
        """
        Initialize SBERT model
        
        Args:
            model_name: Pre-trained SBERT model name
            cache_dir: Directory to cache model and embeddings
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"Loading SBERT model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        
        self.career_embeddings = None
        self.career_data = None
    
    def build_career_text(self, career_row):
        """
        Build comprehensive text for a career from CSV data
        
        Args:
            career_row: Dictionary/Series with career information
        
        Returns:
            Combined text string for embedding
        """
        parts = []
        
        # Title and description (most important)
        title = career_row.get("title", "")
        description = career_row.get("description", "")
        parts.append(f"{title}: {description}")
        
        # Required skills
        skills = career_row.get("required_skills", "")
        if skills:
            parts.append(f"Required skills: {skills}")
        
        # Suitable interests
        interests = career_row.get("suitable_interests", "")
        if interests:
            parts.append(f"Suitable for students interested in: {interests}")
        
        # Education path
        edu_path = career_row.get("education_path", "")
        if edu_path:
            parts.append(f"Education path: {edu_path}")
        
        # Stream tag
        stream = career_row.get("stream_tag", "")
        if stream:
            parts.append(f"Stream: {stream}")
        
        return " ".join(parts)
    
    def load_careers_from_csv(self, csv_path):
        """
        Load career data from CSV file
        
        Args:
            csv_path: Path to careers.csv file
        
        Returns:
            DataFrame with career data
        """
        print(f"Loading careers from: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} careers")
        return df
    
    def generate_career_embeddings(self, careers_df, force_regenerate=False):
        """
        Generate embeddings for all careers and cache them
        
        Args:
            careers_df: DataFrame with career data
            force_regenerate: If True, regenerate even if cache exists
        
        Returns:
            numpy array of embeddings (n_careers, embedding_dim)
        """
        cache_path = os.path.join(self.cache_dir, "career_embeddings.npy")
        career_data_path = os.path.join(self.cache_dir, "career_data.csv")
        
        # Check if cached embeddings exist
        if not force_regenerate and os.path.exists(cache_path) and os.path.exists(career_data_path):
            print(f"Loading cached career embeddings from: {cache_path}")
            self.career_embeddings = np.load(cache_path)
            self.career_data = pd.read_csv(career_data_path)
            print(f"Loaded {len(self.career_embeddings)} cached embeddings")
            return self.career_embeddings
        
        # Generate new embeddings
        print("Generating career embeddings...")
        career_texts = []
        
        for idx, row in careers_df.iterrows():
            career_text = self.build_career_text(row)
            career_texts.append(career_text)
        
        print(f"Encoding {len(career_texts)} career descriptions...")
        embeddings = self.model.encode(
            career_texts,
            convert_to_numpy=True,
            show_progress_bar=True,
            batch_size=32
        )
        
        # Cache embeddings and data
        print(f"Saving embeddings to: {cache_path}")
        np.save(cache_path, embeddings)
        careers_df.to_csv(career_data_path, index=False)
        
        self.career_embeddings = embeddings
        self.career_data = careers_df
        
        print(f"Generated and cached {len(embeddings)} career embeddings")
        return embeddings
    
    def generate_student_embedding(self, student_text):
        """
        Generate embedding for student query text
        
        Args:
            student_text: Combined text from student profile
        
        Returns:
            numpy array of embedding (embedding_dim,)
        """
        print(f"Generating student embedding for query: {student_text[:100]}...")
        embedding = self.model.encode(
            student_text,
            convert_to_numpy=True
        )
        return embedding
    
    def get_embedding_dimension(self):
        """Get the dimension of embeddings"""
        return self.model.get_sentence_embedding_dimension()
