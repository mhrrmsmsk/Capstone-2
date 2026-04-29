"""
Model training module for crop recommendation and yield prediction.
Trains both classification and regression models with performance evaluation.
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
)
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    mean_squared_error, r2_score, mean_absolute_error
)
import matplotlib.pyplot as plt
import seaborn as sns
from .logger import get_logger

logger = get_logger("train")


class ModelTrainer:
    """
    Trains and evaluates machine learning models for crop recommendation and yield prediction.
    """
    
    def __init__(self, models_dir=None):
        """
        Initialize the model trainer.
        
        Args:
            models_dir: Directory to save trained models
        """
        self.models_dir = Path(models_dir) if models_dir else Path(__file__).parent.parent / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        self.crop_classifier = None
        self.yield_regressor = None
        self.feature_importance_clf = None
        self.feature_importance_reg = None
        self.classifier_experiments = []
        self.regressor_experiments = []
        self.training_summary = {}
        self.cv_folds = 3
        
        logger.info(f"ModelTrainer initialized. Models directory: {self.models_dir}")
    
    def _evaluate_classifier_candidate(self, model_name, model, X_train, y_train, X_test, y_test):
        """Fit and score a classifier candidate."""
        model.fit(X_train, y_train)

        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        cv_scores = cross_val_score(model, X_train, y_train, cv=self.cv_folds)

        return {
            'task': 'classification',
            'model_type': model_name,
            'train_accuracy': accuracy_score(y_train, y_pred_train),
            'test_accuracy': accuracy_score(y_test, y_pred_test),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'classification_report': classification_report(y_test, y_pred_test),
            'model': model,
        }

    def _evaluate_regressor_candidate(self, model_name, model, X_train, y_train, X_test, y_test):
        """Fit and score a regressor candidate."""
        model.fit(X_train, y_train)

        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        cv_scores = cross_val_score(model, X_train, y_train, cv=self.cv_folds, scoring='r2')

        return {
            'task': 'regression',
            'model_type': model_name,
            'train_rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
            'train_mae': float(mean_absolute_error(y_train, y_pred_train)),
            'test_mae': float(mean_absolute_error(y_test, y_pred_test)),
            'train_r2': float(r2_score(y_train, y_pred_train)),
            'test_r2': float(r2_score(y_test, y_pred_test)),
            'cv_r2_mean': float(cv_scores.mean()),
            'cv_r2_std': float(cv_scores.std()),
            'model': model,
        }

    def train_crop_classifier(self, X_train, y_train, X_test, y_test, model_type='auto'):
        """
        Train the crop recommendation classifier.
        
        Args:
            X_train, y_train: Training data
            X_test, y_test: Testing data
            model_type: 'auto' to benchmark all candidates, or a specific candidate name
        
        Returns:
            Dictionary with training metrics
        """
        logger.info("Training crop classification model...")

        candidate_models = {
            'RandomForest': RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            ),
            'ExtraTrees': ExtraTreesClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            ),
        }

        model_names = list(candidate_models.keys()) if model_type == 'auto' else [model_type]
        if any(name not in candidate_models for name in model_names):
            raise ValueError(f"Unknown model type(s): {model_names}")
        self.classifier_experiments = []

        for candidate_name in model_names:
            candidate_result = self._evaluate_classifier_candidate(
                candidate_name,
                candidate_models[candidate_name],
                X_train,
                y_train,
                X_test,
                y_test,
            )
            self.classifier_experiments.append(candidate_result)
            logger.info(
                f"Classifier candidate {candidate_name} - Test Accuracy: {candidate_result['test_accuracy']:.4f}, "
                f"CV: {candidate_result['cv_mean']:.4f} (+/- {candidate_result['cv_std']:.4f})"
            )

        self.classifier_experiments.sort(
            key=lambda item: (item['test_accuracy'], item['cv_mean']),
            reverse=True,
        )
        best_result = self.classifier_experiments[0]
        self.crop_classifier = best_result['model']

        self.feature_importance_clf = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.crop_classifier.feature_importances_
        }).sort_values('importance', ascending=False)

        best_result['feature_importance'] = self.feature_importance_clf.to_dict(orient='records')
        logger.info(f"Selected classifier: {best_result['model_type']}")
        logger.info(f"\nTop 10 Most Important Features (Crop Classification):\n{self.feature_importance_clf.head(10)}")

        return best_result
    
    def train_yield_regressor(self, X_train, y_train, X_test, y_test, model_type='auto'):
        """
        Train the yield prediction regressor.
        
        Args:
            X_train, y_train: Training data
            X_test, y_test: Testing data
            model_type: 'auto' to benchmark all candidates, or a specific candidate name
        
        Returns:
            Dictionary with training metrics
        """
        logger.info("Training yield regression model...")
        
        candidate_models = {
            'RandomForest': RandomForestRegressor(
                n_estimators=300,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1
            ),
            'ExtraTrees': ExtraTreesRegressor(
                n_estimators=300,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1
            ),
        }

        model_names = list(candidate_models.keys()) if model_type == 'auto' else [model_type]
        if any(name not in candidate_models for name in model_names):
            raise ValueError(f"Unknown model type(s): {model_names}")
        self.regressor_experiments = []

        for candidate_name in model_names:
            candidate_result = self._evaluate_regressor_candidate(
                candidate_name,
                candidate_models[candidate_name],
                X_train,
                y_train,
                X_test,
                y_test,
            )
            self.regressor_experiments.append(candidate_result)
            logger.info(
                f"Regressor candidate {candidate_name} - Test R²: {candidate_result['test_r2']:.4f}, "
                f"RMSE: {candidate_result['test_rmse']:.4f}, CV: {candidate_result['cv_r2_mean']:.4f} (+/- {candidate_result['cv_r2_std']:.4f})"
            )

        self.regressor_experiments.sort(
            key=lambda item: (item['test_r2'], -item['test_rmse'], item['cv_r2_mean']),
            reverse=True,
        )
        best_result = self.regressor_experiments[0]
        self.yield_regressor = best_result['model']

        self.feature_importance_reg = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.yield_regressor.feature_importances_
        }).sort_values('importance', ascending=False)

        best_result['feature_importance'] = self.feature_importance_reg.to_dict(orient='records')
        logger.info(f"Selected regressor: {best_result['model_type']}")
        logger.info(f"\nTop 10 Most Important Features (Yield Regression):\n{self.feature_importance_reg.head(10)}")

        return best_result
    
    def save_models(self):
        """Save trained models to disk."""
        if self.crop_classifier:
            joblib.dump(self.crop_classifier, self.models_dir / "crop_classifier.pkl")
            logger.info("Crop classifier saved")
        
        if self.yield_regressor:
            joblib.dump(self.yield_regressor, self.models_dir / "yield_regressor.pkl")
            logger.info("Yield regressor saved")
        
        if self.feature_importance_clf is not None:
            self.feature_importance_clf.to_csv(self.models_dir / "feature_importance_crop.csv", index=False)
        
        if self.feature_importance_reg is not None:
            self.feature_importance_reg.to_csv(self.models_dir / "feature_importance_yield.csv", index=False)

        self.save_training_metrics()

    def save_training_metrics(self):
        """Persist model comparison results and final training summary."""
        metrics_dir = self.models_dir / "metrics"
        metrics_dir.mkdir(exist_ok=True)

        def to_jsonable(value):
            if isinstance(value, (np.floating, np.integer)):
                return value.item()
            return value

        summary = {
            'classifier_best_model': self.classifier_experiments[0]['model_type'] if self.classifier_experiments else None,
            'regressor_best_model': self.regressor_experiments[0]['model_type'] if self.regressor_experiments else None,
            'classifier_experiments': [
                {k: to_jsonable(v) for k, v in experiment.items() if k != 'model'}
                for experiment in self.classifier_experiments
            ],
            'regressor_experiments': [
                {k: to_jsonable(v) for k, v in experiment.items() if k != 'model'}
                for experiment in self.regressor_experiments
            ],
        }

        self.training_summary = summary

        with open(metrics_dir / "training_summary.json", "w") as handle:
            json.dump(summary, handle, indent=2)

        classifier_rows = []
        for experiment in self.classifier_experiments:
            classifier_rows.append({
                'task': 'classification',
                'model_type': experiment['model_type'],
                'train_accuracy': to_jsonable(experiment['train_accuracy']),
                'test_accuracy': to_jsonable(experiment['test_accuracy']),
                'cv_mean': to_jsonable(experiment['cv_mean']),
                'cv_std': to_jsonable(experiment['cv_std']),
            })

        regressor_rows = []
        for experiment in self.regressor_experiments:
            regressor_rows.append({
                'task': 'regression',
                'model_type': experiment['model_type'],
                'train_rmse': to_jsonable(experiment['train_rmse']),
                'test_rmse': to_jsonable(experiment['test_rmse']),
                'train_mae': to_jsonable(experiment['train_mae']),
                'test_mae': to_jsonable(experiment['test_mae']),
                'train_r2': to_jsonable(experiment['train_r2']),
                'test_r2': to_jsonable(experiment['test_r2']),
                'cv_r2_mean': to_jsonable(experiment['cv_r2_mean']),
                'cv_r2_std': to_jsonable(experiment['cv_r2_std']),
            })

        pd.DataFrame(classifier_rows).to_csv(metrics_dir / "classifier_experiments.csv", index=False)
        pd.DataFrame(regressor_rows).to_csv(metrics_dir / "regressor_experiments.csv", index=False)
    
    def load_models(self):
        """Load pre-trained models from disk."""
        try:
            self.crop_classifier = joblib.load(self.models_dir / "crop_classifier.pkl")
            logger.info("Crop classifier loaded")
        except FileNotFoundError:
            logger.warning("Crop classifier not found")
        
        try:
            self.yield_regressor = joblib.load(self.models_dir / "yield_regressor.pkl")
            logger.info("Yield regressor loaded")
        except FileNotFoundError:
            logger.warning("Yield regressor not found")
    
    def plot_feature_importance(self, top_n=15, save_dir=None):
        """Plot and save feature importance visualizations."""
        if save_dir is None:
            save_dir = self.models_dir / "plots"
        
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)
        
        # Plot for classifier
        if self.feature_importance_clf is not None:
            plt.figure(figsize=(10, 6))
            top_features = self.feature_importance_clf.head(top_n)
            plt.barh(top_features['feature'], top_features['importance'])
            plt.xlabel('Importance')
            plt.title('Top Features - Crop Classification')
            plt.tight_layout()
            plt.savefig(save_dir / "feature_importance_crop.png", dpi=300, bbox_inches='tight')
            plt.close()
            logger.info("Crop classifier feature importance plot saved")
        
        # Plot for regressor
        if self.feature_importance_reg is not None:
            plt.figure(figsize=(10, 6))
            top_features = self.feature_importance_reg.head(top_n)
            plt.barh(top_features['feature'], top_features['importance'])
            plt.xlabel('Importance')
            plt.title('Top Features - Yield Prediction')
            plt.tight_layout()
            plt.savefig(save_dir / "feature_importance_yield.png", dpi=300, bbox_inches='tight')
            plt.close()
            logger.info("Yield regressor feature importance plot saved")
    
    def get_model_performance_summary(self):
        """Get a summary of model performance."""
        summary = {
            'crop_classifier': self.crop_classifier is not None,
            'yield_regressor': self.yield_regressor is not None
        }
        return summary
