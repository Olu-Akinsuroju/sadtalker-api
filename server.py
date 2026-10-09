"""
SadTalker FastAPI wrapper
POST /generate  — multipart form: image (file) + audio (file)
Header: X-API-Key  must match API_KEY env var
Returns: MP4 video file
"""

import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse

app = FastAPI(title="SadTalker API", version="1.0.0")

API_KEY = os.environ.get("API_KEY", "")
SADTALKER_DIR = Path("/app/SadTalker")
RESULTS_DIR = Path("/tmp/sadtalker_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _check_api_key(x_api_key: str | None) -> None:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY env var is not set on the server")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate(
    image: UploadFile = File(..., description="Source face image (jpg/png)"),
    audio: UploadFile = File(..., description="Driving audio (wav/mp3)"),
    x_api_key: str | None = Header(default=None),
):
    _check_api_key(x_api_key)

    job_id = uuid.uuid4().hex
    work_dir = Path(tempfile.mkdtemp(prefix=f"sadtalker_{job_id}_"))

    try:
        # Save uploads to temp dir
        image_path = work_dir / ("input" + Path(image.filename or "input.jpg").suffix)
        audio_path = work_dir / ("input" + Path(audio.filename or "input.wav").suffix)

        for upload, dest in ((image, image_path), (audio, audio_path)):
            with dest.open("wb") as f:
                shutil.copyfileobj(upload.file, f)

        output_dir = work_dir / "output"
        output_dir.mkdir()

        cmd = [
            "python",
            str(SADTALKER_DIR / "inference.py"),
            "--driven_audio", str(audio_path),
            "--source_image", str(image_path),
            "--result_dir", str(output_dir),
            "--still",           # stabilise head pose
            "--preprocess", "full",
        ]

        result = subprocess.run(
            cmd,
            cwd=str(SADTALKER_DIR),
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"SadTalker failed:\n{result.stderr[-2000:]}",
            )

        # Find the generated mp4
        videos = list(output_dir.rglob("*.mp4"))
        if not videos:
            raise HTTPException(status_code=500, detail="SadTalker produced no output file")

        video_path = videos[0]

        # Copy to a persistent results location so FastAPI can serve it
        final_path = RESULTS_DIR / f"{job_id}.mp4"
        shutil.copy(video_path, final_path)

        return FileResponse(
            path=str(final_path),
            media_type="video/mp4",
            filename=f"sadtalker_{job_id}.mp4",
            background=None,
        )

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
