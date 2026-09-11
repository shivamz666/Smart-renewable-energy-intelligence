#!/usr/bin/env python3
"""
Entry point for the Smart Renewable Energy Intelligence Platform backend.
Run: python run.py
Or:  uvicorn backend.main:app --reload --port 8000
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print(" Smart Renewable Energy Intelligence Platform")
    print(" Agentic AI Decision Support — Kutch & Banaskantha")
    print("=" * 65)
    print(" DATA SOURCE: DEMO / SIMULATED DATA")
    print(" SAFETY: Decision-support only. No equipment control.")
    print(" API docs: http://localhost:8000/docs")
    print(" Frontend: http://localhost:3000 (run npm dev separately)")
    print("=" * 65)

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
