from fastapi import FastAPI
import psutil
import docker
import os

app = FastAPI()

try:
    client = docker.from_env()
except Exception:
    client = None

@app.get("/api/status")
def get_status():
    return {
        "system": {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
        },
        "gantry": {
            "status": "online",
            "version": "2026.2.19-2"
        }
    }

@app.get("/api/containers")
def get_containers():
    if not client:
        return {"error": "Docker not accessible"}
    return [{"name": c.name, "status": c.status} for c in client.containers.list()]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
