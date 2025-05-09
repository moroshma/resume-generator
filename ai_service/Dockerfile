# Dockerfile

# --- Stage 1: Base Image ---
FROM python:3.11-slim as base

# --- Set Environment Variables ---
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Set Working Directory ---
WORKDIR /app

# --- Install System Dependencies (if any) ---

# Install fonts needed by fpdf2 for Unicode (e.g., Cyrillic) support
RUN apt-get update && \
    apt-get install -y --no-install-recommends fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*


# --- Install Python Dependencies ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
COPY . .

# --- Expose Port ---
EXPOSE 8080

# --- Define Runtime Command ---

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
