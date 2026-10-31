from fastapi import FastAPI

app = FastAPI(title="LiveLink Engine")

@app.get("/")
def home():
    return {"Message" : "Welcome to LiveLink engine"}