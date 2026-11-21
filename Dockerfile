FROM python:3.11-slim

# LIMITAHAN ANG CPU CORES PARA HINDI MAUBOS ANG RAM
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"

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

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
