"""
FastAPI endpoints for the crop recommendation system.
Provides REST API for making predictions and getting recommendations.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from pathlib import Path

# Note: These imports would work when running the API in the proper environment
# from .preprocessing import CropDataProcessor
# from .train import ModelTrainer
# from .predict import CropPredictor
# from .recommender import IntelligentRecommender
# from .logger import get_logger

# logger = get_logger("api")

# For development, you can use the following structure:
# This file demonstrates the API endpoints structure
# When deployed, uncomment imports and implement the actual endpoints

app = FastAPI(
    title="Crop Recommendation & Yield Optimization API",
    description="ML-powered system for crop recommendation and yield prediction",
    version="1.0.0"
)

# Global variables to hold models
predictor = None
recommender = None


class PredictionInput(BaseModel):
    """Input schema for prediction request."""
    Fertility: Optional[float] = None
    Photoperiod: Optional[str] = None
    Temperature: Optional[float] = None
    Rainfall: Optional[float] = None
    pH: Optional[float] = None
    Light_Hours: Optional[float] = None
    Light_Intensity: Optional[float] = None
    Rh: Optional[float] = None
    Nitrogen: Optional[float] = None
    Phosphorus: Optional[float] = None
    Potassium: Optional[float] = None
    Category_pH: Optional[str] = None
    Soil_Type: Optional[str] = None
    Season: Optional[str] = None
    N_Ratio: Optional[float] = None
    P_Ratio: Optional[float] = None
    K_Ratio: Optional[float] = None


class CropOptimizationInput(BaseModel):
    """Input schema for crop optimization request."""
    crop_name: str
    Fertility: Optional[float] = None
    Photoperiod: Optional[str] = None
    Temperature: Optional[float] = None
    Rainfall: Optional[float] = None
    pH: Optional[float] = None
    Light_Hours: Optional[float] = None
    Light_Intensity: Optional[float] = None
    Rh: Optional[float] = None
    Nitrogen: Optional[float] = None
    Phosphorus: Optional[float] = None
    Potassium: Optional[float] = None
    Category_pH: Optional[str] = None
    Soil_Type: Optional[str] = None
    Season: Optional[str] = None
    N_Ratio: Optional[float] = None
    P_Ratio: Optional[float] = None
    K_Ratio: Optional[float] = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Crop Recommendation & Yield Optimization API",
        "version": "1.0.0",
        "endpoints": {
            "POST /predict": "Get crop recommendations and yield prediction",
            "POST /optimize-crop": "Get optimization for specific crop",
            "GET /feature-importance": "Get feature importance scores",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running"
    }


@app.post("/predict")
async def predict(input_data: PredictionInput):
    """
    Make crop recommendation and yield prediction.
    
    Accepts both complete and partial input data.
    Returns top 3 crop recommendations with probabilities, estimated yield, and optimal conditions.
    
    Example:
    {
        "Temperature": 21,
        "pH": 6.2,
        "Nitrogen": 120,
        "Soil_Type": "Loam"
    }
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please initialize the system.")
    
    try:
        # Convert input to dictionary, excluding None values
        input_dict = {k: v for k, v in input_data.dict().items() if v is not None}
        
        if not input_dict:
            raise HTTPException(status_code=400, detail="At least one feature must be provided")
        
        # Validate input
        validation = predictor.validate_input(input_dict)
        
        # Make prediction
        result = predictor.predict(input_dict)
        result['input_validation'] = validation
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/optimize-crop")
async def optimize_crop(input_data: CropOptimizationInput):
    """
    Get optimization recommendations for a specific crop.
    
    Returns optimal conditions (ranges) for all features based on high-yield samples.
    
    Example:
    {
        "crop_name": "Strawberry",
        "Temperature": 20,
        "pH": 6.5,
        "Rainfall": 750
    }
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please initialize the system.")
    
    try:
        crop_name = input_data.crop_name
        
        # Extract features (excluding crop_name)
        input_dict = {k: v for k, v in input_data.dict().items() 
                     if v is not None and k != "crop_name"}
        
        if not input_dict:
            raise HTTPException(status_code=400, detail="At least one feature must be provided")
        
        # Make prediction for specific crop
        result = predictor.predict_for_crop(crop_name, input_dict)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/feature-importance")
async def get_feature_importance():
    """Get feature importance scores from trained models."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please initialize the system.")
    
    try:
        importance = predictor.get_feature_importance()
        
        return {
            "feature_importance": importance,
            "total_features": len(importance)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@app.post("/batch-predict")
async def batch_predict(inputs: List[PredictionInput]):
    """
    Make batch predictions for multiple inputs.
    
    Example:
    [
        {"Temperature": 20, "pH": 6.5},
        {"Temperature": 22, "Rainfall": 800},
        {"Nitrogen": 150, "Phosphorus": 100}
    ]
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please initialize the system.")
    
    if not inputs:
        raise HTTPException(status_code=400, detail="At least one input must be provided")
    
    if len(inputs) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 inputs allowed per request")
    
    try:
        input_dicts = [
            {k: v for k, v in input_data.dict().items() if v is not None}
            for input_data in inputs
        ]
        
        results = predictor.batch_predict(input_dicts)
        
        return {
            "total_predictions": len(results),
            "predictions": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/model-info")
async def get_model_info():
    """Get information about loaded models."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        "crop_classifier": predictor.crop_classifier is not None,
        "yield_regressor": predictor.yield_regressor is not None,
        "feature_count": len(predictor.feature_columns),
        "numerical_features": len(predictor.numerical_features),
        "categorical_features": len(predictor.categorical_features),
        "features": predictor.feature_columns
    }


def initialize_api(predictor_instance, recommender_instance):
    """
    Initialize the API with model instances.
    Call this after loading models in main.py or notebook.
    
    Args:
        predictor_instance: CropPredictor instance
        recommender_instance: IntelligentRecommender instance
    """
    global predictor, recommender
    predictor = predictor_instance
    recommender = recommender_instance


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
