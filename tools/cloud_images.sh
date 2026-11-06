#!/usr/bin/env bash
# Generate an episode's missing AI illustrations on GitHub Actions (FLUX.1-schnell on free CPU runners, one image per job).
# Usage: bash tools/cloud_images.sh EP02_ILLU      (RUN=<id> attaches to an existing run)
set -euo pipefail
EP="$1"; REPO_NAME="${REPO_NAME:-margin-mechanics-render}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN="$(tr -d '\r\n ' < "$ROOT/../github_token.txt")"
API="https://api.github.com"
gh_api() { curl -sfL -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" "$@"; }
json() { python -I -c "import json,sys; d=json.load(sys.stdin); print($1)"; }
USER="$(gh_api "$API/user" | json "d['login']")"
R="$API/repos/$USER/$REPO_NAME"
cd "$ROOT"

python -I tools/gen_images.py "$EP" --cloud
N="$(python -I -c "import json;print(len(json.load(open('$EP/ai_jobs.json'))))")"
[ "$N" = "0" ] && { echo "All images already exist."; exit 0; }

latest_run() { (gh_api "$R/actions/workflows/images.yml/runs?per_page=1" 2>/dev/null || echo "{\"workflow_runs\":[]}") | json "d['workflow_runs'][0]['id'] if d['workflow_runs'] else 0"; }
if [ -z "${RUN:-}" ]; then
  git add -A "$EP" tools .github && git -c user.name="Margin Mechanics" -c user.email=345416375+naveedsaas360-art@users.noreply.github.com commit -qm "$EP: image jobs ($N)" || true
  git -C "$ROOT" add -A >/dev/null 2>&1; git -C "$ROOT" -c user.name="Margin Mechanics" -c user.email=345416375+naveedsaas360-art@users.noreply.github.com commit -qm "render snapshot" >/dev/null 2>&1 || true
  source "$ROOT/tools/push_public.sh"; publish_snapshot
  PREV="$(latest_run)"
  gh_api -X POST "$R/actions/workflows/images.yml/dispatches" -d "{\"ref\":\"main\",\"inputs\":{\"episode\":\"$EP\"}}"
  for _ in $(seq 1 60); do sleep 5; RUN="$(latest_run || echo "$PREV")"; [ "$RUN" != "$PREV" ] && break; done
fi
echo "Image run ($N jobs): https://github.com/$USER/$REPO_NAME/actions/runs/$RUN"
while :; do
  STATUS="$( (gh_api "$R/actions/runs/$RUN" | json "d['status']") 2>/dev/null || echo unknown)"
  [ "$STATUS" = "completed" ] && break; sleep 30
done

TMP="$(mktemp -d)"
gh_api "$R/actions/runs/$RUN/artifacts?per_page=100" | json "' '.join(str(a['id']) for a in d['artifacts'] if a['name'].startswith('img-'))" | tr -d '\r' | tr ' ' '\n' |
while read -r ID; do [ -n "$ID" ] && curl -sfL --max-time 180 -H "Authorization: Bearer $TOKEN" -o "$TMP/$ID.zip" "$R/actions/artifacts/$ID/zip"; done
python -I -c "
import zipfile, glob, pathlib, sys
for z in glob.glob(sys.argv[1] + '/*.zip'):
    zf = zipfile.ZipFile(z)
    for m in zf.namelist():
        pathlib.Path(sys.argv[2], pathlib.Path(m).name).write_bytes(zf.read(m))
" "$TMP" "$ROOT/$EP/ai"
rm -rf "$TMP"
python -I tools/gen_images.py "$EP" --cloud
