FROM python:3.10-slim

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requerimientos
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY src/ ./src
COPY docs/ ./docs

CMD ["python", "src/main.py"]

