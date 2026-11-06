# Status: paused 2026-11-05 (~17:55 UTC), resume here

## In flight (GitHub Actions, keep running while the PC is off)
1. **Full video EP02_6MIN_FULL** ("The AI Money Loop, Explained in 6 Minutes", 37 scenes, 1,001 words, ~5:45).
   Render run 42073179574. To collect it: `RUN=42073179574 bash tools/cloud_render.sh EP02_6MIN_FULL`
   (if the run failed: rerun failed jobs via API, or `bash tools/cloud_render.sh EP02_6MIN_FULL` again).
   Then: second-by-second QA (previews + qa sheet), thumbnail, upload.md (title, description, chapters, credits, AI disclosure).
2. **Illustrated pilot images EP02_ILLU** (15 FLUX.1-schnell images, storybook style). Image run 42072928979.
   Collect: `RUN=42072928979 bash tools/cloud_images.sh EP02_ILLU` (2 images already local from the HF Space).
   At 35 min the jobs had not finished one image (2 vCPU / 7 GB private runners, Q4 FLUX + swap). If it timed out:
   switch to flux1-schnell-Q3_K_S/Q2_K + t5 Q3, or 1024x576 + upscale; consider a separate public repo for 4 vCPU / 16 GB runners.
   Then check images by eye, `bash tools/cloud_render.sh EP02_ILLU`, QA, deliver the minute.

## Decided today
- User: free options or code only; never ask the user to create accounts or keys.
- Pollinations (anonymous) is now 402/weak; the HF Space works but has a small daily quota per IP.
- Reference formats: Illustrated Storybook Documentary (Time In Minutes) and Animated Case File (Capital Case). After the pilot: a 1-minute Case File test (Rockefeller or Enron).
- Hook rule: shock line, then "In the next 6 minutes you'll see ① ② ③", including one payoff personal to the viewer.
- VoiceStudio (AGPL, CPU Docker) = later upgrade: designed channel voice + dubbing. open-higgsfield = skip (paid API, no license).
