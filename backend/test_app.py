#!/usr/bin/env python
"""Minimal test app to verify HTTP server works"""
import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "OK", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting test app...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
