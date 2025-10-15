FROM python:3.11-slim

# Set working directory inside the container (Docker will create it)
WORKDIR /app

# Copy dependencies and install
# assuming requirements.txt is in the models folder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download spacy model
RUN python -m spacy download en_core_web_sm

# Copy your Python file and model files explicitly
# assuming all these files are in the local models folder (the build context)
COPY Main.py .
COPY fake_news_model_fixed_svc.pkl .
COPY granular_fake_news_model_final_C1.0.pkl .


# Expose Cloud Run port
EXPOSE 8080

# Run FastAPI with uvicorn on 0.0.0.0:$PORT
CMD ["sh", "-c", "uvicorn Main:app --host 0.0.0.0 --port ${PORT:-8080}"]