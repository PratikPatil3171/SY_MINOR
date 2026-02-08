"""
Training Data Preparation Module
Prepares student data for ML model training.
Processes FakeStudents.csv and creates domain-labeled training data.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from domain_mapper import DomainMapper


class TrainingDataPreparator:
    """Prepares training data from student records."""
    
    APTITUDE_FEATURES = [
        'aptitude_quant',
        'aptitude_logical',
        'aptitude_verbal',
        'aptitude_creative',
        'aptitude_technical',
        'aptitude_commerce'
    ]
    
    def __init__(self, students_csv_path: str, careers_csv_path: str):
        """
        Initialize training data preparator.
        
        Args:
            students_csv_path: Path to FakeStudents.csv
            careers_csv_path: Path to careers.csv
        """
        self.students_csv_path = students_csv_path
        self.careers_csv_path = careers_csv_path
        self.domain_mapper = DomainMapper()
        
        # Load data
        self.students_df = None
        self.careers_df = None
        self.training_data = None
        
    def load_data(self):
        """Load student and career data."""
        print("Loading data...")
        
        # Load students
        self.students_df = pd.read_csv(self.students_csv_path)
        print(f"✓ Loaded {len(self.students_df)} student records")
        
        # Load careers
        self.careers_df = pd.read_csv(self.careers_csv_path)
        print(f"✓ Loaded {len(self.careers_df)} careers")
        
        # Add domain labels to careers
        self.careers_df = self.domain_mapper.create_domain_labels(self.careers_df)
        
    def prepare_features(self) -> pd.DataFrame:
        """
        Extract and prepare features from student data.
        
        Returns:
            DataFrame with prepared features
        """
        print("\nPreparing features...")
        
        # Select relevant columns
        feature_df = self.students_df.copy()
        
        # Ensure all aptitude features exist
        for feature in self.APTITUDE_FEATURES:
            if feature not in feature_df.columns:
                feature_df[feature] = 0
        
        # Create additional engineered features
        feature_df['avg_aptitude'] = feature_df[self.APTITUDE_FEATURES].mean(axis=1)
        feature_df['max_aptitude'] = feature_df[self.APTITUDE_FEATURES].max(axis=1)
        feature_df['min_aptitude'] = feature_df[self.APTITUDE_FEATURES].min(axis=1)
        feature_df['aptitude_range'] = feature_df['max_aptitude'] - feature_df['min_aptitude']
        
        # Technical vs non-technical
        feature_df['tech_score'] = (
            feature_df['aptitude_technical'] * 0.5 +
            feature_df['aptitude_logical'] * 0.3 +
            feature_df['aptitude_quant'] * 0.2
        )
        
        # Business score
        feature_df['business_score'] = (
            feature_df['aptitude_commerce'] * 0.5 +
            feature_df['aptitude_verbal'] * 0.3 +
            feature_df['aptitude_logical'] * 0.2
        )
        
        # Creative score
        feature_df['creative_score'] = (
            feature_df['aptitude_creative'] * 0.6 +
            feature_df['aptitude_verbal'] * 0.4
        )
        
        print(f"✓ Created {len(feature_df.columns)} features")
        
        return feature_df
    
    def create_domain_labels(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create domain labels from best career.
        
        Args:
            feature_df: DataFrame with student features
            
        Returns:
            DataFrame with domain labels
        """
        print("Creating domain labels...")
        
        labeled_df = feature_df.copy()
        
        # Map best career to domain
        career_to_domain = {
            row['career_id']: row['domain']
            for _, row in self.careers_df.iterrows()
        }
        
        labeled_df['target_domain'] = labeled_df['best_career_id'].map(career_to_domain)
        
        # Handle missing mappings
        labeled_df['target_domain'].fillna('business', inplace=True)
        
        print(f"✓ Created domain labels")
        print(f"  Domain distribution:")
        for domain, count in labeled_df['target_domain'].value_counts().items():
            print(f"    {domain}: {count}")
        
        return labeled_df
    
    def create_domain_fit_scores(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create domain fit scores for multi-output regression.
        
        Args:
            feature_df: DataFrame with features and target domain
            
        Returns:
            DataFrame with domain fit scores (0-100 for each domain)
        """
        print("\nCreating domain fit scores...")
        
        scored_df = feature_df.copy()
        
        # For each domain, calculate a fit score based on aptitudes
        for domain in self.domain_mapper.get_all_domains():
            feature_weights = self.domain_mapper.get_domain_features(domain)
            
            # Calculate weighted score
            domain_score = 0
            for feature, weight in feature_weights.items():
                if feature in scored_df.columns:
                    domain_score += scored_df[feature] * weight
                else:
                    # Handle missing features (like aptitude_commerce for science students)
                    domain_score += 50 * weight  # Use neutral score
            
            # Boost score if this is the target domain
            is_target = (scored_df['target_domain'] == domain).astype(int)
            domain_score = domain_score + (is_target * 15)  # Add bonus for actual match
            
            # Clip to 0-100 range
            scored_df[f'{domain}_fit'] = np.clip(domain_score, 0, 100)
        
        print(f"✓ Created fit scores for {len(self.domain_mapper.get_all_domains())} domains")
        
        return scored_df
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Complete training data preparation pipeline.
        
        Returns:
            Tuple of (X_features, y_classification, y_regression)
        """
        print("=== Training Data Preparation ===\n")
        
        # Load data
        self.load_data()
        
        # Prepare features
        feature_df = self.prepare_features()
        
        # Create domain labels
        labeled_df = self.create_domain_labels(feature_df)
        
        # Create domain fit scores
        scored_df = self.create_domain_fit_scores(labeled_df)
        
        # Prepare X (features)
        feature_cols = (
            self.APTITUDE_FEATURES +
            ['avg_aptitude', 'max_aptitude', 'min_aptitude', 'aptitude_range',
             'tech_score', 'business_score', 'creative_score']
        )
        X = scored_df[feature_cols].fillna(50)  # Fill missing with neutral score
        
        # Prepare y_classification (target domain)
        y_classification = scored_df['target_domain']
        
        # Prepare y_regression (domain fit scores)
        domain_fit_cols = [f'{domain}_fit' for domain in self.domain_mapper.get_all_domains()]
        y_regression = scored_df[domain_fit_cols]
        
        print(f"\n✅ Training data prepared!")
        print(f"   X shape: {X.shape}")
        print(f"   y_classification shape: {y_classification.shape}")
        print(f"   y_regression shape: {y_regression.shape}")
        
        self.training_data = {
            'X': X,
            'y_classification': y_classification,
            'y_regression': y_regression,
            'feature_names': feature_cols,
            'domain_names': self.domain_mapper.get_all_domains()
        }
        
        return X, y_classification, y_regression
    
    def save_training_data(self, output_dir: str = 'data'):
        """
        Save prepared training data to CSV files.
        
        Args:
            output_dir: Directory to save data
        """
        if self.training_data is None:
            raise ValueError("Must call prepare_training_data() first")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save features
        X_path = os.path.join(output_dir, 'training_features.csv')
        self.training_data['X'].to_csv(X_path, index=False)
        print(f"✓ Saved features to {X_path}")
        
        # Save classification targets
        y_class_path = os.path.join(output_dir, 'training_labels_classification.csv')
        self.training_data['y_classification'].to_csv(y_class_path, index=False, header=['target_domain'])
        print(f"✓ Saved classification labels to {y_class_path}")
        
        # Save regression targets
        y_reg_path = os.path.join(output_dir, 'training_labels_regression.csv')
        self.training_data['y_regression'].to_csv(y_reg_path, index=False)
        print(f"✓ Saved regression labels to {y_reg_path}")
    
    def get_feature_statistics(self) -> Dict:
        """Get statistics about prepared features."""
        if self.training_data is None:
            raise ValueError("Must call prepare_training_data() first")
        
        stats = {
            'n_samples': len(self.training_data['X']),
            'n_features': len(self.training_data['feature_names']),
            'n_domains': len(self.training_data['domain_names']),
            'feature_names': self.training_data['feature_names'],
            'domain_names': self.training_data['domain_names'],
            'class_distribution': self.training_data['y_classification'].value_counts().to_dict()
        }
        
        return stats


if __name__ == "__main__":
    # Test training data preparation
    import sys
    
    # Use provided CSV files
    students_csv = "../data/FakeStudents.csv"  # Adjust path as needed
    careers_csv = "../data/careers.csv"
    
    # Check if files exist
    if not os.path.exists(students_csv):
        print(f"❌ Students CSV not found: {students_csv}")
        sys.exit(1)
    
    if not os.path.exists(careers_csv):
        print(f"❌ Careers CSV not found: {careers_csv}")
        sys.exit(1)
    
    # Prepare training data
    preparator = TrainingDataPreparator(students_csv, careers_csv)
    X, y_class, y_reg = preparator.prepare_training_data()
    
    print("\n" + "="*50)
    print("Sample data:")
    print("\nFirst 3 rows of X:")
    print(X.head(3))
    
    print("\nFirst 3 classification labels:")
    print(y_class.head(3))
    
    print("\nFirst 3 regression targets:")
    print(y_reg.head(3))
    
    # Save data
    preparator.save_training_data('data')
    
    # Show statistics
    print("\n" + "="*50)
    print("Statistics:")
    stats = preparator.get_feature_statistics()
    for key, value in stats.items():
        if key not in ['feature_names', 'domain_names']:
            print(f"  {key}: {value}")
