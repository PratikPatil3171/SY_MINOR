"""
FAISS Career Retrieval
Uses FAISS to efficiently find similar careers based on embeddings
"""
import os
import numpy as np
import faiss


class CareerRetriever:
    """Handles FAISS index for fast similarity search"""
    
    def __init__(self, embedding_dim=384, cache_dir="./cache"):
        """
        Initialize FAISS index
        
        Args:
            embedding_dim: Dimension of embeddings (384 for all-MiniLM-L6-v2)
            cache_dir: Directory to cache FAISS index
        """
        self.embedding_dim = embedding_dim
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize FAISS index (using L2 distance)
        self.index = None
        self.career_ids = None
    
    def build_index(self, career_embeddings, career_ids, force_rebuild=False):
        """
        Build FAISS index from career embeddings
        
        Args:
            career_embeddings: numpy array of shape (n_careers, embedding_dim)
            career_ids: list of career IDs corresponding to embeddings
            force_rebuild: If True, rebuild even if cache exists
        """
        cache_path = os.path.join(self.cache_dir, "faiss_index.bin")
        ids_path = os.path.join(self.cache_dir, "career_ids.npy")
        
        # Check if cached index exists
        if not force_rebuild and os.path.exists(cache_path) and os.path.exists(ids_path):
            print(f"Loading cached FAISS index from: {cache_path}")
            self.index = faiss.read_index(cache_path)
            self.career_ids = np.load(ids_path, allow_pickle=True).tolist()
            print(f"Loaded FAISS index with {self.index.ntotal} vectors")
            return
        
        # Build new index
        print(f"Building FAISS index with {len(career_embeddings)} vectors...")
        
        # Normalize embeddings for cosine similarity
        # (L2 distance on normalized vectors = cosine similarity)
        embeddings_normalized = career_embeddings.copy()
        faiss.normalize_L2(embeddings_normalized)
        
        # Create index (IndexFlatIP for inner product = cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Add vectors to index
        self.index.add(embeddings_normalized.astype('float32'))
        self.career_ids = career_ids
        
        # Save index to cache
        print(f"Saving FAISS index to: {cache_path}")
        faiss.write_index(self.index, cache_path)
        np.save(ids_path, np.array(career_ids, dtype=object))
        
        print(f"FAISS index built with {self.index.ntotal} vectors")
    
    def search(self, student_embedding, top_k=10):
        """
        Search for top K similar careers
        
        Args:
            student_embedding: numpy array of shape (embedding_dim,)
            top_k: Number of top careers to retrieve
        
        Returns:
            tuple: (career_indices, similarity_scores)
                career_indices: list of indices in career_ids
                similarity_scores: list of cosine similarity scores (0-1)
        """
        if self.index is None:
            raise ValueError("FAISS index not built. Call build_index() first.")
        
        # Normalize student embedding
        query = student_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query)
        
        # Search
        similarities, indices = self.index.search(query, top_k)
        
        # Convert to lists and return
        indices = indices[0].tolist()
        similarities = similarities[0].tolist()
        
        print(f"Retrieved top {len(indices)} careers with similarities: {[f'{s:.3f}' for s in similarities]}")
        
        return indices, similarities
    
    def get_career_id_by_index(self, index):
        """Get career ID by index"""
        if self.career_ids is None:
            raise ValueError("Career IDs not loaded")
        return self.career_ids[index]
    
    def get_career_ids_by_indices(self, indices):
        """Get career IDs by indices"""
        return [self.get_career_id_by_index(i) for i in indices]
