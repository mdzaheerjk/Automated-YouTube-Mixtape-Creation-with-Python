from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse
import os, glob, traceback

from .utils import new_job, set_job_status, get_job, save_upload_file, ensure_output_dir
from .audio import smooth_fade_mixtape_from_files
from .video import make_video_from_audio
from .description import generate_youtube_description_with_timestamps
from .config import OUTPUT_DIR, ALLOWED_AUDIO_EXT

app = FastAPI(title="Mixtape Automation API")
ensure_output_dir()

# Simple uploads folder for each job
UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), "..", "uploaded")
os.makedirs(UPLOAD_ROOT, exist_ok=True)

@app.post("/upload-track/")
async def upload_track(file: UploadFile = File(...), job_prefix: str = Form(None)):
    """
    Upload a single track. Returns saved path (for debugging). In a real app you'd want proper storage.
    """
    job_prefix = job_prefix or "default"
    dest_dir = os.path.join(UPLOAD_ROOT, job_prefix)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)
    save_upload_file(file, dest_path)
    return {"uploaded": dest_path}

@app.post("/create-mixtape/")
def create_mixtape(background_tasks: BackgroundTasks,
                   job_prefix: str = Form(...),
                   transition_ms: int = Form(6000),
                   output_name: str = Form("mixtape.mp3")):
    """
    Kick off a mixtape creation job that concatenates all tracks present in the job_prefix folder.
    Returns a job_id to poll status.
    """
    job_id = new_job()
    def task():
        try:
            folder = os.path.join(UPLOAD_ROOT, job_prefix)
            files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.lower().endswith(ALLOWED_AUDIO_EXT)]
            if not files:
                set_job_status(job_id, "failed", error="No audio files found")
                return
            set_job_status(job_id, "running")
            out_path = smooth_fade_mixtape_from_files(files, output_filename=output_name, transition_ms=transition_ms)
            set_job_status(job_id, "completed", result=out_path)
        except Exception as e:
            set_job_status(job_id, "failed", error=str(e) + "\n" + traceback.format_exc())

    background_tasks.add_task(task)
    return {"job_id": job_id}

@app.get("/job/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        return JSONResponse({"error": "job not found"}, status_code=404)
    return job

@app.post("/make-video/")
def make_video(background_tasks: BackgroundTasks,
               image_path: str = Form(...),
               audio_path: str = Form(...),
               output_name: str = Form("mixtape_vid.mp4")):
    job_id = new_job()
    def task():
        try:
            set_job_status(job_id, "running")
            out = make_video_from_audio(image_path, audio_path, output_filename=output_name)
            set_job_status(job_id, "completed", result=out)
        except Exception as e:
            set_job_status(job_id, "failed", error=str(e))
    background_tasks.add_task(task)
    return {"job_id": job_id}

@app.post("/generate-description/")
def generate_description(job_prefix: str = Form(...), mixtape_name: str = Form("Mixtape"), genre: str = Form("Mix")):
    folder = os.path.join(UPLOAD_ROOT, job_prefix)
    files = [os.path.join(folder, f) for f in sorted(os.listdir(folder))
             if f.lower().endswith(ALLOWED_AUDIO_EXT)]
    if not files:
        return {"error": "no tracks found"}
    desc = generate_youtube_description_with_timestamps(files, mixtape_name=mixtape_name, genre=genre)
    return {"description": desc}

@app.get("/download/")
def download_file(path: str):
    if not os.path.exists(path):
        return JSONResponse({"error": "file not found"}, status_code=404)
    return FileResponse(path, media_type="application/octet-stream", filename=os.path.basename(path))
