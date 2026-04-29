"""
Smoke tests for the Crop Recommendation & Yield Optimization System.

These tests verify that core modules can be imported and basic
functionality works without requiring trained models.
"""

import pytest
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------

class TestImports:
    """Verify that all public modules can be imported."""

    def test_import_preprocessing(self):
        from src.preprocessing import CropDataProcessor
        assert CropDataProcessor is not None

    def test_import_train(self):
        from src.train import ModelTrainer
        assert ModelTrainer is not None

    def test_import_predict(self):
        from src.predict import CropPredictor
        assert CropPredictor is not None

    def test_import_recommender(self):
        from src.recommender import IntelligentRecommender
        assert IntelligentRecommender is not None

    def test_import_logger(self):
        from src.logger import get_logger
        assert get_logger is not None

    def test_import_api(self):
        from src.api import app
        assert app is not None

    def test_import_package(self):
        import src
        assert src.__version__ == "1.0.0"


# ---------------------------------------------------------------------------
# Data loading tests
# ---------------------------------------------------------------------------

class TestDataLoading:
    """Verify that the dataset can be loaded and has expected shape."""

    DATA_PATH = PROJECT_ROOT / "data" / "Soil_Nutrients.csv"

    @pytest.mark.skipif(
        not DATA_PATH.exists(),
        reason="Dataset not available (gitignored or not cloned with data)"
    )
    def test_data_file_exists(self):
        assert self.DATA_PATH.exists()

    @pytest.mark.skipif(
        not DATA_PATH.exists(),
        reason="Dataset not available"
    )
    def test_data_loads(self):
        from src.preprocessing import CropDataProcessor
        processor = CropDataProcessor(str(self.DATA_PATH))
        df = processor.load_data()
        assert df is not None
        assert df.shape[0] > 0
        assert df.shape[1] > 0

    @pytest.mark.skipif(
        not DATA_PATH.exists(),
        reason="Dataset not available"
    )
    def test_data_has_expected_columns(self):
        from src.preprocessing import CropDataProcessor
        processor = CropDataProcessor(str(self.DATA_PATH))
        df = processor.load_data()
        assert "Name" in df.columns
        assert "Yield" in df.columns


# ---------------------------------------------------------------------------
# Preprocessing tests
# ---------------------------------------------------------------------------

class TestPreprocessing:
    """Verify preprocessing pipeline works on sample data."""

    DATA_PATH = PROJECT_ROOT / "data" / "Soil_Nutrients.csv"

    @pytest.mark.skipif(
        not DATA_PATH.exists(),
        reason="Dataset not available"
    )
    def test_feature_identification(self):
        from src.preprocessing import CropDataProcessor
        processor = CropDataProcessor(str(self.DATA_PATH))
        processor.load_data()
        processor.handle_missing_values(strategy="mean")
        cat_features, num_features = processor.identify_features()
        assert len(cat_features) > 0
        assert len(num_features) > 0

    @pytest.mark.skipif(
        not DATA_PATH.exists(),
        reason="Dataset not available"
    )
    def test_prepare_features(self):
        from src.preprocessing import CropDataProcessor
        processor = CropDataProcessor(str(self.DATA_PATH))
        processor.load_data()
        processor.handle_missing_values(strategy="mean")
        processor.identify_features()
        X, y_crop, y_yield = processor.prepare_features_for_training()
        assert X.shape[0] > 0


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

class TestAPI:
    """Verify FastAPI app can be instantiated and has expected routes."""

    def test_app_creation(self):
        from src.api import app
        assert app.title == "Crop Recommendation & Yield Optimization API"

    def test_health_endpoint_exists(self):
        from src.api import app
        routes = [route.path for route in app.routes]
        assert "/health" in routes

    def test_predict_endpoint_exists(self):
        from src.api import app
        routes = [route.path for route in app.routes]
        assert "/predict" in routes


# ---------------------------------------------------------------------------
# Logger tests
# ---------------------------------------------------------------------------

class TestLogger:
    """Verify logging infrastructure works."""

    def test_get_logger(self):
        from src.logger import get_logger
        test_logger = get_logger("test")
        assert test_logger is not None

    def test_logger_name(self):
        from src.logger import get_logger
        test_logger = get_logger("smoke")
        assert "CropRecommendation" in test_logger.name
