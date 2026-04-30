"""
Recommendation engine with intelligent missing value estimation.
Uses KNN similarity and cosine similarity to find similar samples and estimate optimal values.
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from pathlib import Path
from .logger import get_logger

logger = get_logger("recommender")


class IntelligentRecommender:
    """
    Provides crop recommendations and optimal condition suggestions.
    Handles both complete and incomplete input data.
    """
    
    def __init__(self, df_train, X_train_processed, y_crop, y_yield, 
                 feature_columns, numerical_features, categorical_features, 
                 preprocessor):
        """
        Initialize the recommender.
        
        Args:
            df_train: Original training dataframe
            X_train_processed: Processed feature matrix (encoded and scaled)
            y_crop: Target crop names
            y_yield: Target yield values
            feature_columns: List of feature column names
            numerical_features: List of numerical feature names
            categorical_features: List of categorical feature names
            preprocessor: CropDataProcessor instance for encoding/scaling
        """
        self.df_train = df_train.copy()
        self.X_train_processed = X_train_processed.copy()
        self.y_crop = y_crop.values if hasattr(y_crop, 'values') else y_crop
        self.y_yield = y_yield.values if hasattr(y_yield, 'values') else y_yield
        
        self.feature_columns = feature_columns
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.preprocessor = preprocessor
        
        # Build KNN model on processed features
        self.knn_model = NearestNeighbors(n_neighbors=10, metric='euclidean')
        self.knn_model.fit(X_train_processed)
        
        logger.info("IntelligentRecommender initialized with KNN model")

    def _summarize_feature_values(self, feature_name, values):
        """Summarize a feature using numeric stats or categorical mode."""
        series = pd.Series(values).dropna()

        if series.empty:
            return None

        if feature_name in self.numerical_features:
            numeric_values = pd.to_numeric(series, errors="coerce").dropna()
            if numeric_values.empty:
                return None

            min_val = float(numeric_values.min())
            max_val = float(numeric_values.max())
            mean_val = float(numeric_values.mean())
            std_val = float(numeric_values.std(ddof=0))

            return {
                'min': min_val,
                'max': max_val,
                'mean': mean_val,
                'std': std_val,
                'range': f"{min_val:.2f}–{max_val:.2f}",
                'recommended': f"{mean_val:.2f} ± {std_val:.2f}"
            }

        mode_values = series.mode()
        if mode_values.empty:
            mode_value = str(series.iloc[0])
        else:
            mode_value = str(mode_values.iloc[0])

        return {
            'min': mode_value,
            'max': mode_value,
            'mean': mode_value,
            'std': 0.0,
            'range': mode_value,
            'recommended': mode_value
        }
    
    def find_similar_samples(self, partial_input_dict, n_neighbors=10, high_yield_only=True):
        """
        Find similar samples based on partial input using KNN similarity.
        
        Args:
            partial_input_dict: Dictionary with available features {feature_name: value}
            n_neighbors: Number of similar samples to retrieve
            high_yield_only: If True, only consider samples with above-median yield
        
        Returns:
            Similar samples with their features and yields
        """
        logger.info(f"Finding similar samples for input: {partial_input_dict}")
        
        # Create a feature vector from partial input
        # Use mean values for missing features from training data
        feature_vector = {}
        for feat in self.feature_columns:
            if feat in partial_input_dict:
                feature_vector[feat] = partial_input_dict[feat]
            else:
                # Use median for numerical features, mode for categorical
                if feat in self.numerical_features:
                    feature_vector[feat] = self.df_train[feat].median()
                else:
                    feature_vector[feat] = self.df_train[feat].mode()[0] if len(self.df_train[feat].mode()) > 0 else self.df_train[feat].iloc[0]
        
        # Encode and scale the feature vector
        input_df = pd.DataFrame([feature_vector])
        input_processed = self.preprocessor.encode_and_scale(input_df, fit=False)
        
        # Find nearest neighbors
        distances, indices = self.knn_model.kneighbors(input_processed, n_neighbors=n_neighbors)
        
        # Get similar samples
        similar_samples = []
        for idx in indices[0]:
            sample = {
                'features': self.df_train.iloc[idx][self.feature_columns].to_dict(),
                'crop': self.y_crop[idx],
                'yield': self.y_yield[idx]
            }
            similar_samples.append(sample)
        
        # Filter by high yield if requested
        if high_yield_only:
            median_yield = np.median(self.y_yield)
            similar_samples = [s for s in similar_samples if s['yield'] >= median_yield]
        
        logger.info(f"Found {len(similar_samples)} similar high-yield samples")
        
        return similar_samples
    
    def estimate_missing_values(self, partial_input_dict, n_neighbors=10):
        """
        Estimate optimal values for missing features using similar high-yield samples.
        
        Args:
            partial_input_dict: Dictionary with available features
            n_neighbors: Number of similar samples to use
        
        Returns:
            Dictionary with estimated optimal ranges {feature_name: (min, max, mean, std)}
        """
        logger.info("Estimating optimal values for missing features...")
        
        similar_samples = self.find_similar_samples(partial_input_dict, n_neighbors, high_yield_only=True)
        
        if not similar_samples:
            logger.warning("No high-yield similar samples found, using general median values")
            similar_samples = self.find_similar_samples(partial_input_dict, n_neighbors, high_yield_only=False)
        
        estimated_values = {}
        
        for feat in self.feature_columns:
            if feat not in partial_input_dict:  # Only estimate missing features
                values = [s['features'][feat] for s in similar_samples if feat in s['features']]
                
                summary = self._summarize_feature_values(feat, values)
                if summary is not None:
                    estimated_values[feat] = summary
        
        logger.info(f"Estimated values for {len(estimated_values)} missing features")
        
        return estimated_values
    
    def recommend_crops(self, partial_input_dict, crop_classifier, n_recommendations=3):
        """
        Recommend top crops based on partial input.
        Uses similar samples to fill missing values, then predicts with classifier.
        
        Args:
            partial_input_dict: Dictionary with available features
            crop_classifier: Trained crop classifier model
            n_recommendations: Number of top recommendations to return
        
        Returns:
            List of recommended crops with probabilities
        """
        logger.info(f"Recommending crops for input: {list(partial_input_dict.keys())}")
        
        # Build a complete feature vector by filling missing features with
        # training-data medians/modes (same logic as find_similar_samples)
        feature_vector = {}
        for feat in self.feature_columns:
            if feat in partial_input_dict:
                feature_vector[feat] = partial_input_dict[feat]
            else:
                if feat in self.numerical_features:
                    feature_vector[feat] = self.df_train[feat].median()
                else:
                    modes = self.df_train[feat].mode()
                    feature_vector[feat] = modes.iloc[0] if len(modes) > 0 else self.df_train[feat].iloc[0]
        
        # Encode and scale the completed feature vector
        input_df = pd.DataFrame([feature_vector])
        input_processed = self.preprocessor.encode_and_scale(input_df, fit=False)
        
        # Use the actual classifier to get real probabilities
        crop_probs = crop_classifier.predict_proba(input_processed)[0]
        crop_names = crop_classifier.classes_
        
        # Build sorted recommendation list
        crop_recommendations = []
        for name, prob in sorted(zip(crop_names, crop_probs), key=lambda x: x[1], reverse=True)[:n_recommendations]:
            crop_recommendations.append({
                'name': str(name),
                'probability': round(float(prob), 4),
            })
        
        logger.info(f"Top {n_recommendations} recommendations: {[c['name'] for c in crop_recommendations]}")
        
        return crop_recommendations
    
    def predict_yield_for_crop(self, crop_name, partial_input_dict, yield_regressor):
        """
        Predict yield for a specific crop with partial input.
        
        Args:
            crop_name: Target crop name
            partial_input_dict: Dictionary with available features
            yield_regressor: Trained yield regressor model
        
        Returns:
            Predicted yield value
        """
        logger.info(f"Predicting yield for crop '{crop_name}'")
        
        # Find similar samples for this specific crop
        similar_samples = [s for s in self.find_similar_samples(partial_input_dict, n_neighbors=50)
                          if s['crop'] == crop_name]
        
        if not similar_samples:
            logger.warning(f"No similar samples found for crop '{crop_name}', using training data median")
            median_yield = np.median(self.y_yield)
            return float(median_yield)
        
        # Use mean yield of similar samples as estimate
        predicted_yield = float(np.mean([s['yield'] for s in similar_samples]))
        
        logger.info(f"Predicted yield: {predicted_yield:.2f}")
        
        return predicted_yield
    
    def get_optimization_recommendations(self, crop_name, n_samples=20):
        """
        Get optimization recommendations for a specific crop.
        Returns optimal ranges for all features based on high-yield samples of that crop.
        
        Args:
            crop_name: Target crop name
            n_samples: Number of high-yield samples to analyze
        
        Returns:
            Dictionary with optimal ranges for each feature
        """
        logger.info(f"Getting optimization recommendations for crop '{crop_name}'")
        
        # Filter for this crop
        crop_mask = (self.y_crop == crop_name)
        crop_indices = np.where(crop_mask)[0]
        
        if len(crop_indices) == 0:
            logger.warning(f"No samples found for crop '{crop_name}'")
            return {}
        
        # Get high-yield samples
        crop_yields = self.y_yield[crop_mask]
        yield_threshold = np.percentile(crop_yields, 75)  # Top 25% yield
        
        high_yield_indices = crop_indices[self.y_yield[crop_indices] >= yield_threshold]
        
        if len(high_yield_indices) == 0:
            high_yield_indices = crop_indices[:n_samples]
        
        # Extract features from high-yield samples
        high_yield_features = self.df_train.iloc[high_yield_indices][self.feature_columns]
        
        # Calculate ranges
        optimized_conditions = {}
        for feat in self.feature_columns:
            summary = self._summarize_feature_values(feat, high_yield_features[feat])
            if summary is not None:
                optimized_conditions[feat] = summary
        
        logger.info(f"Generated optimization recommendations for {len(optimized_conditions)} features")
        
        return optimized_conditions
    
    def save_recommender(self, save_dir=None):
        """Save recommender state."""
        if save_dir is None:
            save_dir = Path(__file__).parent.parent / "models"
        
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)
        
        joblib.dump(self.knn_model, save_dir / "knn_model.pkl")
        logger.info("Recommender KNN model saved")
    
    def load_recommender(self, load_dir=None):
        """Load recommender state."""
        if load_dir is None:
            load_dir = Path(__file__).parent.parent / "models"
        
        load_dir = Path(load_dir)
        
        self.knn_model = joblib.load(load_dir / "knn_model.pkl")
        logger.info("Recommender KNN model loaded")
