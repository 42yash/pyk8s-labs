from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1")
def read_root():
 return {"message": "Hello from PyK8s-Lab Backend"}