"""
Data preprocessing pipeline for the crop recommendation system.
Handles:
- Loading and exploring data
- Handling missing values
- Encoding categorical variables
- Normalizing numerical features
- Splitting train/test data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path
from .logger import get_logger

logger = get_logger("preprocessing")


class CropDataProcessor:
    """
    Handles all data preprocessing for the crop recommendation system.
    """
    
    def __init__(self, data_path=None):
        """
        Initialize the data processor.
        
        Args:
            data_path: Path to the CSV file. If None, dataset should be passed to load_data()
        """
        self.data_path = data_path
        self.df = None
        self.df_processed = None
        self.preprocessor = None
        self.scaler = None
        self.label_encoder = {}
        self.feature_columns = None
        self.categorical_features = None
        self.numerical_features = None
        
        logger.info("CropDataProcessor initialized")
    
    def load_data(self, data_path=None):
        """Load dataset from CSV."""
        if data_path:
            self.data_path = data_path
        
        if self.data_path is None:
            raise ValueError("data_path must be provided")
        
        logger.info(f"Loading data from {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        logger.info(f"Data shape: {self.df.shape}")
        logger.info(f"Columns: {list(self.df.columns)}")
        
        return self.df
    
    def explore_data(self):
        """Print data exploration information."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        logger.info("=" * 80)
        logger.info("DATA EXPLORATION REPORT")
        logger.info("=" * 80)
        
        logger.info(f"\nDataset Shape: {self.df.shape}")
        logger.info(f"\nMissing Values:\n{self.df.isnull().sum()}")
        logger.info(f"\nData Types:\n{self.df.dtypes}")
        logger.info(f"\nFirst few rows:\n{self.df.head()}")
        logger.info(f"\nBasic Statistics:\n{self.df.describe()}")
        logger.info(f"\nUnique values per column:\n{self.df.nunique()}")
        
        return {
            'shape': self.df.shape,
            'missing': self.df.isnull().sum(),
            'dtypes': self.df.dtypes,
            'unique': self.df.nunique()
        }
    
    def identify_features(self):
        """
        Identify categorical and numerical features.
        """
        # Define features based on dataset structure
        # Target: Name (crop classification), Yield (regression)
        
        categorical_cols = ['Fertility', 'Photoperiod', 'Category_pH', 'Soil_Type', 'Season']
        numerical_cols = ['Temperature', 'Rainfall', 'pH', 'Light_Hours',
                         'Light_Intensity', 'Rh', 'Nitrogen', 'Phosphorus', 'Potassium',
                         'N_Ratio', 'P_Ratio', 'K_Ratio']
        
        self.categorical_features = categorical_cols
        self.numerical_features = numerical_cols
        self.feature_columns = categorical_cols + numerical_cols
        
        logger.info(f"Categorical features: {self.categorical_features}")
        logger.info(f"Numerical features: {self.numerical_features}")
        
        return self.categorical_features, self.numerical_features
    
    def handle_missing_values(self, strategy='mean'):
        """
        Handle missing values using specified strategy.
        
        Args:
            strategy: 'mean', 'median', or 'drop'
        """
        if self.df is None:
            raise ValueError("Data not loaded")
        
        missing_before = self.df.isnull().sum().sum()
        logger.info(f"Missing values before handling: {missing_before}")
        
        if strategy == 'mean':
            # For numerical columns, use mean
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numerical_cols] = self.df[numerical_cols].fillna(self.df[numerical_cols].mean())
            # For categorical, use mode
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if col != 'Name':  # Don't fill target
                    self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
        
        elif strategy == 'median':
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numerical_cols] = self.df[numerical_cols].fillna(self.df[numerical_cols].median())
        
        elif strategy == 'drop':
            self.df = self.df.dropna()
        
        missing_after = self.df.isnull().sum().sum()
        logger.info(f"Missing values after handling: {missing_after}")
        
        return self.df
    
    def prepare_features_for_training(self):
        """
        Prepare features and targets for model training.
        Returns:
            X_features: Feature matrix
            y_crop: Target crop names
            y_yield: Target yield values
        """
        if self.df is None:
            raise ValueError("Data not loaded")
        
        self.identify_features()
        
        # Create feature matrix
        X = self.df[self.feature_columns].copy()
        
        # Create targets
        y_crop = self.df['Name'].copy()  # For classification
        y_yield = self.df['Yield'].copy()  # For regression
        
        logger.info(f"Feature matrix shape: {X.shape}")
        logger.info(f"Crop target shape: {y_crop.shape}")
        logger.info(f"Yield target shape: {y_yield.shape}")
        logger.info(f"Unique crops: {y_crop.nunique()}")
        
        return X, y_crop, y_yield
    
    def encode_and_scale(self, X, fit=True):
        """
        Encode categorical variables and scale numerical features.
        
        Args:
            X: Feature matrix
            fit: If True, fit the preprocessor; if False, transform only
        
        Returns:
            X_processed: Processed feature matrix
        """
        X_copy = X.copy()

        if self.feature_columns is not None:
            missing_columns = [col for col in self.feature_columns if col not in X_copy.columns]
            if missing_columns:
                raise ValueError(f"Missing required features: {missing_columns}")
            X_copy = X_copy.reindex(columns=self.feature_columns)
        
        # Encode categorical variables
        for col in self.categorical_features:
            if col not in self.label_encoder:
                self.label_encoder[col] = LabelEncoder()
                X_copy[col] = self.label_encoder[col].fit_transform(X_copy[col].astype(str))
            else:
                known_classes = set(self.label_encoder[col].classes_)
                fallback_class = self.label_encoder[col].classes_[0]
                cleaned_values = X_copy[col].astype(str).apply(
                    lambda value: value if value in known_classes else fallback_class
                )
                X_copy[col] = self.label_encoder[col].transform(cleaned_values)
        
        # Scale numerical features
        if fit:
            self.scaler = StandardScaler()
            X_copy[self.numerical_features] = self.scaler.fit_transform(
                X_copy[self.numerical_features].to_numpy()
            )
        else:
            X_copy[self.numerical_features] = self.scaler.transform(
                X_copy[self.numerical_features].to_numpy()
            )
        
        logger.info(f"Encoded and scaled feature matrix shape: {X_copy.shape}")
        
        return X_copy
    
    def save_preprocessor(self, save_dir=None):
        """Save preprocessor components for later use."""
        if save_dir is None:
            save_dir = Path(__file__).parent.parent / "models"
        
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)
        
        joblib.dump(self.scaler, save_dir / "scaler.pkl")
        joblib.dump(self.label_encoder, save_dir / "label_encoder.pkl")
        
        logger.info(f"Preprocessor saved to {save_dir}")
    
    def load_preprocessor(self, load_dir=None):
        """Load saved preprocessor components."""
        if load_dir is None:
            load_dir = Path(__file__).parent.parent / "models"
        
        load_dir = Path(load_dir)
        
        self.scaler = joblib.load(load_dir / "scaler.pkl")
        self.label_encoder = joblib.load(load_dir / "label_encoder.pkl")
        
        logger.info(f"Preprocessor loaded from {load_dir}")
    
    def get_data_info(self):
        """Get comprehensive data information."""
        return {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'numerical_features': self.numerical_features,
            'categorical_features': self.categorical_features,
            'missing_values': self.df.isnull().sum().to_dict(),
            'unique_crops': self.df['Name'].nunique(),
            'crop_distribution': self.df['Name'].value_counts().to_dict()
        }
