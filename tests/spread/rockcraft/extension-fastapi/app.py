from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "ok"
