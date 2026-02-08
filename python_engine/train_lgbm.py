"""
Train LightGBM Ranking Model
Complete training pipeline for Phase 3 LightGBM ranker.
"""

import os
import sys
from ranking_pair_generator import RankingPairGenerator
from lgbm_ranker import LGBMRankerModel


def train_lgbm_ranker(
    students_csv: str = "../data/FakeStudents.csv",
    careers_csv: str = "../data/careers.csv",
    model_dir: str = "models",
    regenerate_pairs: bool = True
):
    """
    Complete LightGBM ranking model training pipeline.
    
    Args:
        students_csv: Path to student data
        careers_csv: Path to career data
        model_dir: Directory to save models
        regenerate_pairs: Whether to regenerate ranking pairs
    """
    print("="*70)
    print(" "*15 + "PHASE 3: LightGBM RANKING MODEL TRAINING")
    print("="*70)
    print()
    
    # Check if files exist
    if not os.path.exists(students_csv):
        print(f"❌ Error: Student data not found at {students_csv}")
        return False
    
    if not os.path.exists(careers_csv):
        print(f"❌ Error: Career data not found at {careers_csv}")
        return False
    
    try:
        # Step 1: Generate ranking pairs
        pairs_path = "../data/ranking_pairs.csv"
        
        if regenerate_pairs or not os.path.exists(pairs_path):
            print("STEP 1: Generating Ranking Pairs")
            print("-" * 70)
            
            generator = RankingPairGenerator(students_csv, careers_csv)
            generator.load_data()
            pairs_df = generator.generate_pairs()
            generator.save_pairs(pairs_df)
        else:
            print(f"STEP 1: Using existing ranking pairs from {pairs_path}")
            print("-" * 70)
            import pandas as pd
            pairs_df = pd.read_csv(pairs_path)
            print(f"✓ Loaded {len(pairs_df)} pairs")
        
        # Step 2: Train LightGBM model
        print("\n" + "="*70)
        print("STEP 2: Training LightGBM Ranker")
        print("-" * 70)
        
        ranker = LGBMRankerModel(model_dir=model_dir)
        
        # Prepare data
        X_train, y_train, group_train, X_test, y_test, group_test = ranker.prepare_data(pairs_df)
        
        # Train
        ranker.train(X_train, y_train, group_train, X_test, y_test, group_test)
        
        # Step 3: Save model
        print("\n" + "="*70)
        print("STEP 3: Saving Model")
        print("-" * 70)
        
        ranker.save_model()
        
        # Step 4: Display results
        print("\n" + "="*70)
        print("TRAINING COMPLETE!")
        print("="*70)
        
        print("\n📊 Model Performance:")
        print(f"  NDCG@10: {ranker.metrics.get('ndcg@10', 0):.4f}")
        print(f"  MSE: {ranker.metrics.get('mse', 0):.4f}")
        print(f"  Best iteration: {ranker.metrics.get('best_iteration', 0)}")
        print(f"  Test groups: {ranker.metrics.get('n_test_groups', 0)}")
        
        # Feature importance
        print("\n📈 Top 10 Most Important Features:")
        importance = ranker.get_feature_importance()
        for idx, row in importance.head(10).iterrows():
            print(f"  {row['feature']:20s} {row['importance']:10.1f}")
        
        print(f"\n✅ Models saved to: {os.path.abspath(model_dir)}")
        print("\nFiles created:")
        print(f"  ✓ {model_dir}/lgbm_ranker.txt")
        print(f"  ✓ {model_dir}/lgbm_metadata.pkl")
        
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("1. Test the model: python test_lgbm_ranker.py")
        print("2. The recommendation engine can now use LightGBM!")
        print("3. Restart the Flask API: python app.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train LightGBM ranking model')
    parser.add_argument('--students', default='../data/FakeStudents.csv',
                       help='Path to student CSV file')
    parser.add_argument('--careers', default='../data/careers.csv',
                       help='Path to careers CSV file')
    parser.add_argument('--model-dir', default='models',
                       help='Directory to save models')
    parser.add_argument('--no-regenerate', action='store_true',
                       help='Use existing ranking pairs instead of regenerating')
    
    args = parser.parse_args()
    
    success = train_lgbm_ranker(
        students_csv=args.students,
        careers_csv=args.careers,
        model_dir=args.model_dir,
        regenerate_pairs=not args.no_regenerate
    )
    
    sys.exit(0 if success else 1)
