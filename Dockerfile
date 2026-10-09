# ─────────────────────────────────────────────────────────────────────────────
# SadTalker + FastAPI wrapper
# Base: wawa9000/sadtalker (includes model weights + all SadTalker deps)
# ─────────────────────────────────────────────────────────────────────────────
FROM wawa9000/sadtalker:latest

WORKDIR /app

# Install FastAPI + Uvicorn on top of the existing environment
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.30.6 \
    python-multipart==0.0.9

# Copy our API server
COPY server.py /app/server.py

# Expose HTTP port
EXPOSE 8000

# API_KEY must be supplied at runtime via -e API_KEY=...
ENV API_KEY=""

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
