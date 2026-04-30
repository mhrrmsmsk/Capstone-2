"""
FastAPI endpoints for the crop recommendation system.
Provides REST API for making predictions and getting recommendations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from .preprocessing import CropDataProcessor
from .predict import CropPredictor
from .recommender import IntelligentRecommender
from .logger import get_logger

logger = get_logger("api")

app = FastAPI(
    title="CropSense API",
    description="ML-powered crop recommendation and yield optimization",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model state
_predictor: Optional[CropPredictor] = None
_recommender: Optional[IntelligentRecommender] = None
_df_train: Optional[pd.DataFrame] = None
_categorical_options: Dict[str, List[str]] = {}


def _load_models():
    global _predictor, _recommender, _df_train, _categorical_options
    if _predictor is not None:
        return

    models_path = Path(__file__).parent.parent / "models"
    data_path = Path(__file__).parent.parent / "data" / "Soil_Nutrients.csv"

    classifier = joblib.load(models_path / "crop_classifier.pkl")
    regressor = joblib.load(models_path / "yield_regressor.pkl")

    _df_train = pd.read_csv(data_path)

    preprocessor = CropDataProcessor(str(data_path))
    preprocessor.load_preprocessor(models_path)
    preprocessor.load_data()
    preprocessor.handle_missing_values()
    preprocessor.identify_features()

    X_train, y_crop, y_yield = preprocessor.prepare_features_for_training()
    X_train_processed = preprocessor.encode_and_scale(X_train, fit=False)

    _recommender = IntelligentRecommender(
        df_train=_df_train,
        X_train_processed=X_train_processed,
        y_crop=y_crop,
        y_yield=y_yield,
        feature_columns=preprocessor.feature_columns,
        numerical_features=preprocessor.numerical_features,
        categorical_features=preprocessor.categorical_features,
        preprocessor=preprocessor,
    )

    _predictor = CropPredictor(
        classifier,
        regressor,
        preprocessor,
        _recommender,
        preprocessor.feature_columns,
        preprocessor.numerical_features,
        preprocessor.categorical_features,
    )

    for col in preprocessor.categorical_features:
        _categorical_options[col] = sorted(_df_train[col].dropna().unique().tolist())

    logger.info("Models loaded successfully")


@app.on_event("startup")
async def startup_event():
    _load_models()


# ─── Pydantic schemas ────────────────────────────────────────────────────────

class PredictionInput(BaseModel):
    Temperature: Optional[float] = None
    Rainfall: Optional[float] = None
    pH: Optional[float] = None
    Light_Hours: Optional[float] = None
    Light_Intensity: Optional[float] = None
    Rh: Optional[float] = None
    Nitrogen: Optional[float] = None
    Phosphorus: Optional[float] = None
    Potassium: Optional[float] = None
    N_Ratio: Optional[float] = None
    P_Ratio: Optional[float] = None
    K_Ratio: Optional[float] = None
    Fertility: Optional[str] = None
    Photoperiod: Optional[str] = None
    Category_pH: Optional[str] = None
    Soil_Type: Optional[str] = None
    Season: Optional[str] = None


class CropOptimizationInput(BaseModel):
    crop_name: str
    Temperature: Optional[float] = None
    Rainfall: Optional[float] = None
    pH: Optional[float] = None
    Light_Hours: Optional[float] = None
    Light_Intensity: Optional[float] = None
    Rh: Optional[float] = None
    Nitrogen: Optional[float] = None
    Phosphorus: Optional[float] = None
    Potassium: Optional[float] = None
    N_Ratio: Optional[float] = None
    P_Ratio: Optional[float] = None
    K_Ratio: Optional[float] = None
    Fertility: Optional[str] = None
    Photoperiod: Optional[str] = None
    Category_pH: Optional[str] = None
    Soil_Type: Optional[str] = None
    Season: Optional[str] = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _clean(d: dict) -> dict:
    """Remove None values from dict."""
    return {k: v for k, v in d.items() if v is not None}


def _to_serializable(obj: Any) -> Any:
    """Recursively convert numpy types to Python native types."""
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_serializable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": _predictor is not None}


@app.get("/crops")
async def get_crops():
    """Return list of supported crops and categorical option values."""
    if _df_train is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    crops = sorted(_df_train["Name"].dropna().unique().tolist())
    return {"crops": crops, "categorical_options": _categorical_options}


@app.post("/predict")
async def predict(input_data: PredictionInput):
    """Predict crop and yield from partial or complete sensor data."""
    if _predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    try:
        input_dict = _clean(input_data.dict())
        if not input_dict:
            raise HTTPException(status_code=400, detail="At least one feature must be provided")
        result = _predictor.predict(input_dict)
        return JSONResponse(content=_to_serializable(result))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize-crop")
async def optimize_crop(input_data: CropOptimizationInput):
    """Get optimization plan for a specific crop given current conditions."""
    if _predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    try:
        crop_name = input_data.crop_name
        input_dict = {k: v for k, v in input_data.dict().items()
                      if v is not None and k != "crop_name"}
        if not input_dict:
            raise HTTPException(status_code=400, detail="At least one feature must be provided")
        result = _predictor.predict_for_crop(crop_name, input_dict)
        return JSONResponse(content=_to_serializable(result))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Optimization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-predict")
async def batch_predict(inputs: List[PredictionInput]):
    """Batch prediction — accepts up to 500 rows."""
    if _predictor is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    if not inputs:
        raise HTTPException(status_code=400, detail="At least one input required")
    if len(inputs) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 rows per request")
    try:
        results = []
        for i, row in enumerate(inputs):
            d = _clean(row.dict())
            if not d:
                continue
            r = _predictor.predict(d)
            r["row_index"] = i + 1
            results.append(_to_serializable(r))
        return {"total": len(results), "predictions": results}
    except Exception as e:
        logger.error(f"Batch error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feature-importance")
async def feature_importance():
    """Return feature importance from saved CSVs."""
    models_path = Path(__file__).parent.parent / "models"
    result = {}
    for name, fname in [("crop", "feature_importance_crop.csv"),
                         ("yield", "feature_importance_yield.csv")]:
        fp = models_path / fname
        if fp.exists():
            df = pd.read_csv(fp)
            result[name] = df.rename(columns={"feature": "feature", "importance": "importance"}).to_dict(orient="records")
    if not result:
        raise HTTPException(status_code=404, detail="Feature importance files not found. Run run_pipeline.py first.")
    return result


@app.get("/feature-bounds")
async def feature_bounds():
    """Return allowed input range for every numerical feature.

    Strategy: dataset min/max  ±  20% buffer (floored at 0 where negative
    makes no physical sense), rounded to 2 decimal places.
    """
    if _df_train is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    NUMERICAL = [
        "Temperature", "Rainfall", "pH",
        "Light_Hours", "Light_Intensity", "Rh",
        "Nitrogen", "Phosphorus", "Potassium",
        "N_Ratio", "P_Ratio", "K_Ratio",
    ]
    # Features that cannot be negative
    NON_NEGATIVE = {
        "Rainfall", "Light_Hours", "Light_Intensity", "Rh",
        "Nitrogen", "Phosphorus", "Potassium",
        "N_Ratio", "P_Ratio", "K_Ratio",
    }

    bounds = {}
    for col in NUMERICAL:
        if col not in _df_train.columns:
            continue
        col_min = float(_df_train[col].min())
        col_max = float(_df_train[col].max())
        spread  = col_max - col_min if col_max != col_min else abs(col_max) * 0.2 or 1.0

        lo = col_min - spread * 0.20
        hi = col_max + spread * 0.20

        if col in NON_NEGATIVE:
            lo = max(lo, 0.0)

        bounds[col] = {
            "min":      round(lo, 2),
            "max":      round(hi, 2),
            "data_min": round(col_min, 2),
            "data_max": round(col_max, 2),
        }

    return bounds


@app.get("/stats")
async def stats():
    """Return dataset statistics for the dashboard."""
    if _df_train is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    crops = sorted(_df_train["Name"].dropna().unique().tolist())
    yield_stats = {
        "min": float(_df_train["Yield"].min()),
        "max": float(_df_train["Yield"].max()),
        "mean": float(_df_train["Yield"].mean()),
    }
    crop_yield = (
        _df_train.groupby("Name")["Yield"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Name": "crop", "Yield": "avg_yield"})
        .to_dict(orient="records")
    )
    return {
        "total_samples": int(len(_df_train)),
        "total_crops": len(crops),
        "total_features": 17,
        "classification_accuracy": 1.0,
        "yield_r2": 0.9946,
        "yield_stats": yield_stats,
        "crop_yield_ranking": _to_serializable(crop_yield),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
