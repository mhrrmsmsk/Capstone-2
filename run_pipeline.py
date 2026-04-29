#!/usr/bin/env python3
"""
Complete end-to-end pipeline script for the Crop Recommendation & Yield Optimization System.
Run this script to train all models and save artifacts.

Usage:
    python run_pipeline.py
"""

import sys
import os


PROJECT_DIR = '/Users/muharremsimsek/Desktop/Capstone 2'
VENV_PYTHON = os.path.join(PROJECT_DIR, '.venv', 'bin', 'python')


def bootstrap_virtual_environment():
    """Re-execute the pipeline with the project virtual environment if needed."""
    current_executable = os.path.abspath(sys.executable)
    venv_executable = os.path.abspath(VENV_PYTHON)

    if current_executable != venv_executable and os.path.exists(venv_executable):
        os.execv(venv_executable, [venv_executable, __file__] + sys.argv[1:])

    if current_executable != venv_executable and not os.path.exists(venv_executable):
        print(
            "[ERROR] Project virtual environment not found. "
            "Run 'python3 setup_streamlit.py' first to create .venv."
        )
        sys.exit(1)


bootstrap_virtual_environment()

sys.path.insert(0, PROJECT_DIR)

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from pathlib import Path

# Import custom modules
from src.preprocessing import CropDataProcessor
from src.train import ModelTrainer
from src.predict import CropPredictor
from src.recommender import IntelligentRecommender
from src.logger import get_logger

logger = get_logger("pipeline")

def main():
    """Run the complete ML pipeline."""
    
    print("\n" + "="*80)
    print("CROP RECOMMENDATION & YIELD OPTIMIZATION SYSTEM")
    print("Complete End-to-End ML Pipeline")
    print("="*80 + "\n")
    
    # ========================================================================
    # STEP 1: LOAD AND EXPLORE DATA
    # ========================================================================
    print("STEP 1: Loading and Exploring Data")
    print("-" * 80)
    
    data_path = '/Users/muharremsimsek/Desktop/Capstone 2/data/Soil_Nutrients.csv'
    processor = CropDataProcessor(data_path)
    df = processor.load_data()
    data_info = processor.explore_data()
    
    print(f"✓ Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")
    print(f"✓ Unique crops: {df['Name'].nunique()}")
    
    # ========================================================================
    # STEP 2: PREPROCESS DATA
    # ========================================================================
    print("\n\nSTEP 2: Preprocessing Data")
    print("-" * 80)
    
    processor.handle_missing_values(strategy='mean')
    print("✓ Missing values handled")
    
    categorical_features, numerical_features = processor.identify_features()
    print(f"✓ Features identified: {len(categorical_features)} categorical, {len(numerical_features)} numerical")
    
    X, y_crop, y_yield = processor.prepare_features_for_training()
    print(f"✓ Features prepared: {X.shape}")
    
    X_processed = processor.encode_and_scale(X, fit=True)
    print(f"✓ Features encoded and scaled: {X_processed.shape}")
    
    processor.save_preprocessor()
    print("✓ Preprocessor saved")
    
    # Split data
    X_train, X_test, y_crop_train, y_crop_test, y_yield_train, y_yield_test = train_test_split(
        X_processed, y_crop, y_yield, 
        test_size=0.2, 
        random_state=42,
        stratify=y_crop
    )
    
    print(f"✓ Data split: Train {X_train.shape}, Test {X_test.shape}")
    
    # ========================================================================
    # STEP 3: TRAIN CLASSIFICATION MODEL
    # ========================================================================
    print("\n\nSTEP 3: Training Crop Classification Model")
    print("-" * 80)
    
    trainer = ModelTrainer()
    
    clf_metrics = trainer.train_crop_classifier(
        X_train, y_crop_train, 
        X_test, y_crop_test,
        model_type='auto'
    )
    
    print(f"✓ Classification Model Trained")
    print(f"  Train Accuracy: {clf_metrics['train_accuracy']:.4f}")
    print(f"  Test Accuracy: {clf_metrics['test_accuracy']:.4f}")
    print(f"  CV Score: {clf_metrics['cv_mean']:.4f} (±{clf_metrics['cv_std']:.4f})")
    
    # ========================================================================
    # STEP 4: TRAIN REGRESSION MODEL
    # ========================================================================
    print("\n\nSTEP 4: Training Yield Prediction Model")
    print("-" * 80)
    
    reg_metrics = trainer.train_yield_regressor(
        X_train, y_yield_train,
        X_test, y_yield_test,
        model_type='auto'
    )
    
    print(f"✓ Regression Model Trained")
    print(f"  Test RMSE: {reg_metrics['test_rmse']:.4f}")
    print(f"  Test MAE: {reg_metrics['test_mae']:.4f}")
    print(f"  Test R²: {reg_metrics['test_r2']:.4f}")
    print(f"  CV R²: {reg_metrics['cv_r2_mean']:.4f} (±{reg_metrics['cv_r2_std']:.4f})")
    
    print("\n✓ Generating feature importance plots...")
    trainer.plot_feature_importance(top_n=15)
    print("✓ Feature importance plots saved")
    
    # ========================================================================
    # STEP 5: BUILD RECOMMENDATION ENGINE
    # ========================================================================
    print("\n\nSTEP 5: Building Intelligent Recommendation Engine")
    print("-" * 80)
    
    recommender = IntelligentRecommender(
        df_train=df,
        X_train_processed=X_processed,
        y_crop=y_crop,
        y_yield=y_yield,
        feature_columns=processor.feature_columns,
        numerical_features=processor.numerical_features,
        categorical_features=processor.categorical_features,
        preprocessor=processor
    )
    
    print("✓ Intelligent recommender initialized with KNN similarity search")
    
    # ========================================================================
    # STEP 6: SAVE ALL MODELS
    # ========================================================================
    print("\n\nSTEP 6: Saving Models and Artifacts")
    print("-" * 80)
    
    trainer.save_models()
    recommender.save_recommender()
    
    # Save metadata
    import json
    from datetime import datetime
    
    metadata = {
        'model_version': '1.0.0',
        'training_date': datetime.now().isoformat(),
        'crop_classifier_accuracy': float(clf_metrics['test_accuracy']),
        'yield_regressor_r2': float(reg_metrics['test_r2']),
        'yield_regressor_rmse': float(reg_metrics['test_rmse']),
        'total_features': len(processor.feature_columns),
        'numerical_features': processor.numerical_features,
        'categorical_features': processor.categorical_features,
        'unique_crops': int(df['Name'].nunique()),
        'crops': sorted(df['Name'].unique())
    }
    
    models_dir = Path('/Users/muharremsimsek/Desktop/Capstone 2/models')
    with open(models_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
    
    print("✓ All models and artifacts saved:")
    print(f"  - Crop Classifier: {models_dir / 'crop_classifier.pkl'}")
    print(f"  - Yield Regressor: {models_dir / 'yield_regressor.pkl'}")
    print(f"  - Scaler: {models_dir / 'scaler.pkl'}")
    print(f"  - Label Encoders: {models_dir / 'label_encoder.pkl'}")
    print(f"  - KNN Model: {models_dir / 'knn_model.pkl'}")
    print(f"  - Metadata: {models_dir / 'metadata.json'}")
    
    # ========================================================================
    # STEP 7: INITIALIZE UNIFIED PREDICTOR
    # ========================================================================
    print("\n\nSTEP 7: Initializing Unified Prediction Engine")
    print("-" * 80)
    
    predictor = CropPredictor(
        crop_classifier=trainer.crop_classifier,
        yield_regressor=trainer.yield_regressor,
        preprocessor=processor,
        recommender=recommender,
        feature_columns=processor.feature_columns,
        numerical_features=processor.numerical_features,
        categorical_features=processor.categorical_features
    )
    
    print("✓ Unified predictor initialized")
    
    # ========================================================================
    # STEP 8: DEMONSTRATION: END-TO-END PREDICTIONS
    # ========================================================================
    print("\n\nSTEP 8: End-to-End Prediction Demonstrations")
    print("-" * 80)
    
    # Demo 1: Minimal Input
    print("\n[DEMO 1] Minimal Input - Only 3 Sensor Values")
    print("─" * 80)
    
    demo1_input = {
        'Temperature': 22,
        'Rainfall': 800,
        'pH': 6.3
    }
    
    print(f"Input: {demo1_input}")
    demo1_result = predictor.predict(demo1_input)
    print(f"\n✓ Recommendations:")
    for i, crop in enumerate(demo1_result['recommended_crops'], 1):
        print(f"  {i}. {crop['name']}: {crop['probability']:.2%}")
    print(f"\nEstimated Yield: {demo1_result['estimated_yield']:.2f}")
    print(f"Missing Features Estimated: {demo1_result['missing_features_count']}")
    
    # Demo 2: Moderate Input
    print("\n\n[DEMO 2] Moderate Input - 8 Environmental & Soil Features")
    print("─" * 80)
    
    demo2_input = {
        'Temperature': 19,
        'Rainfall': 700,
        'pH': 6.5,
        'Nitrogen': 180,
        'Phosphorus': 110,
        'Potassium': 240,
        'Soil_Type': 'Loam',
        'Season': 'Spring'
    }
    
    print(f"Input Features: {len(demo2_input)}")
    demo2_result = predictor.predict(demo2_input)
    print(f"\n✓ Top 3 Recommended Crops:")
    for i, crop in enumerate(demo2_result['recommended_crops'], 1):
        print(f"  {i}. {crop['name']}: {crop['probability']:.2%}")
    print(f"\nEstimated Yield: {demo2_result['estimated_yield']:.2f}")
    
    # Demo 3: Crop Optimization
    print("\n\n[DEMO 3] Crop-Specific Optimization")
    print("─" * 80)
    
    demo3_crop = 'Strawberry'
    demo3_input = {
        'Temperature': 20,
        'Rainfall': 750,
        'pH': 6.5
    }
    
    print(f"Crop: {demo3_crop}")
    print(f"Current Conditions: {demo3_input}")
    
    demo3_result = predictor.predict_for_crop(demo3_crop, demo3_input)
    print(f"\nEstimated Yield: {demo3_result['estimated_yield']:.2f}")
    print(f"\nTop 5 Optimization Suggestions:")
    
    opt_conds = demo3_result['optimized_conditions']
    sorted_conds = sorted(opt_conds.items(), key=lambda x: x[1].get('std', 0), reverse=True)[:5]
    for feat, vals in sorted_conds:
        print(f"  • {feat}: {vals['range']} (recommended: {vals['recommended']})")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n\n" + "="*80)
    print("SYSTEM READY FOR DEPLOYMENT")
    print("="*80)
    
    summary = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    PIPELINE EXECUTION COMPLETE ✓                          ║
╚════════════════════════════════════════════════════════════════════════════╝

MODELS TRAINED:
  ✓ Crop Classification:  {clf_metrics['test_accuracy']:.2%} accuracy
  ✓ Yield Prediction:     R² = {reg_metrics['test_r2']:.4f}

FEATURES:
  • Total Features:       {len(processor.feature_columns)}
  • Categorical:          {len(processor.categorical_features)}
  • Numerical:            {len(processor.numerical_features)}
  • Unique Crops:         {df['Name'].nunique()}

KEY CAPABILITIES:
  ✓ Complete data handling (all 18 features)
  ✓ Partial data handling (intelligent estimation with KNN)
  ✓ Crop recommendations (top 3 with probabilities)
  ✓ Yield prediction (with high accuracy)
  ✓ Condition optimization (ranges for each crop)
  ✓ Batch predictions (multiple inputs at once)

NEXT STEPS:
  1. To run FastAPI server:
     $ cd /Users/muharremsimsek/Desktop/Capstone\\ 2
     $ uvicorn src.api:app --host 0.0.0.0 --port 8000
  
  2. API will be available at:
     http://localhost:8000
     http://localhost:8000/docs (interactive documentation)
  
  3. To use in Python code:
     from src.predict import CropPredictor
     predictor = CropPredictor(...)
     result = predictor.predict({...})

ARTIFACTS LOCATION:
  Models:  /Users/muharremsimsek/Desktop/Capstone 2/models/
  Logs:    /Users/muharremsimsek/Desktop/Capstone 2/logs/
  Plots:   /Users/muharremsimsek/Desktop/Capstone 2/models/plots/

════════════════════════════════════════════════════════════════════════════════
"""
    
    print(summary)
    
    logger.info("Pipeline execution complete ✓")
    print("\n✓ All logs saved to: /Users/muharremsimsek/Desktop/Capstone 2/logs/")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        sys.exit(1)
