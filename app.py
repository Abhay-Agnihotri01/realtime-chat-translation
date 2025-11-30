import uvicorn
import sys
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

sys.path.append('./backend')
from backend.main import app

# Mount static files (built React app)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
