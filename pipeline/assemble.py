"""Join rendered chunks in order and add narration, pen sound and music -> out/<name>.mp4."""
import json, subprocess
from pathlib import Path

MM = Path("whiteboard/public/mm")
for job_file in sorted(Path("out").glob("*_job.json")):
    job = json.loads(job_file.read_text(encoding="utf-8"))
    name, dur = job["name"], job["duration"]
    parts = sorted(Path("parts").glob(f"{name}_[0-9][0-9].mp4"))
    lst = Path("parts") / f"{name}.txt"
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts))
    inputs = ["-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(MM / job["audio"])]
    mix, labels = [], ["[1:a]"]
    if job.get("sfx"):
        inputs += ["-i", str(MM / job["sfx"])]
        mix.append(f"[{len(labels) + 1}:a]volume=0.5[s]")
        labels.append("[s]")
    if job.get("music"):
        m = job["music"]
        inputs += ["-stream_loop", "-1", "-i", str(MM / m["file"])]
        mix.append(f"[{len(labels) + 1}:a]volume={m['volume']},afade=t=in:d=1.5,"
                   f"afade=t=out:st={max(0, dur - 2.5):.2f}:d=2.5[m]")
        labels.append("[m]")
    mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(mix),
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-t", str(dur), "-movflags", "+faststart", f"out/{name}.mp4"]
    print("+", " ".join(cmd), f"({len(parts)} parts)", flush=True)
    subprocess.run(cmd, check=True)
    job_file.unlink()
