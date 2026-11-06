"""Render this machine's share of every prepared whiteboard video.

Usage: python pipeline/chunks.py <chunk_index> <chunk_count>
Reads out/*_job.json from the prepare stage; writes parts/<name>_<index>.mp4 (video only).
"""
import json, math, subprocess, sys
from pathlib import Path

idx, count = int(sys.argv[1]), int(sys.argv[2])
Path("parts").mkdir(exist_ok=True)
for job_file in sorted(Path("out").glob("*_job.json")):
    job = json.loads(job_file.read_text(encoding="utf-8"))
    size = math.ceil(job["frames"] / count)
    first, last = idx * size, min(job["frames"] - 1, (idx + 1) * size - 1)
    if first > last:
        continue
    out = Path("parts").resolve() / f"{job['name']}_{idx:02}.mp4"
    cmd = ["npx", "remotion", "render", "src/index.js", job.get("comp", "Board"), str(out),
           f"--props=public/mm/{job['name']}_props.json", f"--frames={first}-{last}",
           "--muted", "--codec=h264", "--crf=18"]
    if job.get("comp") == "Story3D":
        cmd += ["--gl=swangle", "--concurrency=2"]  # software WebGL on GPU-less cloud machines
    else:
        cmd += ["--concurrency=100%"]
    print("+", " ".join(cmd), flush=True)
    if subprocess.run(cmd, cwd="whiteboard").returncode != 0:
        # transient decode failures happen under load: one retry with fewer parallel tabs
        cmd = [c for c in cmd if not c.startswith("--concurrency")] + ["--concurrency=2"]
        print("! retrying with lower concurrency:", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True, cwd="whiteboard")
