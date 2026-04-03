import uvicorn

def app_factory():
    from src.app import app
    return app

if __name__ == "__main__":
    uvicorn.run("main:app_factory", host="0.0.0.0", port=8080, workers=1, reload=True, factory=True)