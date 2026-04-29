"""
Prediction module for the crop recommendation system.
Handles making predictions and generating complete recommendations.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
from .logger import get_logger

logger = get_logger("predict")


class CropPredictor:
    """
    Makes predictions using trained models and generates complete recommendations.
    """
    
    def __init__(self, crop_classifier, yield_regressor, preprocessor, 
                 recommender, feature_columns, numerical_features, categorical_features):
        """
        Initialize the predictor.
        
        Args:
            crop_classifier: Trained classification model
            yield_regressor: Trained regression model
            preprocessor: CropDataProcessor instance
            recommender: IntelligentRecommender instance
            feature_columns: List of all features
            numerical_features: List of numerical features
            categorical_features: List of categorical features
        """
        self.crop_classifier = crop_classifier
        self.yield_regressor = yield_regressor
        self.preprocessor = preprocessor
        self.recommender = recommender
        
        self.feature_columns = feature_columns
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        
        logger.info("CropPredictor initialized")
    
    def predict_from_complete_data(self, input_dict):
        """
        Make predictions when complete feature data is provided.
        
        Args:
            input_dict: Dictionary with all features {feature_name: value}
        
        Returns:
            Complete prediction result
        """
        logger.info("Making prediction from complete data")
        
        # Create dataframe
        input_df = pd.DataFrame([input_dict]).reindex(columns=self.feature_columns)
        
        # Encode and scale
        X_processed = self.preprocessor.encode_and_scale(input_df, fit=False)
        
        # Get crop recommendations
        crop_probs = self.crop_classifier.predict_proba(X_processed)[0]
        crop_names = self.crop_classifier.classes_
        
        top_crops = []
        for name, prob in sorted(zip(crop_names, crop_probs), key=lambda x: x[1], reverse=True)[:3]:
            top_crops.append({
                'name': str(name),
                'probability': float(prob)
            })
        
        # Predict yield
        predicted_yield = float(self.yield_regressor.predict(X_processed)[0])
        
        # Get optimization recommendations for top crop
        top_crop_name = top_crops[0]['name']
        optimized_conditions = self.recommender.get_optimization_recommendations(top_crop_name)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'input_type': 'complete',
            'recommended_crops': top_crops,
            'estimated_yield': predicted_yield,
            'optimized_conditions': optimized_conditions,
            'explanation': f"Prediction based on complete input data. Top recommended crop: {top_crop_name}"
        }
        
        logger.info(f"Prediction complete. Top crop: {top_crop_name}, Yield: {predicted_yield:.2f}")
        
        return result
    
    def predict_from_partial_data(self, partial_input_dict):
        """
        Make predictions when partial feature data is provided.
        Uses intelligent estimation to fill missing values.
        
        Args:
            partial_input_dict: Dictionary with available features
        
        Returns:
            Complete prediction result with estimated values
        """
        logger.info(f"Making prediction from partial data: {list(partial_input_dict.keys())}")
        
        # Get crop recommendations
        recommended_crops = self.recommender.recommend_crops(
            partial_input_dict,
            self.crop_classifier,
            n_recommendations=3
        )
        
        # Estimate missing values
        estimated_values = self.recommender.estimate_missing_values(
            partial_input_dict,
            n_neighbors=10
        )
        
        # Predict yield for top crop
        if recommended_crops:
            top_crop = recommended_crops[0]['name']
            predicted_yield = self.recommender.predict_yield_for_crop(
                top_crop,
                partial_input_dict,
                self.yield_regressor
            )
        else:
            predicted_yield = 0.0
            top_crop = "Unknown"
        
        # Get optimization recommendations
        optimized_conditions = self.recommender.get_optimization_recommendations(top_crop)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'input_type': 'partial',
            'input_features': partial_input_dict,
            'missing_features_count': len(estimated_values),
            'recommended_crops': recommended_crops,
            'estimated_yield': predicted_yield,
            'estimated_missing_values': estimated_values,
            'optimized_conditions': optimized_conditions,
            'explanation': f"Prediction based on partial input ({len(partial_input_dict)} features provided). "
                          f"Missing values estimated using similarity to high-yield samples. "
                          f"Top recommended crop: {top_crop}"
        }
        
        logger.info(f"Partial prediction complete. Top crop: {top_crop}, Yield: {predicted_yield:.2f}")
        logger.info(f"Estimated {len(estimated_values)} missing features")
        
        return result
    
    def predict(self, input_dict):
        """
        Auto-detect if input is complete or partial and make appropriate prediction.
        
        Args:
            input_dict: Dictionary with features
        
        Returns:
            Complete prediction result
        """
        missing_features = [f for f in self.feature_columns if f not in input_dict]
        
        if len(missing_features) == 0:
            logger.info("Input is complete")
            return self.predict_from_complete_data(input_dict)
        else:
            logger.info(f"Input is partial ({len(missing_features)} missing features)")
            return self.predict_from_partial_data(input_dict)
    
    def predict_for_crop(self, crop_name, input_dict):
        """
        Make yield prediction for a specific crop.
        
        Args:
            crop_name: Target crop name
            input_dict: Dictionary with available features
        
        Returns:
            Prediction result for specific crop
        """
        logger.info(f"Making yield prediction for crop '{crop_name}'")
        
        # Estimate missing values
        estimated_values = self.recommender.estimate_missing_values(input_dict, n_neighbors=10)
        
        # Predict yield
        predicted_yield = self.recommender.predict_yield_for_crop(
            crop_name,
            input_dict,
            self.yield_regressor
        )
        
        # Get optimization recommendations
        optimized_conditions = self.recommender.get_optimization_recommendations(crop_name)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'crop_name': crop_name,
            'input_features': input_dict,
            'estimated_yield': predicted_yield,
            'estimated_missing_values': estimated_values,
            'optimized_conditions': optimized_conditions,
            'explanation': f"Yield optimization for {crop_name}. "
                          f"Recommendations based on similar high-yield samples."
        }
        
        return result
    
    def batch_predict(self, input_list):
        """
        Make predictions for multiple inputs.
        
        Args:
            input_list: List of input dictionaries
        
        Returns:
            List of prediction results
        """
        logger.info(f"Making batch predictions for {len(input_list)} inputs")
        
        results = []
        for i, input_dict in enumerate(input_list):
            logger.info(f"Processing input {i+1}/{len(input_list)}")
            result = self.predict(input_dict)
            results.append(result)
        
        logger.info(f"Batch prediction complete")
        
        return results
    
    def get_feature_importance(self):
        """
        Get feature importance from both models.
        
        Returns:
            Dictionary with feature importance scores
        """
        importance_dict = {}
        
        if self.crop_classifier and hasattr(self.crop_classifier, 'feature_importances_'):
            for feat, imp in zip(self.feature_columns, self.crop_classifier.feature_importances_):
                importance_dict[f"{feat}_classifier"] = float(imp)
        
        if self.yield_regressor and hasattr(self.yield_regressor, 'feature_importances_'):
            for feat, imp in zip(self.feature_columns, self.yield_regressor.feature_importances_):
                importance_dict[f"{feat}_regressor"] = float(imp)
        
        return importance_dict
    
    def validate_input(self, input_dict):
        """
        Validate input features.
        
        Args:
            input_dict: Dictionary with features
        
        Returns:
            Validation result with details
        """
        missing = [f for f in self.feature_columns if f not in input_dict]
        invalid = [f for f in input_dict if f not in self.feature_columns]
        
        result = {
            'valid': len(invalid) == 0,
            'total_features': len(self.feature_columns),
            'provided_features': len(input_dict),
            'missing_features': missing,
            'invalid_features': invalid,
            'coverage': round(len(input_dict) / len(self.feature_columns) * 100, 2)
        }
        
        if result['valid']:
            logger.info(f"Input validation passed ({result['coverage']}% coverage)")
        else:
            logger.warning(f"Input validation failed. Invalid features: {invalid}")
        
        return result
