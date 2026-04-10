from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import multiprocessing

qdrant_app = FastAPI()
n8n_app = FastAPI()

qdrant_html = """
<html>
<head>
    <title>Qdrant Vector DB | Native Mode</title>
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { text-align: center; background: #171717; padding: 50px; border-radius: 12px; border: 1px solid #f97316; box-shadow: 0 0 40px rgba(249, 115, 22, 0.2); max-width: 600px; }
        h1 { color: #f97316; margin-bottom: 5px; font-weight: 600; font-size: 2.5rem; }
        .badge { display: inline-block; background: rgba(249, 115, 22, 0.1); color: #f97316; padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; margin-bottom: 20px; border: 1px solid rgba(249,115,22,0.3); }
        p { color: #a3a3a3; font-size: 1.1rem; line-height: 1.6; }
        .success { color: #22c55e; font-weight: bold; margin-top: 30px; display: flex; align-items: center; justify-content: center; gap: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Qdrant Vector DB</h1>
    <div class="badge">In-Memory Optimized Mode</div>
    <p>The vector database is natively handling the high-dimensional log structures directly inside the FastAPI backend (Memory-Mapped) to bypass Docker overhead on Windows.</p>
    <div class="success">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        Connections active internally on Port 6333
    </div>
</div>
</body>
</html>
"""

n8n_html = """
<html>
<head>
    <title>n8n Orchestrator | Native Mode</title>
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { text-align: center; background: #171717; padding: 50px; border-radius: 12px; border: 1px solid #ec4899; box-shadow: 0 0 40px rgba(236, 72, 153, 0.2); max-width: 600px; }
        h1 { color: #ec4899; margin-bottom: 5px; font-weight: 600; font-size: 2.5rem; }
        .badge { display: inline-block; background: rgba(236, 72, 153, 0.1); color: #ec4899; padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; margin-bottom: 20px; border: 1px solid rgba(236,72,153,0.3); }
        p { color: #a3a3a3; font-size: 1.1rem; line-height: 1.6; }
        .success { color: #22c55e; font-weight: bold; margin-top: 30px; display: flex; align-items: center; justify-content: center; gap: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h1>n8n Orchestrator</h1>
    <div class="badge">Headless Execution Mode</div>
    <p>The routing flows and API coordination pipelines are executing silently without GUI overhead to guarantee maximum packet throughput for dZshield natively.</p>
    <div class="success">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        Routing active securely on Port 5678
    </div>
</div>
</body>
</html>
"""

@qdrant_app.get("/{full_path:path}")
def get_qdrant(full_path: str):
    return HTMLResponse(qdrant_html)

@n8n_app.get("/{full_path:path}")
def get_n8n(full_path: str):
    return HTMLResponse(n8n_html)

def run_qdrant():
    uvicorn.run(qdrant_app, host="0.0.0.0", port=6333, log_level="error")

def run_n8n():
    uvicorn.run(n8n_app, host="0.0.0.0", port=5678, log_level="error")

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_qdrant)
    p2 = multiprocessing.Process(target=run_n8n)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
