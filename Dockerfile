FROM python:3.11-slim

# Mag-install ng mga kailangan para gumana ang dlib at OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopyahin ang requirements at i-install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopyahin ang app code
COPY app.py .

# Expose port (Render requirement)
EXPOSE 10000

# Patakbuhin gamit ang gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
