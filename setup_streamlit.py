#!/usr/bin/env python3
"""
Setup and Install Script for Streamlit Interface
================================================

This script:
1. Installs/updates dependencies
2. Trains models if not available
3. Launches the Streamlit app

Usage:
    python3 setup_streamlit.py
    or
    python setup_streamlit.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


VENV_DIR = Path(__file__).parent / ".venv"


def find_base_python() -> str:
    """Prefer a compatible Python interpreter for the project environment."""
    for candidate in ("python3.11", "python3.12", "python3"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return sys.executable


def get_venv_python() -> Path:
    """Return the Python executable inside the project virtual environment."""
    return VENV_DIR / "bin" / "python"


def get_python_version(python_path: str | Path) -> str:
    """Return the major.minor version string for a Python executable."""
    output = subprocess.check_output([str(python_path), "--version"], text=True).strip()
    return output.replace("Python ", "")


def ensure_virtual_environment(project_dir: Path) -> Path:
    """Create a local virtual environment if it does not already exist."""
    base_python = find_base_python()
    venv_python = get_venv_python()
    expected_version = ".".join(get_python_version(base_python).split(".")[:2])

    if venv_python.exists():
        current_version = ".".join(get_python_version(venv_python).split(".")[:2])
        if current_version != expected_version:
            print(
                f"\n📦 Existing virtual environment uses Python {current_version}, "
                f"recreating with Python {expected_version}..."
            )
            shutil.rmtree(VENV_DIR)
            venv_python = get_venv_python()

    if not venv_python.exists():
        print("\n📦 Creating local virtual environment (.venv)...")
        subprocess.run([base_python, "-m", "venv", str(VENV_DIR)], check=True)
        print("✅ Virtual environment created")

    return venv_python


def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} complete!")
            return True
        else:
            print(f"⚠️ Warning: {description} had issues")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {str(e)}")
        return False


def main():
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("""
    ╔═══════════════════════════════════════════════╗
    ║     🌾 Crop Recommendation System Setup       ║
    ║         Streamlit Web Interface               ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Step 1: Create/activate virtual environment and install dependencies
    print("\n⚙️  STEP 1: Installing/Updating Dependencies")
    venv_python = ensure_virtual_environment(project_dir)

    run_command(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        "Pip upgrade"
    )

    run_command(
        [str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"],
        "Streamlit and dependencies installation"
    )
    
    # Step 2: Check models
    print("\n⚙️  STEP 2: Checking for Trained Models")
    models_dir = project_dir / "models"
    required_files = [
        "crop_classifier.pkl",
        "yield_regressor.pkl",
        "scaler.pkl",
        "label_encoder.pkl",
        "knn_model.pkl"
    ]
    
    missing_models = []
    for file in required_files:
        model_file = models_dir / file
        if not model_file.exists():
            missing_models.append(file)
            print(f"  ⚠️  Missing: {file}")
        else:
            print(f"  ✅ Found: {file}")
    
    if missing_models:
        print(f"\n⚠️  Found {len(missing_models)} missing model files")
        print("   Training models now...")
        
        # Train models using the notebook or pipeline
        train_cmd = [str(venv_python), "run_pipeline.py"]
        if run_command(train_cmd, "Model training"):
            print("✅ Models trained successfully!")
        else:
            print("❌ Model training failed. Please run main.ipynb manually.")
            print(f"   Instructions: {venv_python} run_pipeline.py")
            sys.exit(1)
    else:
        print("✅ All models found!")
    
    # Step 3: Launch Streamlit
    print("\n⚙️  STEP 3: Launching Streamlit App")
    print("\n🚀 Starting Streamlit server...")
    print("   The app will open in your browser at http://localhost:8501")
    print("   Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([str(venv_python), "-m", "streamlit", "run", "streamlit_app.py"], check=False)
    except KeyboardInterrupt:
        print("\n\n👋 Streamlit server stopped.")


if __name__ == "__main__":
    main()
