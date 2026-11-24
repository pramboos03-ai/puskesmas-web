FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port (default 8000 for Koyeb)
EXPOSE 8000

# Start application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
