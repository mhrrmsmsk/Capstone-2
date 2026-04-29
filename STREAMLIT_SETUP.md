# 🎨 Streamlit Web Interface Setup Guide

## Quick Start

### 1️⃣ Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Train Models
Model `.pkl` files are not included in the repo. Train them first (~15 seconds):
```bash
python run_pipeline.py
```

### 3️⃣ Run the App
```bash
streamlit run streamlit_app.py
```

This will:
- Start a local web server
- Open the app in your browser (usually `http://localhost:8501`)
- Display an interactive interface

---

## 🌐 Features

### 🏠 Home Page
- Quick system overview
- Performance metrics
- List of supported crops
- Navigation to other features

### 📊 Single Prediction
**Get crop recommendations and yield estimates**

Three input methods:
- **📝 Manual Input**: Enter each value manually
- **🎲 Random Values**: Load sample data from training set
- **📋 Template**: Select only features you want to provide

Results show:
- Top 5 crop recommendations with probabilities
- Estimated yield value
- Estimated missing values (if applicable)
- Optimized conditions for the recommended crop
- Detailed explanation

### 📈 Batch Prediction
**Process multiple sensor readings at once**

- Upload CSV file with multiple rows
- System processes all predictions
- Shows summary table
- Download results as CSV

Perfect for analyzing multiple fields simultaneously.

### 🔍 Feature Analysis
Three tabs:

**📊 Feature Importance**
- Ranking for crop classification
- Ranking for yield prediction
- See which features matter most

**🎯 Crop Optimization**
- Select a crop
- View optimal ranges for all 17 features
- Download as CSV for reference

**📈 Data Distribution**
- Explore feature distributions
- See how values vary by crop
- Box plots for visualization

### ℹ️ About
- System documentation
- Performance metrics
- List of all supported crops
- Technical stack information

---

## 📋 Example Workflows

### Workflow 1: Check Best Crop for Current Conditions
1. Go to "📊 Single Prediction"
2. Select "📝 Manual Input"
3. Enter your current sensor readings
4. Click "🚀 Make Prediction"
5. See top recommendations with probabilities

### Workflow 2: Optimize Farm for Strawberry Production
1. Go to "🔍 Feature Analysis"
2. Click "🎯 Crop Optimization" tab
3. Select "Strawberry"
4. See optimal ranges for all 17 features
5. Download as CSV for field planning

### Workflow 3: Analyze Multiple Fields
1. Prepare CSV with sensor data from multiple fields
2. Go to "📈 Batch Prediction"
3. Upload CSV file
4. Review results summary
5. Download predictions for reporting

---

## 🎨 UI Components

### Input Fields
- **Number Input**: For numerical features (Temperature, pH, etc.)
- **Selectbox**: For categorical features (Soil_Type, Season, etc.)
- **Slider**: For quick range selection
- **File Uploader**: For batch CSV processing

### Output Visualizations
- **Metrics**: Summary statistics
- **Bar Charts**: Crop recommendations ranking
- **Data Tables**: Feature values and ranges
- **Box Plots**: Data distributions by crop

---

## 💾 Data Upload Format (CSV)

For batch predictions, upload CSV with column names matching features:

```csv
Temperature,Rainfall,pH,Light_Hours,Light_Intensity,Rh,Nitrogen,Phosphorus,Potassium,N_Ratio,P_Ratio,K_Ratio,Fertility,Photoperiod,Category_pH,Soil_Type,Season
21.5,800,6.2,13,500,65,150,80,120,1.25,0.67,1.0,Moderate,Long,Neutral,Loam,Summer
20.3,750,6.5,12.5,480,70,160,85,130,1.30,0.65,1.05,High,Medium,Slightly_Acidic,Clay,Spring
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Use different port
source .venv/bin/activate
streamlit run streamlit_app.py --server.port 8502
```

### Models Not Found
- Model `.pkl` files are gitignored — you must train them first
- Run `python run_pipeline.py` to train and save models
- Check that `models/` directory exists with `.pkl` files

### Import Errors
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Slow Performance
- Streamlit caches models using `@st.cache_resource`
- First load takes longer, subsequent loads are instant
- Batch predictions may take time for large CSV files

---

## 📊 System Architecture

```
User Browser
    ↓
Streamlit Web Server (streamlit_app.py)
    ↓
├─ Page 1: Home
├─ Page 2: Single Prediction
│   ├─ Input Validation
│   ├─ CropPredictor
│   └─ Display Results
├─ Page 3: Batch Prediction
│   ├─ CSV Upload
│   ├─ Process All Rows
│   └─ Export Results
├─ Page 4: Feature Analysis
│   ├─ Feature Importance
│   ├─ Crop Optimization
│   └─ Data Distribution
└─ Page 5: About
    └─ Documentation
```

---

## 🚀 Advanced Usage

### Customize Styling
Edit `streamlit_app.py` to customize:
- Colors and themes
- Layout and spacing
- Icon selections
- Chart configurations

### Add New Features
The app is modular - you can add:
- New prediction tabs
- Additional visualizations
- Custom input validators
- Export formats

### Deploy to Production
```bash
# Deploy to Streamlit Cloud
# 1. Push code to GitHub
# 2. Visit https://share.streamlit.io
# 3. Connect GitHub repo
# 4. Streamlit handles deployment automatically
```

---

## 📞 Support

- **Documentation**: See README.md
- **Issues**: Check browser console (F12)
- **Logs**: Streamlit logs available in terminal

---

## ✅ Checklist

- [x] Streamlit installed
- [x] Dependencies in requirements.txt
- [x] Models trained and saved
- [x] App code created
- [x] Ready to run!

**Next Step**: Run `streamlit run streamlit_app.py` 🚀
