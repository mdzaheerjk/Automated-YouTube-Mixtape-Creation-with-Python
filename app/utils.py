import os, uuid, shutil, threading
from fastapi import UploadFile
from .config import OUTPUT_DIR

# Simple in-memory job store (for demo). Replace with DB in production.
JOB_STORE = {}
JOB_STORE_LOCK = threading.Lock()

def new_job():
    job_id = uuid.uuid4().hex
    with JOB_STORE_LOCK:
        JOB_STORE[job_id] = {"status": "pending", "result": None, "error": None}
    return job_id

def set_job_status(job_id, status, result=None, error=None):
    with JOB_STORE_LOCK:
        JOB_STORE[job_id].update({"status": status, "result": result, "error": error})

def get_job(job_id):
    return JOB_STORE.get(job_id)

def save_upload_file(upload_file: UploadFile, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return dest_path

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
