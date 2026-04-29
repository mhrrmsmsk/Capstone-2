# QUICK START GUIDE
## Sensor-Based Crop Recommendation & Yield Optimization System

---

## ⚡ 30-Second Setup

### 1. Clone & Install
```bash
git clone https://github.com/<your-username>/crop-recommendation-system.git
cd crop-recommendation-system
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Train Models
Model `.pkl` files are not included in the repo. Train them first (~15 seconds):
```bash
python run_pipeline.py
```

### 3. Run the System

**Option A: FastAPI Server (for production/API use)**
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
# Then visit: http://localhost:8000/docs
```

**Option B: Streamlit Web Interface (for interactive use)**
```bash
streamlit run streamlit_app.py
# Opens at: http://localhost:8501
```

**Option C: Jupyter Notebook (for learning)**
```bash
jupyter notebook main.ipynb
```

**Option D: Docker**
```bash
docker build -t crop-recommendation .
docker run -p 8000:8000 crop-recommendation
```

---

## 📊 What You Get

### Crop Recommendation (Classification)
```
Input: Environmental & soil sensor readings
Output: Top 3 recommended crops with confidence percentages
Accuracy: 100% test accuracy (CV: 99.98%)
```

### Yield Prediction (Regression)
```
Input: Crop and growing conditions
Output: Predicted yield value
Accuracy: R² = 0.9946
```

### Smart Missing Value Handling
```
Input: Partial sensor data (3+ features out of 17)
Output: Intelligent estimates for missing features based on similar high-yield samples
Method: KNN similarity search (NOT simple mean imputation)
```

### Crop Optimization
```
Input: Target crop name + available conditions
Output: Optimal ranges for all 17 features
```

---

## 🔧 API Endpoints

### 1. Get Crop Recommendations
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

### 2. Optimize for Specific Crop
```bash
curl -X POST http://localhost:8000/optimize-crop \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Strawberry",
    "Temperature": 20,
    "pH": 6.5
  }'
```

### 3. Batch Predictions
```bash
curl -X POST http://localhost:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '[
    {"Temperature": 20, "pH": 6.5, "Nitrogen": 150},
    {"Temperature": 22, "Rainfall": 800}
  ]'
```

### 4. Feature Importance
```bash
curl http://localhost:8000/feature-importance
```

### 5. Health Check
```bash
curl http://localhost:8000/health
```

---

## 📝 Input Features

You can provide any combination of these 17 features:

**Numerical**: Temperature, Rainfall, pH, Light_Hours, Light_Intensity, Rh, 
             Nitrogen, Phosphorus, Potassium, N_Ratio, P_Ratio, K_Ratio

**Categorical**: Fertility (Low/Moderate/High), Photoperiod, Category_pH, 
                Soil_Type (Loam/Clay/Sandy), Season

---

## 📊 Sample Response

```json
{
  "timestamp": "2024-04-29T14:32:00.123456",
  "input_type": "partial",
  "recommended_crops": [
    {"name": "Strawberry", "probability": 0.87},
    {"name": "Tomato", "probability": 0.09},
    {"name": "Pepper", "probability": 0.04}
  ],
  "estimated_yield": 24.7,
  "missing_features_count": 14,
  "estimated_missing_values": {
    "Light_Hours": {
      "range": "12.5–13.5",
      "recommended": "13.0 ± 0.5"
    },
    "Rainfall": {
      "range": "700–950",
      "recommended": "825 ± 75"
    }
  },
  "optimized_conditions": {
    "Temperature": {"range": "18–22", "recommended": "20 ± 2"},
    "Nitrogen": {"range": "150–190", "recommended": "170 ± 18"}
  },
  "explanation": "Prediction based on 3 provided features. Missing values estimated using similarity to 10 high-yield samples."
}
```

---

## 🎯 Use Cases

### Precision Farming
```
Farmer has: Current temperature, soil pH, rainfall
System provides: Best crop to plant + predicted yield + optimal conditions
```

### Crop Optimization
```
Farm wants: To maximize Strawberry yield
System provides: All 17 feature ranges for optimal conditions
```

### Multi-Location Planning
```
Manager has: 50 sensor readings from different fields
System provides: Top-3 crops for each location in seconds via batch API
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `run_pipeline.py` | Train models and run demo |
| `main.ipynb` | Complete interactive tutorial |
| `streamlit_app.py` | Web interface |
| `README.md` | Full documentation |
| `QUICK_START.md` | This guide |
| `CONTRIBUTING.md` | How to contribute |
| `src/preprocessing.py` | Data processing |
| `src/train.py` | Model training |
| `src/predict.py` | Prediction engine |
| `src/recommender.py` | KNN-based recommendation |
| `src/api.py` | REST API endpoints |

---

## 🐛 Troubleshooting

### "ModuleNotFoundError" when running
```bash
# Make sure you installed dependencies
pip install -r requirements.txt
```

### API won't start
```bash
# Check if port 8000 is in use
lsof -i :8000
# Use different port
uvicorn src.api:app --port 8001
```

### Models not found
```bash
# Model .pkl files are gitignored. Train them first:
python run_pipeline.py
```

---

## 📞 System Architecture

```
User Request
    ↓
Input Validation (src/predict.py)
    ↓
├─→ Complete Data? 
│   ├─→ Encode & Scale (src/preprocessing.py)
│   ├─→ Classify (src/train.py)
│   └─→ Regress (src/train.py)
│
└─→ Partial Data?
    ├─→ Find Similar Samples (src/recommender.py - KNN)
    ├─→ Estimate Missing Values
    ├─→ Recommend Crops
    └─→ Predict Yield
    
Return JSON Response
    ↓
Client/Frontend
```

---

## 🚀 Performance

| Component | Performance |
|-----------|-------------|
| Crop Classification | 100% accuracy |
| Yield Prediction | R² = 0.9946 |
| API Response | < 100ms |
| Batch Processing (100 samples) | < 2 seconds |
| Model Training (15,400 samples) | ~15 seconds |

---

## 📚 Dataset Info

- **Size**: 15,400 samples
- **Crops**: 22 varieties
- **Features**: 17 input + 2 targets
- **Balance**: Perfectly balanced (700 per crop)
- **Missing Values**: None
- **Yield Range**: 0.77 - 66.62 units

---

## 🎓 Learning Resources

1. **For ML concepts**: Read `SYSTEM_COMPLETION_REPORT.md`
2. **For implementation**: Open `main.ipynb` in Jupyter
3. **For API usage**: Visit `http://localhost:8000/docs` (interactive Swagger UI)
4. **For code details**: Check docstrings in `src/*.py` files

---

## ✅ System Status

```
✓ Data Preprocessing:      COMPLETE
✓ Classification Model:    COMPLETE (100% accuracy)
✓ Regression Model:        COMPLETE (R² = 0.9946)
✓ KNN Similarity Search:   COMPLETE
✓ Recommendation Engine:   COMPLETE
✓ REST API:                COMPLETE
✓ FastAPI Integration:     COMPLETE
✓ Logging & Monitoring:    COMPLETE
✓ Documentation:           COMPLETE

STATUS: 🟢 PRODUCTION READY
```

---

## 🎉 Next Steps

1. **Try it locally**
   ```bash
   jupyter notebook main.ipynb
   ```

2. **Deploy the API**
   ```bash
   uvicorn src.api:app --host 0.0.0.0 --port 8000
   ```

3. **Make predictions**
   ```bash
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"Temperature": 20, "pH": 6.5}'
   ```

4. **Scale to production**
   - Use Docker for containerization
   - Deploy on Kubernetes
   - Add load balancing
   - Integrate with database

---

**Last Updated**: April 2024  
**Status**: ✅ Production Ready  
**Support**: See README.md for detailed documentation
