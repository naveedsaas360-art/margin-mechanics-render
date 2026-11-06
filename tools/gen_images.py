"""Generate illustrated scene images (FLUX.1-schnell, free, no account) for every element with an "ai" prompt.

Provider: the public Hugging Face Space black-forest-labs/FLUX.1-schnell via its Gradio HTTP API (anonymous).
Images are saved in <episode>/ai/ as JPG and committed, so the cloud render needs no generator access.
Usage: python -I tools/gen_images.py EPxx
"""
import hashlib, json, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPACE = "https://black-forest-labs-flux-1-schnell.hf.space/gradio_api"
UA = {"User-Agent": "MarginMechanics/1.0 (educational YouTube channel)"}
STYLE = ("warm hand-drawn storybook illustration, clean black ink outlines, soft watercolor wash, cream paper texture, "
         "muted earthy colors with green and red accents, documentary explainer style, detailed background, "
         "16:9 wide composition, no text, no words, no letters, no logos")
CHAR = ("a simple cartoon man with a big perfectly round bald white head, two small black dot eyes, thin eyebrows, "
        "no nose, no hair, wearing a mustard yellow jacket and a navy scarf")
W, H = 1344, 768


def build_prompt(p):
    return f"{p.replace('{char}', CHAR)}, {STYLE}"


def _post(url, body):
    req = urllib.request.Request(url, json.dumps(body).encode(), {**UA, "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def generate(prompt, seed, out):
    for attempt in range(6):
        try:
            ev = _post(f"{SPACE}/call/infer", {"data": [prompt, seed, False, W, H, 4]})["event_id"]
            stream = urllib.request.urlopen(urllib.request.Request(f"{SPACE}/call/infer/{ev}", headers=UA), timeout=300).read().decode()
            if "event: complete" not in stream:
                raise RuntimeError(stream.strip().splitlines()[-1][:200] if stream.strip() else "empty")
            data = json.loads(stream.split("event: complete", 1)[1].split("data:", 1)[1].strip().splitlines()[0])
            tmp = out.with_suffix(".webp")
            tmp.write_bytes(urllib.request.urlopen(urllib.request.Request(data[0]["url"], headers=UA), timeout=120).read())
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-q:v", "2", str(out)], check=True)
            tmp.unlink()
            return True
        except Exception as e:
            print(f"   retry {attempt + 1}: {e}", flush=True)
            time.sleep(30 * (attempt + 1))
    return False


def main(ep, cloud=False):
    """cloud=True: don't generate here; write <ep>/ai_jobs.json for .github/workflows/images.yml
    (tools/cloud_images.sh runs it, drops <key>.png files into <ep>/ai/, then calls this again)."""
    path = ROOT / ep / "scenes.json"
    cfg = json.loads(path.read_text(encoding="utf-8"))
    outdir = ROOT / ep / "ai"
    outdir.mkdir(exist_ok=True)
    done, failed, jobs = {}, 0, {}
    for o in cfg["outputs"]:
        for s in o["scenes"]:
            for e in s["elements"]:
                if not e.get("ai"):
                    continue
                prompt = build_prompt(e["ai"])
                seed = e.get("seed", 7)
                key = hashlib.sha1(f"{prompt}|{seed}".encode()).hexdigest()[:12]
                f = outdir / f"{key}.jpg"
                png = f.with_suffix(".png")
                if not f.exists() and png.exists():
                    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(png), "-q:v", "2", str(f)], check=True)
                    png.unlink()
                if not f.exists() and cloud:
                    jobs[key] = {"file": png.name, "prompt": prompt, "seed": seed}
                    continue
                if key not in done and not f.exists():
                    print(f"-> {e['ai'][:70]}", flush=True)
                    if not generate(prompt, seed, f):
                        print("   ! failed", flush=True); failed += 1
                        continue
                done[key] = True
                e.update(type="shot", kind="image", local=f"{ep}/ai/{f.name}",
                         credit="AI-generated illustration (FLUX.1-schnell, Black Forest Labs)")
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / ep / "ai_jobs.json").write_text(json.dumps(list(jobs.values()), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"images ready: {len(done)}, failed: {failed}, cloud jobs: {len(jobs)}")


if __name__ == "__main__":
    main(sys.argv[1], cloud="--cloud" in sys.argv)
