"""
Streamlit Web Interface for Crop Recommendation & Yield Optimization System
================================================================================

Interactive web application for sensor-based crop recommendations and yield predictions.
Supports both complete and partial sensor data with intelligent missing value estimation.

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import joblib
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.preprocessing import CropDataProcessor
from src.predict import CropPredictor
from src.recommender import IntelligentRecommender
from src.logger import get_logger

# Configuration
st.set_page_config(
    page_title="CropSense — Crop Recommendation & Yield Optimization",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional styling
st.markdown("""
<style>
    /* Cleaner typography */
    .stMetric label { font-size: 0.85rem; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 600; }
    /* Subtle section dividers */
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0; }
    /* Sidebar cleanup */
    [data-testid="stSidebar"] { border-right: 1px solid #e0e0e0; }
    /* Dataframe styling */
    .stDataFrame { border: 1px solid #e0e0e0; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

logger = get_logger("streamlit_app")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_resource
def load_system():
    """Load trained models and initialize predictor"""
    try:
        models_path = Path(__file__).parent / "models"
        data_path = Path(__file__).parent / "data" / "Soil_Nutrients.csv"
        
        # Check if required files exist
        required_files = {
            'crop_classifier.pkl': 'Crop classifier',
            'yield_regressor.pkl': 'Yield regressor',
            'scaler.pkl': 'Feature scaler',
            'label_encoder.pkl': 'Label encoder',
            'knn_model.pkl': 'KNN model'
        }
        
        missing_files = []
        for filename, description in required_files.items():
            filepath = models_path / filename
            if not filepath.exists():
                missing_files.append(f"{description} ({filename})")
                logger.warning(f"Missing: {filename}")
        
        if missing_files:
            error_msg = "Missing trained models:\n"
            for file in missing_files:
                error_msg += f"  • {file}\n"
            error_msg += "\n**To fix:**\n"
            error_msg += "1. Run: `python3 run_pipeline.py`\n"
            error_msg += "2. Or open `main.ipynb` in Jupyter and run all cells"
            st.error(error_msg)
            logger.error(f"Missing model files: {missing_files}")
            return None, None, None
        
        # Load models
        classifier = joblib.load(models_path / "crop_classifier.pkl")
        regressor = joblib.load(models_path / "yield_regressor.pkl")
        knn = joblib.load(models_path / "knn_model.pkl")
        
        # Load data for recommender
        if not data_path.exists():
            st.error(f"Dataset not found: {data_path}")
            return None, None, None
        
        df_train = pd.read_csv(data_path)
        
        # Create preprocessor
        preprocessor = CropDataProcessor(str(data_path))
        preprocessor.load_preprocessor(models_path)
        preprocessor.load_data()
        preprocessor.handle_missing_values()
        preprocessor.identify_features()

        # Prepare the training feature matrix expected by the recommender
        X_train, y_crop, y_yield = preprocessor.prepare_features_for_training()
        X_train_processed = preprocessor.encode_and_scale(X_train, fit=False)
        
        # Initialize recommender
        recommender = IntelligentRecommender(
            df_train=df_train,
            X_train_processed=X_train_processed,
            y_crop=y_crop,
            y_yield=y_yield,
            feature_columns=preprocessor.feature_columns,
            numerical_features=preprocessor.numerical_features,
            categorical_features=preprocessor.categorical_features,
            preprocessor=preprocessor,
        )
        
        # Initialize predictor
        predictor = CropPredictor(
            classifier,
            regressor,
            preprocessor,
            recommender,
            preprocessor.feature_columns,
            preprocessor.numerical_features,
            preprocessor.categorical_features,
        )
        
        return predictor, recommender, df_train
    except Exception as e:
        error_msg = f"Error loading system: {str(e)}\n\n"
        error_msg += "**Troubleshooting steps:**\n"
        error_msg += "1. Make sure you're in the correct directory\n"
        error_msg += "2. Train models: `python3 run_pipeline.py`\n"
        error_msg += "3. Or use Jupyter: `jupyter notebook main.ipynb`\n"
        st.error(error_msg)
        logger.error(f"System loading error: {str(e)}", exc_info=True)
        return None, None, None


def create_gauge_chart(value, title, min_val=0, max_val=100):
    """Create a gauge chart for displaying metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val/2], 'color': "lightgray"},
                {'range': [max_val/2, max_val], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=80, b=20))
    return fig


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Sidebar
    st.sidebar.title("CropSense")
    st.sidebar.caption("Crop Recommendation & Yield Optimization")
    st.sidebar.divider()
    
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Predict", "Optimize", "Batch", "Analysis"],
        label_visibility="collapsed",
    )
    
    st.sidebar.divider()
    st.sidebar.caption("Classification 100% | Regression R²=0.9946 | 22 crops")
    
    # Load system
    predictor, recommender, df_train = load_system()
    
    if predictor is None:
        st.error("System failed to load. Please check the model files.")
        return
    
    # ========================================================================
    # PAGE: DASHBOARD
    # ========================================================================
    if page == "Dashboard":
        st.title("CropSense Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Classification Accuracy", "100%")
        with col2:
            st.metric("Yield R²", "0.9946")
        with col3:
            st.metric("Supported Crops", "22")
        with col4:
            st.metric("Input Features", "17")
        
        st.divider()
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Quick Predict")
            st.caption("Enter a few sensor readings to get a crop recommendation instantly.")
            quick_features = ["Temperature", "Rainfall", "pH"]
            quick_data = {}
            qcols = st.columns(3)
            for i, feat in enumerate(quick_features):
                with qcols[i]:
                    quick_data[feat] = st.number_input(feat, value=0.0, key=f"q_{feat}")
            
            if st.button("Predict", use_container_width=True, key="quick_predict"):
                result = predictor.predict(quick_data)
                top = result.get("recommended_crops", [])
                if top:
                    st.success(f"**Top recommendation:** {top[0]['name']} ({top[0]['probability']:.0%})")
                    if len(top) > 1:
                        others = ", ".join(f"{c['name']} ({c['probability']:.0%})" for c in top[1:4])
                        st.caption(f"Alternatives: {others}")
                    st.metric("Estimated Yield", f"{result.get('estimated_yield', 0):.2f}")
        
        with col_right:
            st.subheader("Supported Crops")
            crops = sorted(df_train['Name'].unique().tolist())
            for crop in crops:
                st.caption(crop)
        
    # ========================================================================
    # PAGE: SINGLE PREDICTION
    # ========================================================================
    elif page == "Predict":
        st.title("Predict Crop & Yield")

        input_method = st.radio("Input method:", ["Manual", "Sample from dataset", "Template"], horizontal=True)

        # Initialize session state
        if 'input_data' not in st.session_state:
            st.session_state.input_data = {}

        # Define features
        numerical_features = [
            'Temperature', 'Rainfall', 'pH', 'Light_Hours', 'Light_Intensity', 'Rh',
            'Nitrogen', 'Phosphorus', 'Potassium', 'N_Ratio', 'P_Ratio', 'K_Ratio'
        ]
        categorical_features = ['Fertility', 'Photoperiod', 'Category_pH', 'Soil_Type', 'Season']
        crops = sorted(df_train['Name'].unique().tolist())

        input_data = {}

        if input_method == "Manual":
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Numerical")
                for feature in numerical_features:
                    input_data[feature] = st.number_input(
                        f"{feature}",
                        value=0.0,
                        key=f"num_{feature}"
                    )

            with col2:
                st.subheader("Categorical")
                input_data['Fertility'] = st.selectbox("Fertility", df_train['Fertility'].unique().tolist(), key="Fertility")
                input_data['Photoperiod'] = st.selectbox("Photoperiod", df_train['Photoperiod'].unique().tolist(), key="Photoperiod")
                input_data['Category_pH'] = st.selectbox("Category_pH", df_train['Category_pH'].unique().tolist(), key="Category_pH")
                input_data['Soil_Type'] = st.selectbox("Soil_Type", df_train['Soil_Type'].unique().tolist(), key="Soil_Type")
                input_data['Season'] = st.selectbox("Season", df_train['Season'].unique().tolist(), key="Season")
        
        elif input_method == "Sample from dataset":
            # Random values from training data
            sample_row = df_train.sample(1).iloc[0]
            
            for feature in numerical_features:
                input_data[feature] = st.number_input(
                    f"{feature}",
                    value=float(sample_row[feature]),
                    key=f"rand_{feature}"
                )
            
            for feature in categorical_features:
                options = df_train[feature].unique().tolist()
                input_data[feature] = st.selectbox(
                    feature,
                    options,
                    index=options.index(sample_row[feature]) if sample_row[feature] in options else 0,
                    key=f"rand_{feature}"
                )
        
        elif input_method == "Template":
            st.info("Select features to provide. Unselected features will be estimated.")
            
            selected_features = st.multiselect(
                "Choose features to provide:",
                numerical_features + categorical_features,
                default=['Temperature', 'Rainfall', 'pH']
            )
            
            # Get sample values
            sample_row = df_train.sample(1).iloc[0]
            
            for feature in selected_features:
                if feature in numerical_features:
                    input_data[feature] = st.number_input(
                        f"{feature}",
                        value=float(sample_row[feature]),
                        key=f"template_{feature}"
                    )
                else:
                    options = df_train[feature].unique().tolist()
                    input_data[feature] = st.selectbox(
                        feature,
                        options,
                        key=f"template_{feature}"
                    )
        
        # Make prediction
        if st.button("Predict", use_container_width=True, type="primary"):
            try:
                result = predictor.predict(input_data)
                st.divider()
                
                # Recommended Crops
                crops_data = result.get('recommended_crops', [])
                
                if crops_data:
                    col1, col2, col3 = st.columns(3)
                    for col, crop in zip([col1, col2, col3], crops_data[:3]):
                        with col:
                            prob = crop.get('probability', 0) * 100
                            st.metric(crop['name'], f"{prob:.1f}%")
                
                # Bar chart
                crop_names = [c['name'] for c in crops_data[:5]]
                crop_probs = [c['probability'] * 100 for c in crops_data[:5]]
                fig = px.bar(
                    x=crop_probs, y=crop_names, orientation='h',
                    labels={'x': 'Probability (%)', 'y': ''},
                    color=crop_probs, color_continuous_scale='greens',
                )
                fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Yield & input type
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Estimated Yield", f"{result.get('estimated_yield', 0):.2f}")
                with col2:
                    st.metric("Input Type", result.get('input_type', 'unknown').title())
                
                # Missing Values
                estimated_missing = result.get('estimated_missing_values', {})
                if estimated_missing:
                    with st.expander("Estimated Missing Values", expanded=False):
                        miss_data = []
                        for feature, ranges in estimated_missing.items():
                            miss_data.append({
                                'Feature': feature,
                                'Range': ranges.get('range', 'N/A'),
                                'Recommended': ranges.get('recommended', 'N/A')
                            })
                        st.dataframe(pd.DataFrame(miss_data), use_container_width=True, hide_index=True)
                
                # Optimized Conditions
                optimized = result.get('optimized_conditions', {})
                if optimized:
                    top_crop_name = crops_data[0]['name'] if crops_data else 'Crop'
                    with st.expander(f"Optimized Conditions for {top_crop_name}", expanded=False):
                        opt_data = []
                        for feature, values in optimized.items():
                            current_value = input_data.get(feature)
                            if current_value is None:
                                current_value = estimated_missing.get(feature, {}).get('recommended', 'N/A')
                            opt_data.append({
                                'Feature': feature,
                                'Current': current_value,
                                'Range': values.get('range', 'N/A'),
                                'Target': values.get('recommended', 'N/A')
                            })
                        opt_df = pd.DataFrame(opt_data)
                        st.dataframe(opt_df, use_container_width=True, hide_index=True)
                        st.download_button("Download CSV", opt_df.to_csv(index=False), f"{top_crop_name}_optimized.csv", "text/csv")

            except Exception as e:
                st.error(f"Prediction failed: {str(e)}")
                logger.error(f"Prediction error: {str(e)}")

    # ========================================================================
    # PAGE: OPTIMIZE
    # ========================================================================
    elif page == "Optimize":
        st.title("Optimize Crop Yield")
        st.caption("Select a crop and enter current conditions. The model identifies which inputs hurt yield and recommends adjustments.")

        numerical_features = [
            'Temperature', 'Rainfall', 'pH', 'Light_Hours', 'Light_Intensity', 'Rh',
            'Nitrogen', 'Phosphorus', 'Potassium', 'N_Ratio', 'P_Ratio', 'K_Ratio'
        ]
        categorical_features = ['Fertility', 'Photoperiod', 'Category_pH', 'Soil_Type', 'Season']
        crops = sorted(df_train['Name'].unique().tolist())

        selected_crop = st.selectbox("Select crop to optimize", crops, key="opt_crop")

        input_method = st.radio("Input method:", ["Manual", "Sample from dataset", "Template"], horizontal=True, key="opt_method")
        opt_data = {}

        if input_method == "Manual":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Numerical**")
                for feature in numerical_features:
                    opt_data[feature] = st.number_input(f"{feature}", value=0.0, key=f"opt_manual_{feature}")
            with col2:
                st.markdown("**Categorical**")
                opt_data['Fertility'] = st.selectbox("Fertility", df_train['Fertility'].unique().tolist(), key="opt_mfert")
                opt_data['Photoperiod'] = st.selectbox("Photoperiod", df_train['Photoperiod'].unique().tolist(), key="opt_mphoto")
                opt_data['Category_pH'] = st.selectbox("Category_pH", df_train['Category_pH'].unique().tolist(), key="opt_mph")
                opt_data['Soil_Type'] = st.selectbox("Soil_Type", df_train['Soil_Type'].unique().tolist(), key="opt_msoil")
                opt_data['Season'] = st.selectbox("Season", df_train['Season'].unique().tolist(), key="opt_mseason")

        elif input_method == "Sample from dataset":
            sample_row = df_train.sample(1).iloc[0]
            for feature in numerical_features:
                opt_data[feature] = st.number_input(f"{feature}", value=float(sample_row[feature]), key=f"opt_rand_{feature}")
            for feature in categorical_features:
                options = df_train[feature].unique().tolist()
                opt_data[feature] = st.selectbox(feature, options, index=options.index(sample_row[feature]) if sample_row[feature] in options else 0, key=f"opt_rand_{feature}")

        elif input_method == "Template":
            st.info("Select features to provide. Unselected features will be estimated.")
            selected_features = st.multiselect("Choose features:", numerical_features + categorical_features, default=['Temperature', 'Rainfall', 'pH'], key="opt_sel")
            sample_row = df_train.sample(1).iloc[0]
            for feature in selected_features:
                if feature in numerical_features:
                    opt_data[feature] = st.number_input(f"{feature}", value=float(sample_row[feature]), key=f"opt_tpl_{feature}")
                else:
                    opt_data[feature] = st.selectbox(feature, df_train[feature].unique().tolist(), key=f"opt_tpl_{feature}")

        if st.button("Analyze", use_container_width=True, type="primary", key="opt_btn"):
            try:
                result = predictor.predict_for_crop(selected_crop, opt_data)
                optimized = result.get('optimized_conditions', {})
                estimated_missing = result.get('estimated_missing_values', {})
                st.divider()

                if optimized:
                    out = []
                    for feature, values in optimized.items():
                        current = opt_data.get(feature)
                        current_display = current if current is not None else estimated_missing.get(feature, {}).get('recommended', 'N/A')
                        target = values.get('recommended', 'N/A')
                        mean_v = values.get('mean')
                        low = values.get('min')
                        high = values.get('max')

                        if feature in numerical_features and isinstance(current, (int, float)) and low is not None and high is not None:
                            if low <= current <= high:
                                status = "Good"
                                action = "Keep"
                            elif mean_v is not None:
                                direction = "Increase" if current < mean_v else "Decrease"
                                action = f"{direction} to {mean_v:.1f}"
                                status = "Adjust"
                            else:
                                action = f"Move to {target}"
                                status = "Adjust"
                        else:
                            if str(current) == str(target):
                                status = "Good"
                                action = "Keep"
                            else:
                                action = f"Change to {target}"
                                status = "Adjust"

                        out.append({
                            'Feature': feature,
                            'Current': current_display,
                            'Range': values.get('range', 'N/A'),
                            'Target': target,
                            'Action': action,
                            'Status': status
                        })

                    out_df = pd.DataFrame(out)
                    out_df['Status'] = pd.Categorical(out_df['Status'], categories=['Adjust', 'Good'], ordered=True)
                    out_df = out_df.sort_values(['Status', 'Feature'], ascending=[True, True]).drop(columns=['Status'])
                    st.dataframe(out_df, use_container_width=True, hide_index=True)

                    st.download_button("Download CSV", out_df.to_csv(index=False), f"{selected_crop}_optimization.csv", "text/csv")

                    issues = out_df[out_df['Action'] != 'Keep']['Feature'].head(5).tolist()
                    if issues:
                        st.info("Priority adjustments: " + ", ".join(issues))
                    else:
                        st.success("All conditions are optimal for this crop.")
                else:
                    st.info("No optimization suggestions available.")

                if result.get('estimated_yield') is not None:
                    st.metric("Estimated Yield", f"{result['estimated_yield']:.2f}")
            except Exception as e:
                st.error(f"Optimization failed: {str(e)}")
                logger.error(f"Optimization error: {str(e)}")

    # ========================================================================
    # PAGE: BATCH
    # ========================================================================
    elif page == "Batch":
        st.title("Batch Prediction")
        st.caption("Upload a CSV with sensor readings for multiple fields.")

        uploaded_file = st.file_uploader("Upload CSV file", type="csv")

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head(), use_container_width=True)

                if st.button("Run Batch", use_container_width=True, type="primary"):
                    progress = st.progress(0)
                    results = []

                    for idx, row in df.iterrows():
                        try:
                            result = predictor.predict(row.to_dict())
                            result['input_index'] = idx + 1
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Row {idx} error: {str(e)}")
                        progress.progress((idx + 1) / len(df))

                    st.success(f"Processed {len(results)} predictions.")

                    out = []
                    for result in results:
                        top = result['recommended_crops'][0]
                        out.append({
                            'Index': result['input_index'],
                            'Top Crop': top['name'],
                            'Probability': f"{top['probability']:.1%}",
                            'Yield': f"{result['estimated_yield']:.2f}",
                            'Input Type': result['input_type']
                        })

                    out_df = pd.DataFrame(out)
                    st.dataframe(out_df, use_container_width=True, hide_index=True)
                    st.download_button("Download Results", out_df.to_csv(index=False), "batch_predictions.csv", "text/csv")

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    # ========================================================================
    # PAGE: FEATURE ANALYSIS
    # ========================================================================
    elif page == "Analysis":
        st.title("Analysis")

        tab1, tab2 = st.tabs(["Feature Importance", "Data Distribution"])

        with tab1:
            try:
                feat_imp_crop = pd.read_csv(Path(__file__).parent / "models" / "feature_importance_crop.csv")
                feat_imp_crop = feat_imp_crop.rename(columns={'feature': 'Feature', 'importance': 'Importance'})
                fig = px.bar(feat_imp_crop.head(10), x='Importance', y='Feature', orientation='h')
                fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(feat_imp_crop, use_container_width=True, hide_index=True)
            except:
                st.info("Feature importance data not available.")

            try:
                feat_imp_yield = pd.read_csv(Path(__file__).parent / "models" / "feature_importance_yield.csv")
                feat_imp_yield = feat_imp_yield.rename(columns={'feature': 'Feature', 'importance': 'Importance'})
                fig = px.bar(feat_imp_yield.head(10), x='Importance', y='Feature', orientation='h')
                fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(feat_imp_yield, use_container_width=True, hide_index=True)
            except:
                st.info("Feature importance data not available.")

        with tab2:
            numerical_features = [
                'Temperature', 'Rainfall', 'pH', 'Light_Hours', 'Light_Intensity', 'Rh',
                'Nitrogen', 'Phosphorus', 'Potassium', 'N_Ratio', 'P_Ratio', 'K_Ratio'
            ]
            selected_feature = st.selectbox("Select feature:", numerical_features, key="dist_feat")
            fig = px.box(df_train, x='Name', y=selected_feature, height=500)
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # PAGE: ABOUT
    # ========================================================================
    elif page == "About":
        st.title("About CropSense")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Classification Accuracy", "100%")
        with col2:
            st.metric("Yield R²", "0.9946")
        with col3:
            st.metric("Supported Crops", "22")
        with col4:
            st.metric("Input Features", "17")

        st.divider()

        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Models")
            st.markdown("- **Classification**: RandomForestClassifier (200 trees) – 100% test accuracy")
            st.markdown("- **Regression**: RandomForestRegressor (200 trees) – R² = 0.9946")
            st.markdown("- **Imputation**: KNN-based similarity search (k=10) with high-yield filtering")

            st.subheader("Dataset")
            st.markdown("- 15,400 samples (700 per crop)")
            st.markdown("- 17 input features (12 numerical + 5 categorical)")
            st.markdown("- 2 targets: crop name + yield")
            st.markdown("- Yield range: 0.77 – 66.62 units")

        with col_right:
            st.subheader("Supported Crops")
            crops = sorted(df_train['Name'].unique().tolist())
            for crop in crops:
                st.caption(crop)

        st.divider()
        st.caption("Built with scikit-learn, Streamlit, Plotly. See README.md for API and documentation.")


if __name__ == "__main__":
    main()
