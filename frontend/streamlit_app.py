import streamlit as st
import requests, time, os

API_BASE = "http://127.0.0.1:8000"  # run uvicorn locally

st.title("YouTube Mixtape Automation")

job_prefix = st.text_input("Job prefix (folder name)", value="job1")

st.header("Upload audio tracks")
uploaded = st.file_uploader("Choose audio files", accept_multiple_files=True, type=["mp3","wav","m4a","aac","ogg","flac"])
if st.button("Upload tracks"):
    for f in uploaded:
        files = {"file": (f.name, f.getvalue())}
        data = {"job_prefix": job_prefix}
        r = requests.post(f"{API_BASE}/upload-track/", files=files, data=data)
        st.write(r.json())

st.header("Create mixtape")
transition_ms = st.number_input("Transition ms", value=6000)
output_name = st.text_input("Output MP3 filename", value="mixtape.mp3")
if st.button("Start mixtape"):
    data = {"job_prefix": job_prefix, "transition_ms": str(transition_ms), "output_name": output_name}
    r = requests.post(f"{API_BASE}/create-mixtape/", data=data)
    st.write(r.json())
    job_id = r.json().get("job_id")
    if job_id:
        st.write("Polling job status...")
        for _ in range(60):
            s = requests.get(f"{API_BASE}/job/{job_id}").json()
            st.write(s)
            if s.get("status") in ("completed","failed"):
                break
            time.sleep(1)

st.header("Generate YouTube description")
mixtape_name = st.text_input("Mixtape name", value="Afro House Mix")
if st.button("Generate description"):
    r = requests.post(f"{API_BASE}/generate-description/", data={"job_prefix": job_prefix, "mixtape_name": mixtape_name, "genre": "Afro House"})
    st.text_area("Description", value=r.json().get("description",""), height=300)

st.header("Make video from mixtape")
image_file = st.file_uploader("Background image", type=["jpg","jpeg","png"])
audio_file_name = st.text_input("Audio path (use output/mixtape.mp3 or uploaded path)", value="output/mixtape.mp3")
video_name = st.text_input("Output video filename", value="mixtape_vid.mp4")
if st.button("Create video"):
    # Save uploaded image locally so API can read it
    if image_file:
        img_path = os.path.join("images", image_file.name)
        os.makedirs("images", exist_ok=True)
        with open(img_path, "wb") as f:
            f.write(image_file.getvalue())
    else:
        st.error("Please upload an image first.")
        img_path = None

    if img_path:
        r = requests.post(f"{API_BASE}/make-video/", data={"image_path": img_path, "audio_path": audio_file_name, "output_name": video_name})
        st.write(r.json())
        job_id = r.json().get("job_id")
        if job_id:
            st.write("Polling video job...")
            for _ in range(120):
                s = requests.get(f"{API_BASE}/job/{job_id}").json()
                st.write(s)
                if s.get("status") in ("completed","failed"):
                    break
                time.sleep(1)
