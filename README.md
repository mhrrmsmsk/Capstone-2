# Sensor-Based Crop Recommendation & Yield Optimization System

A production-ready, end-to-end machine learning system that provides intelligent crop recommendations and yield predictions based on environmental and soil sensor data.

## 🎯 Project Overview

This system intelligently handles **both complete and incomplete sensor data** to:
1. **Recommend optimal crops** based on environmental conditions using classification
2. **Predict crop yield** for given conditions using regression
3. **Estimate missing values** using KNN similarity-based approach
4. **Suggest optimal growing conditions** for each crop based on high-yield samples

## 📊 Dataset

**File**: `data/Soil_Nutrients.csv`

**17 Input Features**:
- **Environmental**: Temperature, Rainfall, Photoperiod, Light_Hours, Light_Intensity, Rh
- **Soil**: pH, Fertility, Soil_Type, Category_pH
- **Nutrients**: Nitrogen, Phosphorus, Potassium, N_Ratio, P_Ratio, K_Ratio
- **Season**: Season

**2 Targets**:
- `Name` (Crop type) - Classification target
- `Yield` - Regression target

## 🏗️ Project Structure

```
crop-recommendation-system/
├── main.ipynb                    # Main Jupyter notebook (complete workflow)
├── run_pipeline.py               # End-to-end training pipeline script
├── streamlit_app.py              # Streamlit web interface
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Modern Python packaging config
├── Dockerfile                    # Container build configuration
├── .dockerignore                 # Docker ignore rules
├── .gitignore                    # Git ignore rules
├── .gitattributes                # Git LFS config for model files
├── LICENSE                       # MIT License
├── README.md                     # This file
├── CONTRIBUTING.md               # Contribution guidelines
├── CODE_OF_CONDUCT.md            # Community code of conduct
├── QUICK_START.md                # 30-second setup guide
├── DELIVERY_SUMMARY.md           # Project delivery summary
├── SYSTEM_COMPLETION_REPORT.md   # Detailed technical report
├── STREAMLIT_SETUP.md            # Streamlit setup guide
├── data/
│   └── Soil_Nutrients.csv       # Dataset (15,400 samples)
├── src/
│   ├── __init__.py              # Package initialization
│   ├── logger.py                # Logging configuration
│   ├── preprocessing.py         # Data preprocessing pipeline
│   ├── train.py                 # Model training module
│   ├── predict.py               # Prediction engine
│   ├── recommender.py           # Intelligent recommendation system
│   └── api.py                   # FastAPI endpoints
├── models/                      # Trained models (Git LFS)
│   ├── crop_classifier.pkl      # Classification model
│   ├── yield_regressor.pkl      # Regression model
│   ├── scaler.pkl               # Feature scaler
│   ├── label_encoder.pkl        # Categorical encoders
│   ├── knn_model.pkl            # Similarity search model
│   ├── metadata.json            # Model metadata
│   ├── feature_importance_crop.csv
│   ├── feature_importance_yield.csv
│   └── plots/
│       ├── feature_importance_crop.png
│       └── feature_importance_yield.png
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_smoke.py            # Smoke tests
└── logs/                        # Application logs (gitignored)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/crop-recommendation-system.git
cd crop-recommendation-system

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Train Models

Trained model files (`.pkl`) are **not included** in the repository due to their size. You must train them first:

```bash
# Option A: Run the pipeline script
python run_pipeline.py

# Option B: Run the Jupyter notebook
jupyter notebook main.ipynb
```

This trains both models and saves them to `models/`. The process takes ~15 seconds.

### 3. Run the System

**Option A: FastAPI Server (for production/API use)**
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
# API: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

**Option B: Streamlit Web Interface (for interactive use)**
```bash
streamlit run streamlit_app.py
# Opens at: http://localhost:8501
```

**Option C: Jupyter Notebook (for learning/exploration)**
```bash
jupyter notebook main.ipynb
```

**Option D: Docker**
```bash
docker build -t crop-recommendation .
docker run -p 8000:8000 crop-recommendation
```

## 🤖 Key Features

### 1. Data Preprocessing
- ✅ **Categorical Encoding**: LabelEncoding for Soil_Type, Season, Photoperiod, Category_pH
- ✅ **Feature Scaling**: StandardScaler for all numerical features
- ✅ **Missing Value Handling**: Smart imputation with median/mean
- ✅ **Train/Test Split**: Stratified 80/20 split

### 2. Crop Classification Model
- **Model**: RandomForestClassifier (200 trees, max_depth=20)
- **Performance**: 100% test accuracy, 99.98% CV
- **Output**: Top-3 crops with probabilities

### 3. Yield Prediction Model
- **Model**: RandomForestRegressor (200 trees, max_depth=20)
- **Performance**: R² = 0.9946, RMSE = 1.14
- **Metrics**: RMSE, MAE, R²

### 4. Intelligent Missing Value Estimation ⭐
Instead of simple mean imputation, this system:
- Uses KNN (k=10) to find similar samples in feature space
- Prioritizes **high-yield samples only**
- Estimates missing values from neighbors
- Provides optimal ranges (min-max, mean ± std)
- Explains recommendations based on data evidence

### 5. Unified Recommendation Engine
```python
# Complete Input
predictor.predict({
    'Fertility': 'High',
    'Temperature': 20,
    'pH': 6.5,
    # ... all 17 features
})

# Partial Input (3+ features)
predictor.predict({
    'Temperature': 20,
    'pH': 6.5,
    'Nitrogen': 150
    # Missing 15 features - will be estimated!
})

# Crop Optimization
predictor.predict_for_crop('Strawberry', {
    'Temperature': 20,
    'pH': 6.5
})
```

## 📡 API Endpoints

### 1. POST /predict
Get crop recommendations and yield prediction

**Request**:
```json
{
    "Temperature": 21,
    "pH": 6.2,
    "Nitrogen": 120,
    "Soil_Type": "Loam"
}
```

**Response**:
```json
{
    "timestamp": "2024-04-29T12:34:56.789...",
    "input_type": "partial",
    "recommended_crops": [
        {"name": "Strawberry", "probability": 0.87},
        {"name": "Tomato", "probability": 0.09},
        {"name": "Pepper", "probability": 0.04}
    ],
    "estimated_yield": 24.7,
    "missing_features_count": 14,
    "estimated_missing_values": {
        "Rainfall": {
            "min": 700.5,
            "max": 950.2,
            "mean": 825.3,
            "std": 75.2,
            "range": "700–950",
            "recommended": "825 ± 75"
        },
        "Light_Hours": { ... },
        ...
    },
    "optimized_conditions": {
        "Rainfall": {"range": "850–1050", "recommended": "920 ± 85"},
        ...
    },
    "explanation": "Prediction based on partial input (4 features provided). ..."
}
```

### 2. POST /optimize-crop
Optimize conditions for a specific crop

**Request**:
```json
{
    "crop_name": "Strawberry",
    "Temperature": 20,
    "pH": 6.5,
    "Rainfall": 750
}
```

**Response**: Optimization recommendations with ranges

### 3. POST /batch-predict
Make predictions for multiple inputs

**Request**:
```json
[
    {"Temperature": 20, "pH": 6.5, "Nitrogen": 150},
    {"Temperature": 22, "Rainfall": 800, "Soil_Type": "Clay"},
    {"Temperature": 18, "pH": 6.2, "Nitrogen": 160}
]
```

### 4. GET /feature-importance
Get feature importance scores from both models

### 5. GET /health
Health check endpoint

### 6. GET /model-info
Get information about loaded models

## 📈 Model Performance

### Classification (Crop Recommendation)
```
Train Accuracy:        1.0000
Test Accuracy:         1.0000
Cross-Validation:      0.9998 (±0.0005)
```

### Regression (Yield Prediction)
```
Test RMSE:             1.1403
Test MAE:              0.5520
Test R²:               0.9946
Cross-Validation R²:   0.9931 (±0.0089)
```

## 🔍 Example Usage

### Example 1: Minimal Input (3 Features)

```python
from src.predict import CropPredictor
from src.preprocessing import CropDataProcessor
from src.train import ModelTrainer
from src.recommender import IntelligentRecommender

# Step 1: Load and preprocess data
processor = CropDataProcessor('data/Soil_Nutrients.csv')
df = processor.load_data()
processor.handle_missing_values(strategy='mean')
processor.identify_features()
X, y_crop, y_yield = processor.prepare_features_for_training()
X_processed = processor.encode_and_scale(X, fit=True)
processor.save_preprocessor()

# Step 2: Train models (or load pre-trained with ModelTrainer.load_models())
trainer = ModelTrainer()
from sklearn.model_selection import train_test_split
X_train, X_test, y_crop_train, y_crop_test, y_yield_train, y_yield_test = \
    train_test_split(X_processed, y_crop, y_yield, test_size=0.2, random_state=42, stratify=y_crop)
trainer.train_crop_classifier(X_train, y_crop_train, X_test, y_crop_test)
trainer.train_yield_regressor(X_train, y_yield_train, X_test, y_yield_test)
trainer.save_models()

# Step 3: Create predictor and make predictions
recommender = IntelligentRecommender(
    df_train=df, X_train_processed=X_processed, y_crop=y_crop, y_yield=y_yield,
    feature_columns=processor.feature_columns,
    numerical_features=processor.numerical_features,
    categorical_features=processor.categorical_features,
    preprocessor=processor
)
recommender.save_recommender()

predictor = CropPredictor(
    crop_classifier=trainer.crop_classifier,
    yield_regressor=trainer.yield_regressor,
    preprocessor=processor,
    recommender=recommender,
    feature_columns=processor.feature_columns,
    numerical_features=processor.numerical_features,
    categorical_features=processor.categorical_features
)

# Make prediction with only 3 features
result = predictor.predict({'Temperature': 22, 'Rainfall': 800, 'pH': 6.3})
print(result['recommended_crops'])  # Top 3 crops with probabilities
# System automatically estimates missing features!
```

### Example 2: Crop Optimization

```python
# Get optimal conditions for Strawberry
optimization = predictor.predict_for_crop('Strawberry', {
    'Temperature': 20,
    'pH': 6.5
})

# Access optimized ranges
print(optimization['optimized_conditions']['Rainfall'])
# Output: {'range': '850–1050', 'recommended': '920 ± 85', ...}
```

### Example 3: API Request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Temperature": 21,
    "pH": 6.2,
    "Nitrogen": 120,
    "Soil_Type": "Loam"
  }'
```

## 📊 Feature Importance

### Top Features for Crop Classification
1. Potassium
2. Rh
3. Phosphorus
4. Nitrogen
5. Light_Intensity

### Top Features for Yield Prediction
1. Light_Hours
2. Soil_Type
3. Potassium
4. Light_Intensity
5. Rainfall

## 🧠 How It Works

### 1. Complete Input Flow
```
Input (17 features) → Encode/Scale → Classifier → Top 3 Crops
                    → Regressor → Yield Estimate
                    → Optimizer → Condition Ranges
```

### 2. Partial Input Flow (Smart)
```
Input (3-17 features)
  ↓
KNN Similarity Search (k=10)
  ↓
Find Similar High-Yield Samples
  ↓
Estimate Missing Values (min-max-mean-std)
  ↓
Recommend Crops (based on neighbor crops)
  ↓
Predict Yield (based on similar samples)
  ↓
Optimize Conditions (ranges for high yield)
```

## 🛠️ Configuration

### Logging
Logs are saved to `logs/system_YYYYMMDD_HHMMSS.log`

### Model Parameters
Edit in respective files:
- **Classification**: `src/train.py` - `train_crop_classifier()`
- **Regression**: `src/train.py` - `train_yield_regressor()`
- **KNN**: `src/recommender.py` - `__init__()` (n_neighbors=10)

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### Manual Testing
Run the notebook cells or use the demo section in `main.ipynb`

## 📋 Module Documentation

### preprocessing.py
```python
CropDataProcessor(data_path)
  - load_data()
  - explore_data()
  - identify_features()
  - handle_missing_values()
  - prepare_features_for_training()
  - encode_and_scale()
  - save_preprocessor()
  - load_preprocessor()
```

### train.py
```python
ModelTrainer(models_dir)
  - train_crop_classifier()
  - train_yield_regressor()
  - save_models()
  - load_models()
  - plot_feature_importance()
```

### recommender.py
```python
IntelligentRecommender()
  - find_similar_samples()
  - estimate_missing_values()
  - recommend_crops()
  - predict_yield_for_crop()
  - get_optimization_recommendations()
```

### predict.py
```python
CropPredictor()
  - predict_from_complete_data()
  - predict_from_partial_data()
  - predict()
  - predict_for_crop()
  - batch_predict()
  - validate_input()
```

## 🔧 Troubleshooting

### Models not found
```bash
# Model .pkl files are gitignored. Train them first:
python run_pipeline.py
# Or run the notebook:
jupyter notebook main.ipynb
```

### Import errors
```bash
# Make sure you're in the project root directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### API connection refused
```bash
# Check if server is running
ps aux | grep uvicorn

# Start server
uvicorn src.api:app --reload
```

## 📚 Dependencies

- `fastapi`: REST API framework
- `uvicorn`: ASGI server
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `scikit-learn`: ML algorithms
- `matplotlib`: Visualization
- `seaborn`: Statistical visualization
- `joblib`: Model persistence
- `pydantic`: Data validation

## 💡 Production Considerations

1. **Deployment**: Use Docker with FastAPI + Uvicorn
2. **Database**: Store predictions in PostgreSQL/MongoDB
3. **Monitoring**: Use Prometheus + Grafana
4. **Caching**: Redis for frequent predictions
5. **Scaling**: Use Kubernetes for horizontal scaling
6. **Security**: Add authentication (JWT/OAuth2)
7. **Rate Limiting**: Implement API throttling
8. **Versioning**: Track model versions in models/

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 👨‍💻 Author

Built as a comprehensive end-to-end ML system following production best practices.

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Last Updated**: April 2024
**Status**: ✅ Production Ready
