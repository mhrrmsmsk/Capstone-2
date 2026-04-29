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
    page_title="Crop Recommendation System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            error_msg = "⚠️ Missing trained models:\n"
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
            st.error(f"❌ Dataset not found: {data_path}")
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
        error_msg = f"❌ Error loading system: {str(e)}\n\n"
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
    st.sidebar.title("🌾 Crop Recommendation System")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Select Mode:",
        ["🏠 Home", "📊 Single Prediction", "📈 Batch Prediction", "🔍 Feature Analysis", "ℹ️ About"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📋 System Info
    - **Models**: Classification (100%) + Regression (R²=0.9931)
    - **Crops**: 22 varieties
    - **Features**: 17 input parameters
    - **Status**: 🟢 Production Ready
    """)
    
    # Load system
    predictor, recommender, df_train = load_system()
    
    if predictor is None:
        st.error("⚠️ System failed to load. Please check the model files.")
        return
    
    # ========================================================================
    # PAGE: HOME
    # ========================================================================
    if page == "🏠 Home":
        st.title("🌾 Sensor-Based Crop Recommendation & Yield Optimization")
        st.markdown("### Welcome to the Intelligent Agricultural System")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Classification Accuracy", "100%", "🎯")
        with col2:
            st.metric("Yield Prediction R²", "0.9931", "✓")
        with col3:
            st.metric("Supported Crops", "22", "🌱")
        
        st.markdown("---")
        
        st.markdown("""
        ## 🚀 Features
        
        ### 📊 Single Prediction
        - Input sensor data (complete or partial)
        - Get crop recommendations with probabilities
        - Receive yield predictions
        - Estimate missing values intelligently
        
        ### 📈 Batch Prediction
        - Process multiple sensor readings at once
        - Export results as CSV
        - Perfect for multi-field analysis
        
        ### 🔍 Feature Analysis
        - View feature importance rankings
        - Understand model decisions
        - See crop-specific optimization ranges
        
        ## 📖 How It Works
        
        1. **Complete Data**: Directly predicts using trained models
        2. **Partial Data**: Uses KNN similarity search to estimate missing values
        3. **Optimization**: Suggests optimal ranges for each crop
        
        ## 🎯 Sample Crops
        """)
        
        # Display sample crops
        sample_crops = df_train['Name'].unique()[:12]
        st.write(", ".join(sample_crops))
        
    # ========================================================================
    # PAGE: SINGLE PREDICTION
    # ========================================================================
    elif page == "📊 Single Prediction":
        st.title("📊 Make a Prediction")
        
        # Feature input method
        input_method = st.radio("Select input method:", ["📝 Manual Input", "🎲 Random Values", "📋 Template"])
        
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
        
        if input_method == "📝 Manual Input":
            col1, col2 = st.columns(2)
            
            # Numerical inputs
            with col1:
                st.subheader("📐 Numerical Features")
                for feature in numerical_features:
                    input_data[feature] = st.number_input(
                        f"{feature}",
                        value=0.0,
                        key=f"num_{feature}"
                    )
            
            # Categorical inputs
            with col2:
                st.subheader("🏷️ Categorical Features")
                
                # Get unique values for each categorical feature
                fertility_options = df_train['Fertility'].unique().tolist()
                photoperiod_options = df_train['Photoperiod'].unique().tolist()
                category_ph_options = df_train['Category_pH'].unique().tolist()
                soil_type_options = df_train['Soil_Type'].unique().tolist()
                season_options = df_train['Season'].unique().tolist()
                
                input_data['Fertility'] = st.selectbox("Fertility", fertility_options, key="Fertility")
                input_data['Photoperiod'] = st.selectbox("Photoperiod", photoperiod_options, key="Photoperiod")
                input_data['Category_pH'] = st.selectbox("Category_pH", category_ph_options, key="Category_pH")
                input_data['Soil_Type'] = st.selectbox("Soil_Type", soil_type_options, key="Soil_Type")
                input_data['Season'] = st.selectbox("Season", season_options, key="Season")
        
        elif input_method == "🎲 Random Values":
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
        
        elif input_method == "📋 Template":
            st.info("Select features to include in prediction (leave unchecked to estimate)")
            
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
        if st.button("🚀 Make Prediction", use_container_width=True):
            try:
                result = predictor.predict(input_data)
                
                # Display results
                st.success("✅ Prediction Complete!")
                st.markdown("---")
                
                # Recommended Crops
                st.subheader("🌱 Recommended Crops")
                crops_data = result.get('recommended_crops', [])
                
                if crops_data:
                    col1, col2, col3 = st.columns(3)
                    
                    for idx, (col, crop) in enumerate(zip([col1, col2, col3], crops_data[:3])):
                        with col:
                            prob = crop.get('probability', 0) * 100
                            st.metric(
                                crop['name'],
                                f"{prob:.1f}%",
                                delta=f"Confidence"
                            )
                
                # Create bar chart for recommendations
                crop_names = [c['name'] for c in crops_data[:5]]
                crop_probs = [c['probability'] * 100 for c in crops_data[:5]]
                
                fig = px.bar(
                    x=crop_probs,
                    y=crop_names,
                    orientation='h',
                    title="Top 5 Crop Recommendations",
                    labels={'x': 'Probability (%)', 'y': 'Crop'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Estimated Yield
                st.subheader("📈 Estimated Yield")
                yield_value = result.get('estimated_yield', 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Yield Value", f"{yield_value:.2f} units")
                with col2:
                    st.metric("Input Type", result.get('input_type', 'unknown').upper())
                
                # Missing Values Estimation
                estimated_missing = result.get('estimated_missing_values', {})
                if estimated_missing:
                    st.subheader("🔍 Estimated Missing Values")
                    
                    cols = st.columns(3)
                    for idx, (feature, ranges) in enumerate(list(estimated_missing.items())[:6]):
                        with cols[idx % 3]:
                            st.write(f"**{feature}**")
                            st.write(f"Range: {ranges.get('range', 'N/A')}")
                            st.write(f"Recommended: {ranges.get('recommended', 'N/A')}")
                
                # Optimized Conditions
                optimized = result.get('optimized_conditions', {})
                if optimized:
                    top_crop_name = crops_data[0]['name'] if crops_data else 'Selected Crop'
                    st.subheader(f"✨ Optimized Conditions for {top_crop_name}")
                    st.caption("These are the target values recommended for the selected crop based on similar high-yield samples.")

                    # Create dataframe for better visualization
                    opt_data = []
                    for feature, values in optimized.items():
                        current_value = input_data.get(feature)
                        if current_value is None:
                            current_value = estimated_missing.get(feature, {}).get('recommended', 'N/A')

                        opt_data.append({
                            'Feature': feature,
                            'Current Value': current_value,
                            'Recommended Range': values.get('range', 'N/A'),
                            'Recommended Target': values.get('recommended', 'N/A')
                        })

                    opt_df = pd.DataFrame(opt_data)
                    st.dataframe(opt_df, use_container_width=True)

                    csv = opt_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Optimized Values as CSV",
                        data=csv,
                        file_name=f"{top_crop_name}_optimized_values.csv",
                        mime="text/csv"
                    )
                
                # Explanation
                explanation = result.get('explanation', '')
                if explanation:
                    st.subheader("📝 Explanation")
                    st.info(explanation)

            except Exception as e:
                st.error(f"❌ Prediction failed: {str(e)}")
                logger.error(f"Prediction error: {str(e)}")

        # Separate crop optimization section
        st.markdown("---")
        st.subheader("🎯 Crop Optimization")
        st.caption("Select the crop you want to optimize, then enter the current values. The model will tell you which values are hurting yield and what to change.")

        selected_crop_for_optimization = st.selectbox(
            "Select crop to optimize",
            crops,
            key="selected_crop_for_optimization"
        )

        optimization_input_method = st.radio(
            "How do you want to enter the crop conditions?",
            ["📝 Manual Input", "🎲 Random Values", "📋 Template"],
            key="optimization_input_method"
        )

        optimization_input_data = {}

        if optimization_input_method == "📝 Manual Input":
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Numerical values**")
                for feature in numerical_features:
                    optimization_input_data[feature] = st.number_input(
                        f"{feature}",
                        value=0.0,
                        key=f"opt_num_{feature}"
                    )

            with col2:
                st.markdown("**Categorical values**")
                optimization_input_data['Fertility'] = st.selectbox(
                    "Fertility",
                    df_train['Fertility'].unique().tolist(),
                    key="opt_Fertility"
                )
                optimization_input_data['Photoperiod'] = st.selectbox(
                    "Photoperiod",
                    df_train['Photoperiod'].unique().tolist(),
                    key="opt_Photoperiod"
                )
                optimization_input_data['Category_pH'] = st.selectbox(
                    "Category_pH",
                    df_train['Category_pH'].unique().tolist(),
                    key="opt_Category_pH"
                )
                optimization_input_data['Soil_Type'] = st.selectbox(
                    "Soil_Type",
                    df_train['Soil_Type'].unique().tolist(),
                    key="opt_Soil_Type"
                )
                optimization_input_data['Season'] = st.selectbox(
                    "Season",
                    df_train['Season'].unique().tolist(),
                    key="opt_Season"
                )

        elif optimization_input_method == "🎲 Random Values":
            sample_row = df_train.sample(1).iloc[0]
            for feature in numerical_features:
                optimization_input_data[feature] = st.number_input(
                    f"{feature}",
                    value=float(sample_row[feature]),
                    key=f"opt_rand_{feature}"
                )

            for feature in categorical_features:
                options = df_train[feature].unique().tolist()
                optimization_input_data[feature] = st.selectbox(
                    feature,
                    options,
                    index=options.index(sample_row[feature]) if sample_row[feature] in options else 0,
                    key=f"opt_rand_{feature}"
                )

        elif optimization_input_method == "📋 Template":
            st.info("Select the features you want to provide. Unselected features will be estimated before optimization.")

            selected_features = st.multiselect(
                "Choose features to provide:",
                numerical_features + categorical_features,
                default=['Temperature', 'Rainfall', 'pH'],
                key="optimization_selected_features"
            )

            sample_row = df_train.sample(1).iloc[0]

            for feature in selected_features:
                if feature in numerical_features:
                    optimization_input_data[feature] = st.number_input(
                        f"{feature}",
                        value=float(sample_row[feature]),
                        key=f"opt_template_{feature}"
                    )
                else:
                    optimization_input_data[feature] = st.selectbox(
                        feature,
                        df_train[feature].unique().tolist(),
                        key=f"opt_template_{feature}"
                    )

        if st.button("🔧 Suggest Optimal Values", use_container_width=True, key="optimize_selected_crop_button"):
            try:
                opt_result = predictor.predict_for_crop(selected_crop_for_optimization, optimization_input_data)
                optimized = opt_result.get('optimized_conditions', {})
                estimated_missing = opt_result.get('estimated_missing_values', {})

                st.success(f"✅ Optimization ready for {selected_crop_for_optimization}")
                st.write(
                    "The table below highlights which inputs are hurting yield and what to change for the selected crop."
                )

                if optimized:
                    crop_baseline = df_train[df_train['Name'] == selected_crop_for_optimization]
                    opt_data = []
                    for feature, values in optimized.items():
                        current_value = optimization_input_data.get(feature)
                        current_display = current_value if current_value is not None else estimated_missing.get(feature, {}).get('recommended', 'N/A')
                        target_value = values.get('recommended', 'N/A')

                        if feature in numerical_features and isinstance(current_value, (int, float)):
                            low = values.get('min')
                            high = values.get('max')
                            mean_value = values.get('mean')

                            if low is not None and high is not None and low <= current_value <= high:
                                suggestion = "Looks good"
                                priority = "Low"
                            elif mean_value is not None:
                                direction = "Increase" if current_value < mean_value else "Decrease"
                                suggestion = f"{direction} toward {mean_value:.2f}"
                                priority = "High"
                            else:
                                suggestion = f"Move toward {target_value}"
                                priority = "Medium"
                        else:
                            if str(current_value) == str(target_value):
                                suggestion = "Looks good"
                                priority = "Low"
                            else:
                                suggestion = f"Change to {target_value}"
                                priority = "High"

                        opt_data.append({
                            'Feature': feature,
                            'Current Value': current_display,
                            'Recommended Target': target_value,
                            'Recommended Range': values.get('range', 'N/A'),
                            'What to Change': suggestion,
                            'Priority': priority
                        })

                    opt_df = pd.DataFrame(opt_data)
                    opt_df['Priority'] = pd.Categorical(opt_df['Priority'], categories=['High', 'Medium', 'Low'], ordered=True)
                    opt_df = opt_df.sort_values(['Priority', 'Feature'], ascending=[True, True]).drop(columns=['Priority'])
                    st.dataframe(opt_df, use_container_width=True)

                    csv = opt_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Optimization Suggestions as CSV",
                        data=csv,
                        file_name=f"{selected_crop_for_optimization}_optimization_suggestions.csv",
                        mime="text/csv",
                        key="download_selected_crop_optimization"
                    )

                    problem_features = opt_df[opt_df['What to Change'] != 'Looks good']['Feature'].head(5).tolist()
                    if problem_features:
                        st.warning("Likely limiting inputs: " + ", ".join(problem_features))
                    else:
                        st.success("All provided values are already close to the crop-friendly range.")
                else:
                    st.warning("No optimization suggestions could be generated for the selected crop.")

                if opt_result.get('estimated_yield') is not None:
                    st.metric("Estimated Yield for Selected Crop", f"{opt_result['estimated_yield']:.2f} units")

            except Exception as e:
                st.error(f"❌ Optimization failed: {str(e)}")
                logger.error(f"Optimization error: {str(e)}")
    
    # ========================================================================
    # PAGE: BATCH PREDICTION
    # ========================================================================
    elif page == "📈 Batch Prediction":
        st.title("📈 Batch Prediction")
        
        # Option to upload CSV
        uploaded_file = st.file_uploader("Upload CSV file with sensor data", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                st.subheader("📋 Preview Data")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("🚀 Process All Predictions", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = []
                    
                    for idx, row in df.iterrows():
                        try:
                            result = predictor.predict(row.to_dict())
                            result['input_index'] = idx + 1
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Row {idx} error: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(df))
                        status_text.text(f"Processing: {idx + 1}/{len(df)}")
                    
                    st.success(f"✅ Processed {len(results)} predictions!")
                    
                    # Display results
                    st.subheader("📊 Results Summary")
                    
                    results_df = []
                    for result in results:
                        top_crop = result['recommended_crops'][0]
                        results_df.append({
                            'Index': result['input_index'],
                            'Top Crop': top_crop['name'],
                            'Probability': f"{top_crop['probability']:.2%}",
                            'Estimated Yield': f"{result['estimated_yield']:.2f}",
                            'Input Type': result['input_type']
                        })
                    
                    results_summary = pd.DataFrame(results_df)
                    st.dataframe(results_summary, use_container_width=True)
                    
                    # Download results
                    csv = results_summary.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name="batch_predictions.csv",
                        mime="text/csv"
                    )
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    # ========================================================================
    # PAGE: FEATURE ANALYSIS
    # ========================================================================
    elif page == "🔍 Feature Analysis":
        st.title("🔍 Feature Analysis")
        
        tab1, tab2, tab3 = st.tabs(["📊 Feature Importance", "🎯 Crop Optimization", "📈 Data Distribution"])
        
        with tab1:
            st.subheader("Feature Importance for Crop Classification")
            
            # Load feature importance
            try:
                feat_imp_crop = pd.read_csv(Path(__file__).parent / "models" / "feature_importance_crop.csv")
                feat_imp_crop = feat_imp_crop.rename(columns={
                    'feature': 'Feature',
                    'importance': 'Importance'
                })
                
                fig = px.bar(
                    feat_imp_crop.head(10),
                    x='Importance',
                    y='Feature',
                    orientation='h',
                    title="Top 10 Features for Crop Classification"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(feat_imp_crop, use_container_width=True)
            except:
                st.warning("Feature importance data not available")
            
            st.subheader("Feature Importance for Yield Prediction")
            
            try:
                feat_imp_yield = pd.read_csv(Path(__file__).parent / "models" / "feature_importance_yield.csv")
                feat_imp_yield = feat_imp_yield.rename(columns={
                    'feature': 'Feature',
                    'importance': 'Importance'
                })
                
                fig = px.bar(
                    feat_imp_yield.head(10),
                    x='Importance',
                    y='Feature',
                    orientation='h',
                    title="Top 10 Features for Yield Prediction"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(feat_imp_yield, use_container_width=True)
            except:
                st.warning("Feature importance data not available")
        
        with tab2:
            st.subheader("🎯 Crop-Specific Optimization Ranges")
            
            # Select crop
            crops = sorted(df_train['Name'].unique().tolist())
            selected_crop = st.selectbox("Select crop:", crops)
            
            # Get optimization for crop
            try:
                optimized = recommender.get_optimization_recommendations(selected_crop)
                
                if optimized:
                    opt_data = []
                    for feature, values in optimized.items():
                        opt_data.append({
                            'Feature': feature,
                            'Range': values.get('range', 'N/A'),
                            'Recommended': values.get('recommended', 'N/A')
                        })
                    
                    opt_df = pd.DataFrame(opt_data)
                    st.dataframe(opt_df, use_container_width=True)
                    
                    # Export
                    csv = opt_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Optimization as CSV",
                        data=csv,
                        file_name=f"{selected_crop}_optimization.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No optimization ranges available for the selected crop.")
            except Exception as e:
                st.error(f"Error getting optimization: {str(e)}")
        
        with tab3:
            st.subheader("📈 Feature Distributions by Crop")
            
            # Select features to plot
            numerical_features = [
                'Temperature', 'Rainfall', 'pH', 'Light_Hours', 'Light_Intensity', 'Rh',
                'Nitrogen', 'Phosphorus', 'Potassium', 'N_Ratio', 'P_Ratio', 'K_Ratio'
            ]
            
            selected_feature = st.selectbox("Select feature:", numerical_features)
            
            fig = px.box(
                df_train,
                x='Name',
                y=selected_feature,
                title=f"{selected_feature} Distribution by Crop",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # PAGE: ABOUT
    # ========================================================================
    elif page == "ℹ️ About":
        st.title("ℹ️ About This System")
        
        st.markdown("""
        ## 🌾 Sensor-Based Crop Recommendation & Yield Optimization System
        
        ### 📊 System Overview
        
        This is a production-ready machine learning system that:
        
        - **Recommends optimal crops** based on sensor and soil data
        - **Predicts crop yield** with high accuracy
        - **Handles incomplete data** using intelligent estimation
        - **Provides optimization ranges** for each crop
        
        ### 🎯 Performance Metrics
        
        | Metric | Value |
        |--------|-------|
        | Classification Accuracy | 100% |
        | Regression R² Score | 0.9931 |
        | Regression RMSE | 1.30 units |
        | Supported Crops | 22 varieties |
        | Input Features | 17 parameters |
        
        ### 🔬 Machine Learning Models
        
        **Classification (Crop Recommendation)**
        - Algorithm: RandomForestClassifier (200 trees)
        - Task: Predict crop name from sensor data
        - Accuracy: 100% on test set
        
        **Regression (Yield Prediction)**
        - Algorithm: RandomForestRegressor (200 trees)
        - Task: Predict crop yield value
        - R² Score: 0.9931 (explains 99.31% of variance)
        
        ### 🧠 Missing Value Estimation
        
        When partial data is provided:
        1. **KNN Similarity Search** finds 10 nearest similar samples
        2. **High-Yield Filtering** prioritizes samples with good yields
        3. **Range Estimation** provides min-max-mean-std ranges
        4. **Smart Recommendation** suggests optimal values
        
        ### 📈 Dataset
        
        - **Size**: 15,400 samples
        - **Crops**: 22 unique varieties
        - **Features**: 17 input parameters
        - **Balance**: Perfectly balanced (700 samples per crop)
        - **Yield Range**: 0.77 - 66.62 units
        
        ### 🌱 Supported Crops
        """)
        
        # Display crops in columns
        crops = sorted(df_train['Name'].unique().tolist())
        cols = st.columns(3)
        for idx, crop in enumerate(crops):
            with cols[idx % 3]:
                st.write(f"• {crop}")
        
        st.markdown("""
        ### 📚 Features
        
        **Numerical Features (12)**
        - Temperature, Rainfall, pH
        - Light_Hours, Light_Intensity, Rh
        - Nitrogen, Phosphorus, Potassium
        - N_Ratio, P_Ratio, K_Ratio
        
        **Categorical Features (5)**
        - Fertility (Low/Moderate/High)
        - Photoperiod
        - Category_pH
        - Soil_Type (Loam/Clay/Sandy)
        - Season
        
        ### 🚀 How to Use
        
        1. **Single Prediction**: Input sensor data to get recommendations
        2. **Batch Prediction**: Upload CSV for multi-field analysis
        3. **Feature Analysis**: Explore feature importance and optimization ranges
        
        ### 📝 Technical Stack
        
        - **ML Framework**: scikit-learn
        - **Web Interface**: Streamlit
        - **Data Processing**: pandas, numpy
        - **Visualization**: Plotly
        - **API**: FastAPI
        
        ### 📞 Support
        
        For detailed documentation, see the project README and documentation files.
        """)


if __name__ == "__main__":
    main()
