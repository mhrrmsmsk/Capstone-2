FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY data/ data/
COPY run_pipeline.py .
COPY streamlit_app.py .

# Train models if not present (can be overridden by mounting a models/ volume)
RUN python run_pipeline.py || echo "Models will need to be trained at runtime"

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Default: run FastAPI server
# Override with: docker run ... streamlit run streamlit_app.py
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
