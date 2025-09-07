# Use Python 3.9 explicitly
FROM python:3.9.18-slim-bullseye

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "chatapp:app", "--bind", "0.0.0.0:5000"]