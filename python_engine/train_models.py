"""
Model Training Script
Trains ML models for Phase 2 aptitude scoring.
Run this script to train models on FakeStudents.csv data.
"""

import os
import sys
from training_data_prep import TrainingDataPreparator
from ml_domain_classifier import MLDomainClassifier


def train_models(
    students_csv: str = "../data/FakeStudents.csv",
    careers_csv: str = "../data/careers.csv",
    model_dir: str = "models",
    n_estimators: int = 100,
    max_depth: int = 10
):
    """
    Complete ML model training pipeline.
    
    Args:
        students_csv: Path to student training data
        careers_csv: Path to careers data
        model_dir: Directory to save trained models
        n_estimators: Number of trees in RandomForest
        max_depth: Max depth of trees
    """
    print("="*60)
    print("PHASE 2: ML MODEL TRAINING")
    print("="*60)
    print()
    
    # Check if files exist
    if not os.path.exists(students_csv):
        print(f"❌ Error: Student data not found at {students_csv}")
        print("   Please ensure FakeStudents.csv is in the data/ directory")
        return False
    
    if not os.path.exists(careers_csv):
        print(f"❌ Error: Career data not found at {careers_csv}")
        print("   Please ensure careers.csv is in the data/ directory")
        return False
    
    try:
        # Step 1: Prepare training data
        print("STEP 1: Preparing Training Data")
        print("-" * 60)
        preparator = TrainingDataPreparator(students_csv, careers_csv)
        X, y_classification, y_regression = preparator.prepare_training_data()
        
        # Save training data for reference
        preparator.save_training_data('data')
        
        # Step 2: Train ML models
        print("\n" + "="*60)
        print("STEP 2: Training ML Models")
        print("-" * 60)
        classifier = MLDomainClassifier(model_dir=model_dir)
        classifier.train(X, y_regression, y_classification)
        
        # Step 3: Save models
        print("\n" + "="*60)
        print("STEP 3: Saving Models")
        print("-" * 60)
        classifier.save_models()
        
        # Step 4: Display results
        print("\n" + "="*60)
        print("TRAINING COMPLETE!")
        print("="*60)
        
        print("\n📊 Model Performance:")
        print("\nRegression Model (Domain Fit Scores):")
        reg_metrics = classifier.metrics['regression']
        print(f"  Overall R² Score: {reg_metrics['overall_r2']:.3f}")
        print(f"  Overall MSE: {reg_metrics['overall_mse']:.2f}")
        print(f"  Training samples: {reg_metrics['train_size']}")
        print(f"  Test samples: {reg_metrics['test_size']}")
        
        print("\n  Per-Domain Performance:")
        for domain, metrics in reg_metrics['domain_metrics'].items():
            print(f"    {domain:12s} - R²: {metrics['r2']:5.3f}, MSE: {metrics['mse']:6.2f}")
        
        print("\nClassification Model (Primary Domain):")
        class_metrics = classifier.metrics['classification']
        print(f"  Accuracy: {class_metrics['accuracy']:.3f}")
        print(f"  Cross-validation: {class_metrics['cv_mean']:.3f} (±{class_metrics['cv_std']:.3f})")
        print(f"  Training samples: {class_metrics['train_size']}")
        print(f"  Test samples: {class_metrics['test_size']}")
        
        # Feature importance
        print("\n📈 Top 10 Most Important Features:")
        importance = classifier.get_feature_importance()
        for idx, row in importance.head(10).iterrows():
            print(f"  {row['feature']:20s} {row['importance']:.4f}")
        
        print("\n✅ Models saved to:", os.path.abspath(model_dir))
        print("\nFiles created:")
        print(f"  ✓ {model_dir}/domain_regression_model.pkl")
        print(f"  ✓ {model_dir}/domain_classification_model.pkl")
        print(f"  ✓ {model_dir}/model_metadata.pkl")
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Test the models: python test_ml_models.py")
        print("2. The recommendation engine will now use ML predictions!")
        print("3. Restart the Flask API: python app.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def retrain_models():
    """Quick retrain with default parameters."""
    return train_models()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train ML models for career recommendation')
    parser.add_argument('--students', default='../data/FakeStudents.csv', 
                       help='Path to student CSV file')
    parser.add_argument('--careers', default='../data/careers.csv',
                       help='Path to careers CSV file')
    parser.add_argument('--model-dir', default='models',
                       help='Directory to save models')
    parser.add_argument('--n-estimators', type=int, default=100,
                       help='Number of trees in RandomForest')
    parser.add_argument('--max-depth', type=int, default=10,
                       help='Maximum depth of trees')
    
    args = parser.parse_args()
    
    success = train_models(
        students_csv=args.students,
        careers_csv=args.careers,
        model_dir=args.model_dir,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    
    sys.exit(0 if success else 1)
