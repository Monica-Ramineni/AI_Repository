from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

handler = Mangum(app) 