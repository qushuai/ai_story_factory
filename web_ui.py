import os
import uuid
import subprocess
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import threading

app = FastAPI()

templates = Jinja2Templates(directory="templates")

LOG_FILE = "run.log"


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
def generate(story: str = Form(...)):

    story_id = str(uuid.uuid4())[:8]

    os.makedirs("stories", exist_ok=True)

    story_path = f"output/stories/{story_id}.txt"

    with open(story_path, "w", encoding="utf-8") as f:
        f.write(story)

    thread = threading.Thread(target=run_pipeline, args=(story_path,))
    thread.start()

    return {"status": "started", "story_id": story_id}


def run_pipeline(story_path):

    with open(LOG_FILE, "w", encoding="utf-8") as log:

        process = subprocess.Popen(
            ["python", "main.py", story_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(line.strip())
            log.write(line)
            log.flush()


@app.get("/logs")
def stream_logs():

    def generate():

        with open(LOG_FILE, "r", encoding="utf-8") as f:

            while True:
                line = f.readline()

                if line:
                    yield line
                else:
                    import time
                    time.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/plain")