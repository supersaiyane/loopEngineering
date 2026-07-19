"""
Sepsis Scoring Service — Sprint 2
FastAPI + ONNX runtime inference
"""
from fastapi import FastAPI

app = FastAPI(title="Sepsis Scoring Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "sepsis-scoring-service"}

# TODO Sprint 2:
# - POST /v1/score — accepts feature vector, returns sepsis probability
# - ONNX model loading at startup
# - Feature pipeline (vitals -> normalized feature vector)
