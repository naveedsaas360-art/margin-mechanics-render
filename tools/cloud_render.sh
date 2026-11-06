#!/usr/bin/env bash
# Push the project to a private GitHub repo, render an episode on GitHub Actions,
# and download the finished files into renders/<episode>/.
# Usage: bash tools/cloud_render.sh EP01_Costco [output_name]
# Token: a GitHub fine-grained token (Contents, Actions, Administration: read/write)
#        saved as plain text in C:\Users\dell\YouTube\github_token.txt
set -euo pipefail
EP="$1"; ONLY="${2:-}"; REPO_NAME="${REPO_NAME:-margin-mechanics-render}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN="$(tr -d '\r\n ' < "$ROOT/../github_token.txt")"
API="https://api.github.com"
gh_api() { curl -sfL -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" "$@"; }
json() { python -I -c "import json,sys; d=json.load(sys.stdin); print($1)"; }

USER="$(gh_api "$API/user" | json "d['login']")"

latest_run() { gh_api "$API/repos/$USER/$REPO_NAME/actions/runs?per_page=1" \
  | json "d['workflow_runs'][0]['id'] if d['workflow_runs'] else 0"; }

cd "$ROOT"
if [ -z "${RUN:-}" ]; then  # RUN=<id> skips straight to waiting on an existing run
  git -C "$ROOT" add -A >/dev/null 2>&1; git -C "$ROOT" -c user.name="Margin Mechanics" -c user.email=345416375+naveedsaas360-art@users.noreply.github.com commit -qm "render snapshot" >/dev/null 2>&1 || true
  source "$ROOT/tools/push_public.sh"; publish_snapshot
  PREV="$(latest_run)"
  gh_api -X POST "$API/repos/$USER/$REPO_NAME/actions/workflows/render.yml/dispatches" \
    -d "{\"ref\":\"main\",\"inputs\":{\"episode\":\"$EP\",\"only\":\"$ONLY\"}}"
  echo "Render started for $EP"
  for _ in $(seq 1 60); do
    sleep 5; RUN="$(latest_run || echo "$PREV")"
    [ "$RUN" != "$PREV" ] && break
  done
fi
echo "Run: https://github.com/$USER/$REPO_NAME/actions/runs/$RUN"

while :; do
  STATE="$( (gh_api "$API/repos/$USER/$REPO_NAME/actions/runs/$RUN" | json "d['status']+' '+str(d['conclusion'])") 2>/dev/null || echo "unknown x")"
  read -r STATUS CONCL <<< "$STATE"
  [ "$STATUS" = "completed" ] && break; sleep 30
done
echo "Finished: $CONCL"
[ "$CONCL" = "success" ] || exit 1

ART="$(gh_api "$API/repos/$USER/$REPO_NAME/actions/runs/$RUN/artifacts?per_page=50" | json "[a['id'] for a in d['artifacts'] if a['name']=='$EP'][0]")"
# every render gets its own folder, so a video open in a player never blocks the download
DEST="$ROOT/renders/${EP}_$(date +%m%d_%H%M)"
mkdir -p "$DEST"
gh_api -o "$DEST.zip" "$API/repos/$USER/$REPO_NAME/actions/artifacts/$ART/zip"
python -I -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$DEST.zip" "$DEST"
rm "$DEST.zip"
echo "Saved to $DEST"
ls -la "$DEST"
