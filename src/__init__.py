"""
Crop Recommendation & Yield Optimization System
A complete end-to-end ML system for sensor-based crop management.
"""

from .preprocessing import CropDataProcessor
from .train import ModelTrainer
from .predict import CropPredictor
from .recommender import IntelligentRecommender
from .logger import get_logger

__version__ = "1.0.0"
__author__ = "ML Engineering Team"

__all__ = [
    "CropDataProcessor",
    "ModelTrainer",
    "CropPredictor",
    "IntelligentRecommender",
    "get_logger"
]
