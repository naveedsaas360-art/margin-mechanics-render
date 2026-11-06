#!/usr/bin/env bash
# Publish a history-free snapshot of HEAD to the PUBLIC render repo (public repos get unlimited free Actions minutes).
# No keys live in the repo; the snapshot commit uses GitHub's no-reply address, so no personal email is published.
# Sourced by cloud_render.sh / cloud_images.sh after they set TOKEN, USER, ROOT. Sets REPO_NAME.
REPO_NAME="${REPO_NAME:-margin-mechanics-render}"
NOREPLY="345416375+naveedsaas360-art@users.noreply.github.com"
publish_snapshot() {
  if ! gh_api "$API/repos/$USER/$REPO_NAME" >/dev/null 2>&1; then
    echo "Creating public render repo $USER/$REPO_NAME"
    gh_api -X POST "$API/user/repos" -d "{\"name\":\"$REPO_NAME\",\"private\":false,\"description\":\"Render pipeline for the Margin Mechanics YouTube channel\"}" >/dev/null
    sleep 3
  fi
  local snap; snap="$(mktemp -d)"
  (cd "$ROOT" && git archive HEAD) | tar -x -C "$snap"
  (cd "$snap" && git init -q && git add -A &&
   git -c user.name="Margin Mechanics" -c user.email="$NOREPLY" commit -qm "snapshot" &&
   git push -qf "https://x-access-token:$TOKEN@github.com/$USER/$REPO_NAME.git" HEAD:main)
  rm -rf "$snap"
}
