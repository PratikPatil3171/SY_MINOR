"""
LightGBM Ranker Model
Learning-to-rank model for career recommendations using LightGBM.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import ndcg_score, mean_squared_error


class LGBMRankerModel:
    """
    LightGBM-based ranking model for career recommendations.
    Uses learning-to-rank to predict relevance of (student, career) pairs.
    """
    
    FEATURE_COLUMNS = [
        'similarity',
        'stream_match',
        'domain_match',
        'apt_quant',
        'apt_logical',
        'apt_verbal',
        'apt_creative',
        'apt_technical',
        'apt_commerce',
        'marks_10th',
        'marks_12th',
        'avg_aptitude',
        'tech_score',
        'business_score',
        'creative_score'
    ]
    
    def __init__(self, model_dir: str = 'models'):
        """
        Initialize LightGBM ranker.
        
        Args:
            model_dir: Directory to save/load models
        """
        self.model_dir = model_dir
        self.model = None
        self.feature_columns = self.FEATURE_COLUMNS.copy()
        self.is_trained = False
        self.metrics = {}
        
        os.makedirs(model_dir, exist_ok=True)
    
    def prepare_data(
        self,
        pairs_df: pd.DataFrame,
        test_size: float = 0.2
    ) -> Tuple:
        """
        Prepare data for LightGBM ranking.
        
        Args:
            pairs_df: DataFrame with ranking pairs
            test_size: Test set ratio
            
        Returns:
            Tuple of (X_train, y_train, group_train, X_test, y_test, group_test)
        """
        print("Preparing ranking data...")
        
        # Get unique students for train/test split
        unique_students = pairs_df['student_id'].unique()
        train_students, test_students = train_test_split(
            unique_students,
            test_size=test_size,
            random_state=42
        )
        
        # Split data by student
        train_df = pairs_df[pairs_df['student_id'].isin(train_students)].copy()
        test_df = pairs_df[pairs_df['student_id'].isin(test_students)].copy()
        
        # Sort by group (important for LightGBM ranker!)
        train_df = train_df.sort_values('student_id')
        test_df = test_df.sort_values('student_id')
        
        # Extract features
        X_train = train_df[self.feature_columns].values
        y_train = train_df['relevance'].values
        group_train = train_df.groupby('student_id').size().values
        
        X_test = test_df[self.feature_columns].values
        y_test = test_df['relevance'].values
        group_test = test_df.groupby('student_id').size().values
        
        print(f"✓ Train: {len(train_students)} students, {len(train_df)} pairs")
        print(f"✓ Test: {len(test_students)} students, {len(test_df)} pairs")
        
        return X_train, y_train, group_train, X_test, y_test, group_test
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        group_train: np.ndarray,
        X_test: np.ndarray = None,
        y_test: np.ndarray = None,
        group_test: np.ndarray = None,
        params: Dict = None
    ):
        """
        Train LightGBM ranker.
        
        Args:
            X_train: Training features
            y_train: Training relevance scores
            group_train: Group sizes (# pairs per student)
            X_test: Test features (optional)
            y_test: Test relevance scores (optional)
            group_test: Test group sizes (optional)
            params: LightGBM parameters (optional)
        """
        print("\n=== Training LightGBM Ranker ===\n")
        
        # Default parameters
        if params is None:
            params = {
                'objective': 'lambdarank',
                'metric': 'ndcg',
                'ndcg_eval_at': [1, 3, 5, 10],
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': 0
            }
        
        # Create datasets
        train_data = lgb.Dataset(
            X_train,
            label=y_train,
            group=group_train,
            feature_name=self.feature_columns
        )
        
        valid_sets = [train_data]
        valid_names = ['train']
        
        if X_test is not None:
            test_data = lgb.Dataset(
                X_test,
                label=y_test,
                group=group_test,
                reference=train_data,
                feature_name=self.feature_columns
            )
            valid_sets.append(test_data)
            valid_names.append('test')
        
        # Train model
        print("Training LightGBM model...")
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=200,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=[
                lgb.early_stopping(stopping_rounds=20),
                lgb.log_evaluation(period=20)
            ]
        )
        
        self.is_trained = True
        
        # Evaluate
        if X_test is not None and y_test is not None:
            self._evaluate(X_test, y_test, group_test)
        
        print("\n✅ Training complete!")
    
    def _evaluate(self, X_test: np.ndarray, y_test: np.ndarray, group_test: np.ndarray):
        """Evaluate model performance."""
        print("\n" + "="*70)
        print("Model Evaluation")
        print("="*70)
        
        # Predict
        y_pred = self.model.predict(X_test)
        
        # Calculate NDCG (Normalized Discounted Cumulative Gain)
        # Group predictions by student for ranking evaluation
        start_idx = 0
        ndcg_scores = []
        
        for group_size in group_test:
            end_idx = start_idx + group_size
            y_true_group = y_test[start_idx:end_idx].reshape(1, -1)
            y_pred_group = y_pred[start_idx:end_idx].reshape(1, -1)
            
            # Calculate NDCG@k for this group
            try:
                ndcg = ndcg_score(y_true_group, y_pred_group, k=10)
                ndcg_scores.append(ndcg)
            except:
                pass  # Skip if all zeros
            
            start_idx = end_idx
        
        avg_ndcg = np.mean(ndcg_scores) if ndcg_scores else 0
        
        # MSE
        mse = mean_squared_error(y_test, y_pred)
        
        # Store metrics
        self.metrics = {
            'ndcg@10': avg_ndcg,
            'mse': mse,
            'n_test_groups': len(group_test),
            'best_iteration': self.model.best_iteration
        }
        
        print(f"NDCG@10: {avg_ndcg:.4f}")
        print(f"MSE: {mse:.4f}")
        print(f"Best iteration: {self.model.best_iteration}")
        print(f"Test groups: {len(group_test)}")
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Predict relevance scores for career candidates.
        
        Args:
            features: Feature matrix (n_careers, n_features)
            
        Returns:
            Predicted relevance scores
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load model.")
        
        return self.model.predict(features)
    
    def rank_careers(
        self,
        student_features: Dict,
        career_features: List[Dict],
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Rank careers for a student.
        
        Args:
            student_features: Student aptitudes and info
            career_features: List of career feature dicts
            top_k: Number of top careers to return
            
        Returns:
            List of (career_index, score) tuples, sorted by score
        """
        # Prepare features matrix
        n_careers = len(career_features)
        features_matrix = np.zeros((n_careers, len(self.feature_columns)))
        
        for i, career_feat in enumerate(career_features):
            for j, col in enumerate(self.feature_columns):
                features_matrix[i, j] = career_feat.get(col, 0)
        
        # Predict scores
        scores = self.predict(features_matrix)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Return (index, score) pairs
        results = [(idx, scores[idx]) for idx in top_indices]
        
        return results
    
    def save_model(self):
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        model_path = os.path.join(self.model_dir, 'lgbm_ranker.txt')
        self.model.save_model(model_path)
        print(f"✓ Saved LightGBM model to {model_path}")
        
        # Save metadata
        metadata = {
            'feature_columns': self.feature_columns,
            'metrics': self.metrics
        }
        metadata_path = os.path.join(self.model_dir, 'lgbm_metadata.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✓ Saved metadata to {metadata_path}")
    
    def load_model(self):
        """Load trained model from disk."""
        model_path = os.path.join(self.model_dir, 'lgbm_ranker.txt')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.model = lgb.Booster(model_file=model_path)
        self.is_trained = True
        
        # Load metadata
        metadata_path = os.path.join(self.model_dir, 'lgbm_metadata.pkl')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.feature_columns = metadata['feature_columns']
                self.metrics = metadata['metrics']
        
        print("✓ LightGBM model loaded successfully")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from trained model."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        importance = self.model.feature_importance(importance_type='gain')
        
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        })
        
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        return importance_df


if __name__ == "__main__":
    # Test LightGBM ranker
    print("=== LightGBM Ranker Test ===\n")
    
    # Load ranking pairs
    pairs_path = "../data/ranking_pairs.csv"
    
    if not os.path.exists(pairs_path):
        print("❌ Ranking pairs not found!")
        print("   Run: python ranking_pair_generator.py")
        exit(1)
    
    pairs_df = pd.read_csv(pairs_path)
    print(f"✓ Loaded {len(pairs_df)} ranking pairs\n")
    
    # Initialize ranker
    ranker = LGBMRankerModel(model_dir='models')
    
    # Prepare data
    X_train, y_train, group_train, X_test, y_test, group_test = ranker.prepare_data(pairs_df)
    
    # Train
    ranker.train(X_train, y_train, group_train, X_test, y_test, group_test)
    
    # Save
    ranker.save_model()
    
    # Feature importance
    print("\n" + "="*70)
    print("Top 10 Most Important Features:")
    print("="*70)
    importance = ranker.get_feature_importance()
    print(importance.head(10).to_string(index=False))
