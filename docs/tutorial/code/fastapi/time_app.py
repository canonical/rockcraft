import datetime

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/time")
def time():
    return {"value": f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"}
