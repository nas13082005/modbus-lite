from fastapi import FastAPI

app = FastAPI()

data_store = {}

@app.get("/status")
def status():

    return {"status": "running"}


@app.get("/data")
def data():

    return data_store
