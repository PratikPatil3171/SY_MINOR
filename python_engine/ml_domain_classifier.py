"""
ML Domain Classifier
Trains and uses ML models to predict domain fit scores.
Uses RandomForest for multi-output regression to predict aptitude fit for each domain.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, classification_report, accuracy_score
from domain_mapper import DomainMapper


class MLDomainClassifier:
    """
    ML-based domain aptitude predictor.
    Uses RandomForest models to predict domain fit scores.
    """
    
    def __init__(self, model_dir: str = 'models'):
        """
        Initialize ML domain classifier.
        
        Args:
            model_dir: Directory to save/load models
        """
        self.model_dir = model_dir
        self.domain_mapper = DomainMapper()
        
        # Models
        self.regression_model = None  # Multi-output regressor for domain fit scores
        self.classification_model = None  # Classifier for primary domain
        
        # Model metadata
        self.feature_names = None
        self.domain_names = None
        self.is_trained = False
        
        # Performance metrics
        self.metrics = {}
        
        os.makedirs(model_dir, exist_ok=True)
    
    def train_regression_model(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame,
        n_estimators: int = 100,
        max_depth: int = 10,
        random_state: int = 42
    ) -> Dict:
        """
        Train RandomForest regressor for domain fit scores.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target domain fit scores (n_samples, n_domains)
            n_estimators: Number of trees
            max_depth: Max tree depth
            random_state: Random seed
            
        Returns:
            Dictionary with training metrics
        """
        print("Training regression model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
        
        # Train model
        self.regression_model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.regression_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.regression_model.predict(X_test)
        
        # Calculate metrics for each domain
        domain_metrics = {}
        for i, domain in enumerate(self.domain_names):
            mse = mean_squared_error(y_test.iloc[:, i], y_pred[:, i])
            r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
            domain_metrics[domain] = {'mse': mse, 'r2': r2}
        
        # Overall metrics
        overall_mse = mean_squared_error(y_test, y_pred)
        overall_r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'overall_mse': overall_mse,
            'overall_r2': overall_r2,
            'domain_metrics': domain_metrics,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        self.metrics['regression'] = metrics
        
        print(f"✓ Regression model trained")
        print(f"  Overall R² score: {overall_r2:.3f}")
        print(f"  Overall MSE: {overall_mse:.2f}")
        
        return metrics
    
    def train_classification_model(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_estimators: int = 100,
        max_depth: int = 10,
        random_state: int = 42
    ) -> Dict:
        """
        Train RandomForest classifier for primary domain prediction.
        
        Args:
            X: Feature matrix
            y: Target domain labels
            n_estimators: Number of trees
            max_depth: Max tree depth
            random_state: Random seed
            
        Returns:
            Dictionary with training metrics
        """
        print("\nTraining classification model...")
        
        # Split data (no stratification for small datasets to avoid errors)
        # Check if stratification is possible
        class_counts = y.value_counts()
        can_stratify = all(count >= 2 for count in class_counts)
        
        if can_stratify:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=random_state, stratify=y
            )
        else:
            print("  [INFO] Small dataset - using random split without stratification")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=random_state
            )
        
        # Train model
        self.classification_model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.classification_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classification_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation (use min of 3 or n_classes for cv folds)
        n_classes = len(np.unique(y_train))
        cv_folds = min(3, n_classes, len(y_train) // 2)
        
        if cv_folds >= 2:
            cv_scores = cross_val_score(
                self.classification_model, X_train, y_train, cv=cv_folds, scoring='accuracy'
            )
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
        else:
            print("  [INFO] Too few samples for cross-validation, skipping...")
            cv_mean = accuracy
            cv_std = 0.0
        
        metrics = {
            'accuracy': accuracy,
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        self.metrics['classification'] = metrics
        
        print(f"✓ Classification model trained")
        print(f"  Accuracy: {accuracy:.3f}")
        print(f"  CV Score: {cv_mean:.3f} (±{cv_std:.3f})")
        
        return metrics
    
    def train(
        self,
        X: pd.DataFrame,
        y_regression: pd.DataFrame,
        y_classification: pd.Series
    ):
        """
        Train both regression and classification models.
        
        Args:
            X: Feature matrix
            y_regression: Domain fit score targets
            y_classification: Primary domain labels
        """
        print("=== ML Model Training ===\n")
        
        # Store metadata
        self.feature_names = list(X.columns)
        self.domain_names = list(y_regression.columns)
        
        # Train regression model
        reg_metrics = self.train_regression_model(X, y_regression)
        
        # Train classification model
        class_metrics = self.train_classification_model(X, y_classification)
        
        self.is_trained = True
        
        print("\n✅ All models trained successfully!")
    
    def predict_domain_scores(self, student_features: Dict) -> Dict[str, float]:
        """
        Predict domain fit scores for a student.
        
        Args:
            student_features: Dictionary with aptitude scores
            
        Returns:
            Dictionary mapping domain → fit score (0-100)
        """
        if not self.is_trained:
            raise ValueError("Models not trained. Call train() first or load models.")
        
        # Prepare feature vector
        feature_vector = self._prepare_feature_vector(student_features)
        
        # Predict domain scores
        X = pd.DataFrame([feature_vector], columns=self.feature_names)
        predictions = self.regression_model.predict(X)[0]
        
        # Create domain score dictionary
        domain_scores = {
            domain: float(np.clip(score, 0, 100))
            for domain, score in zip(self.domain_names, predictions)
        }
        
        return domain_scores
    
    def predict_primary_domain(self, student_features: Dict) -> Tuple[str, float]:
        """
        Predict primary domain for a student.
        
        Args:
            student_features: Dictionary with aptitude scores
            
        Returns:
            Tuple of (predicted_domain, confidence)
        """
        if not self.is_trained:
            raise ValueError("Models not trained. Call train() first or load models.")
        
        # Prepare feature vector
        feature_vector = self._prepare_feature_vector(student_features)
        X = pd.DataFrame([feature_vector], columns=self.feature_names)
        
        # Predict
        predicted_domain = self.classification_model.predict(X)[0]
        
        # Get confidence (probability of predicted class)
        probabilities = self.classification_model.predict_proba(X)[0]
        max_prob = probabilities.max()
        
        return predicted_domain, float(max_prob)
    
    def _prepare_feature_vector(self, student_features: Dict) -> Dict:
        """
        Prepare feature vector from student aptitudes.
        
        Args:
            student_features: Dictionary with aptitude scores
            
        Returns:
            Dictionary with all required features
        """
        # Base aptitude features
        features = {
            'aptitude_quant': student_features.get('quant', 0),
            'aptitude_logical': student_features.get('logical', 0),
            'aptitude_verbal': student_features.get('verbal', 0),
            'aptitude_creative': student_features.get('creative', 0),
            'aptitude_technical': student_features.get('technical', 0),
            'aptitude_commerce': student_features.get('commerce', 0)
        }
        
        # Engineered features (same as in training)
        aptitudes = list(features.values())
        features['avg_aptitude'] = np.mean(aptitudes)
        features['max_aptitude'] = np.max(aptitudes)
        features['min_aptitude'] = np.min(aptitudes)
        features['aptitude_range'] = features['max_aptitude'] - features['min_aptitude']
        
        features['tech_score'] = (
            features['aptitude_technical'] * 0.5 +
            features['aptitude_logical'] * 0.3 +
            features['aptitude_quant'] * 0.2
        )
        
        features['business_score'] = (
            features['aptitude_commerce'] * 0.5 +
            features['aptitude_verbal'] * 0.3 +
            features['aptitude_logical'] * 0.2
        )
        
        features['creative_score'] = (
            features['aptitude_creative'] * 0.6 +
            features['aptitude_verbal'] * 0.4
        )
        
        return features
    
    def save_models(self):
        """Save trained models to disk."""
        if not self.is_trained:
            raise ValueError("No trained models to save")
        
        # Save regression model
        reg_path = os.path.join(self.model_dir, 'domain_regression_model.pkl')
        with open(reg_path, 'wb') as f:
            pickle.dump(self.regression_model, f)
        print(f"✓ Saved regression model to {reg_path}")
        
        # Save classification model
        class_path = os.path.join(self.model_dir, 'domain_classification_model.pkl')
        with open(class_path, 'wb') as f:
            pickle.dump(self.classification_model, f)
        print(f"✓ Saved classification model to {class_path}")
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'domain_names': self.domain_names,
            'metrics': self.metrics
        }
        metadata_path = os.path.join(self.model_dir, 'model_metadata.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✓ Saved metadata to {metadata_path}")
    
    def load_models(self):
        """Load trained models from disk."""
        # Load regression model
        reg_path = os.path.join(self.model_dir, 'domain_regression_model.pkl')
        if not os.path.exists(reg_path):
            raise FileNotFoundError(f"Regression model not found: {reg_path}")
        
        with open(reg_path, 'rb') as f:
            self.regression_model = pickle.load(f)
        
        # Load classification model
        class_path = os.path.join(self.model_dir, 'domain_classification_model.pkl')
        if not os.path.exists(class_path):
            raise FileNotFoundError(f"Classification model not found: {class_path}")
        
        with open(class_path, 'rb') as f:
            self.classification_model = pickle.load(f)
        
        # Load metadata
        metadata_path = os.path.join(self.model_dir, 'model_metadata.pkl')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.feature_names = metadata['feature_names']
                self.domain_names = metadata['domain_names']
                self.metrics = metadata['metrics']
        
        self.is_trained = True
        print("✓ Models loaded successfully")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance from regression model.
        
        Returns:
            DataFrame with feature importance scores
        """
        if not self.is_trained:
            raise ValueError("Models not trained")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.regression_model.feature_importances_
        })
        
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        return importance_df


if __name__ == "__main__":
    # Test ML classifier
    from training_data_prep import TrainingDataPreparator
    
    print("=== ML Domain Classifier Test ===\n")
    
    # Prepare training data
    students_csv = "../data/FakeStudents.csv"
    careers_csv = "../data/careers.csv"
    
    preparator = TrainingDataPreparator(students_csv, careers_csv)
    X, y_class, y_reg = preparator.prepare_training_data()
    
    # Train models
    classifier = MLDomainClassifier(model_dir='models')
    classifier.train(X, y_reg, y_class)
    
    # Save models
    classifier.save_models()
    
    # Test prediction
    print("\n" + "="*50)
    print("Testing prediction with sample student:")
    
    sample_student = {
        'quant': 95,
        'logical': 94,
        'verbal': 80,
        'creative': 60,
        'technical': 96,
        'commerce': 50
    }
    
    # Predict domain scores
    domain_scores = classifier.predict_domain_scores(sample_student)
    print("\nDomain Fit Scores:")
    for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {domain}: {score:.1f}")
    
    # Predict primary domain
    primary_domain, confidence = classifier.predict_primary_domain(sample_student)
    print(f"\nPredicted Primary Domain: {primary_domain} (confidence: {confidence:.2%})")
    
    # Feature importance
    print("\n" + "="*50)
    print("Top 5 Most Important Features:")
    importance = classifier.get_feature_importance()
    print(importance.head().to_string(index=False))
