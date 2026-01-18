FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
# Note: We expect TOGETHER_API_KEY to be passed as an env var at runtime
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
