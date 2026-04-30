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


class RecommendationInput(BaseModel):
    crop_name: str
    optimized_conditions: Dict[str, Any]
    current_values: Optional[Dict[str, Any]] = None


@app.post("/recommendations")
async def get_recommendations(data: RecommendationInput):
    """Generate actionable agricultural advice from optimized_conditions.

    For each feature that needs adjustment, returns a category, icon key,
    and bilingual (EN/TR) advice text.
    """

    ADVICE: Dict[str, Any] = {
        "Temperature": {
            "category": "Climate",
            "icon": "thermometer",
            "increase": {
                "en": "Move crops to a warmer location or use greenhouse heating. Consider plastic mulch to retain soil warmth.",
                "tr": "Bitkileri daha sıcak bir alana taşıyın veya sera ısıtması kullanın. Toprak sıcaklığını korumak için plastik malç düşünün."
            },
            "decrease": {
                "en": "Use shade nets or increase irrigation to cool the canopy. Consider growing in a cooler season.",
                "tr": "Gölge ağları kullanın veya yaprak örtüsünü soğutmak için sulamayı artırın. Daha serin bir mevsimde yetiştirmeyi düşünün."
            },
        },
        "Rainfall": {
            "category": "Irrigation",
            "icon": "droplets",
            "increase": {
                "en": "Increase irrigation frequency or switch to drip irrigation. Apply organic mulch to retain soil moisture.",
                "tr": "Sulama sıklığını artırın veya damla sulamaya geçin. Toprak nemini korumak için organik malç uygulayın."
            },
            "decrease": {
                "en": "Improve field drainage. Avoid overhead irrigation; switch to sub-surface or drip methods.",
                "tr": "Tarla drenajını iyileştirin. Yağmurlama sulamadan kaçının; toprak altı veya damla sulama yöntemlerine geçin."
            },
        },
        "pH": {
            "category": "Soil pH",
            "icon": "flask",
            "increase": {
                "en": "Apply agricultural lime (calcium carbonate) to raise soil pH. Dolomitic lime also adds magnesium.",
                "tr": "Toprak pH'ını yükseltmek için tarımsal kireç (kalsiyum karbonat) uygulayın. Dolomitik kireç aynı zamanda magnezyum ekler."
            },
            "decrease": {
                "en": "Apply elemental sulfur or acidifying fertilizers (ammonium sulfate) to lower soil pH.",
                "tr": "Toprak pH'ını düşürmek için elementel kükürt veya asitleştirici gübreler (amonyum sülfat) uygulayın."
            },
        },
        "Light_Hours": {
            "category": "Light",
            "icon": "sun",
            "increase": {
                "en": "Use supplemental grow lights (LED/HPS) or relocate to a more exposed field position.",
                "tr": "Tamamlayıcı büyüme lambaları (LED/HPS) kullanın veya daha açık bir tarla konumuna taşıyın."
            },
            "decrease": {
                "en": "Install shade cloth (30–50%) over the crop canopy to reduce daily light hours.",
                "tr": "Günlük ışık saatlerini azaltmak için bitki örtüsünün üzerine gölge bezi (%30–50) takın."
            },
        },
        "Light_Intensity": {
            "category": "Light",
            "icon": "sun",
            "increase": {
                "en": "Remove shading obstacles (trees, structures) near the field. Use reflective mulch to boost light.",
                "tr": "Tarla yakınındaki gölge engellerini (ağaçlar, yapılar) kaldırın. Işığı artırmak için yansıtıcı malç kullanın."
            },
            "decrease": {
                "en": "Use shade nets or inter-cropping with taller plants to reduce light intensity.",
                "tr": "Işık yoğunluğunu azaltmak için gölge ağları veya daha uzun bitkilerle aralarına ekim yapın."
            },
        },
        "Rh": {
            "category": "Humidity",
            "icon": "wind",
            "increase": {
                "en": "Mist irrigation or foggers can increase humidity. Windbreaks reduce drying winds.",
                "tr": "Sis sulaması veya atomizörler nemi artırabilir. Rüzgar kıranlar kurutucu rüzgarları azaltır."
            },
            "decrease": {
                "en": "Improve air circulation with wider plant spacing. Avoid evening irrigation to reduce night humidity.",
                "tr": "Daha geniş bitki aralığıyla hava sirkülasyonunu iyileştirin. Gece nemini azaltmak için akşam sulamasından kaçının."
            },
        },
        "Nitrogen": {
            "category": "Fertilizer",
            "icon": "leaf",
            "increase": {
                "en": "Apply nitrogen-rich fertilizers: urea (46% N), ammonium nitrate, or organic compost. Split application in multiple doses.",
                "tr": "Azot bakımından zengin gübreler uygulayın: üre (%46 N), amonyum nitrat veya organik kompost. Birden fazla dozda bölünmüş uygulama yapın."
            },
            "decrease": {
                "en": "Reduce nitrogen applications. Use legume cover crops to balance and naturally fix excess nitrogen.",
                "tr": "Azot uygulamalarını azaltın. Fazla azotu dengelemek ve doğal olarak bağlamak için baklagil örtü bitkileri kullanın."
            },
        },
        "Phosphorus": {
            "category": "Fertilizer",
            "icon": "leaf",
            "increase": {
                "en": "Apply superphosphate or di-ammonium phosphate (DAP). Rock phosphate is a slow-release organic option.",
                "tr": "Süperfosfat veya di-amonyum fosfat (DAP) uygulayın. Kaya fosfatı yavaş salınımlı organik bir seçenektir."
            },
            "decrease": {
                "en": "Stop phosphorus fertilization temporarily. High-P soils benefit from deep tillage to dilute concentration.",
                "tr": "Fosfor gübrelemeyi geçici olarak durdurun. Yüksek fosforlu topraklar, konsantrasyonu seyreltmek için derin sürümden yararlanır."
            },
        },
        "Potassium": {
            "category": "Fertilizer",
            "icon": "leaf",
            "increase": {
                "en": "Apply potassium chloride (muriate of potash) or potassium sulfate. Wood ash is a natural organic source.",
                "tr": "Potasyum klorür (potash muriatı) veya potasyum sülfat uygulayın. Odun külü doğal organik bir kaynaktır."
            },
            "decrease": {
                "en": "Avoid potassium-containing fertilizers. Leaching with heavy irrigation can help reduce excess K in sandy soils.",
                "tr": "Potasyum içeren gübrelerden kaçının. Kumlu topraklarda ağır sulamayla yıkama, fazla K'yı azaltmaya yardımcı olabilir."
            },
        },
        "N_Ratio": {
            "category": "Nutrient Balance",
            "icon": "scale",
            "increase": {
                "en": "Increase nitrogen relative to other nutrients. Prefer high-N compound fertilizers.",
                "tr": "Diğer besinlere göre azotu artırın. Yüksek azotlu bileşik gübreler tercih edin."
            },
            "decrease": {
                "en": "Reduce nitrogen or increase phosphorus/potassium to rebalance the N:P:K ratio.",
                "tr": "N:P:K oranını yeniden dengelemek için azotu azaltın veya fosfor/potasyumu artırın."
            },
        },
        "P_Ratio": {
            "category": "Nutrient Balance",
            "icon": "scale",
            "increase": {
                "en": "Increase phosphorus application or reduce nitrogen to improve the P ratio.",
                "tr": "P oranını iyileştirmek için fosfor uygulamasını artırın veya azotu azaltın."
            },
            "decrease": {
                "en": "Reduce phosphorus input or increase nitrogen/potassium to rebalance.",
                "tr": "Yeniden dengelemek için fosfor girdisini azaltın veya azot/potasyumu artırın."
            },
        },
        "K_Ratio": {
            "category": "Nutrient Balance",
            "icon": "scale",
            "increase": {
                "en": "Apply potassium-rich fertilizers or reduce nitrogen to improve the K ratio.",
                "tr": "K oranını iyileştirmek için potasyum açısından zengin gübreler uygulayın veya azotu azaltın."
            },
            "decrease": {
                "en": "Reduce potassium input or increase nitrogen/phosphorus to rebalance.",
                "tr": "Yeniden dengelemek için potasyum girdisini azaltın veya azot/fosfor artırın."
            },
        },
    }

    recommendations = []
    current = data.current_values or {}

    for feat, cond in data.optimized_conditions.items():
        advice_map = ADVICE.get(feat)
        if not advice_map:
            continue

        # Determine direction: compare current value vs recommended target
        cur_val = current.get(feat)
        rec_val = cond.get("recommended") if isinstance(cond, dict) else cond

        direction = None
        try:
            cur_f = float(cur_val) if cur_val is not None else None
            rec_f = float(rec_val) if rec_val is not None else None
            if cur_f is not None and rec_f is not None:
                direction = "increase" if rec_f > cur_f else "decrease"
            elif isinstance(cond, dict) and "mean" in cond:
                mean_f = float(cond["mean"])
                if cur_f is not None:
                    direction = "increase" if mean_f > cur_f else "decrease"
        except (TypeError, ValueError):
            pass

        if direction is None:
            direction = "increase"

        advice_text = advice_map[direction]
        recommendations.append({
            "feature":  feat,
            "category": advice_map["category"],
            "icon":     advice_map["icon"],
            "direction": direction,
            "target":   rec_val,
            "advice":   advice_text,
        })

    return {
        "crop":            data.crop_name,
        "recommendations": recommendations,
    }


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
