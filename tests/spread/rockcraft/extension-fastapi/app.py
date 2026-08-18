from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()
APP_DATA_TEST_FILE = Path("/app-data/fastapi-write-test.txt")


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "ok"


@app.post("/write-app-data", response_class=PlainTextResponse)
def write_app_data():
    APP_DATA_TEST_FILE.write_text("written by FastAPI\n", encoding="utf-8")
    return "written"
