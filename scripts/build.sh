#!/bin/sh
set -eu

if [ "$#" -gt 1 ]; then
    printf 'Usage: %s [image-tag]\n' "$0" >&2
    exit 2
fi

project_dir=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
image_tag=${1:-github-api}

exec docker build --file "$project_dir/Dockerfile" --tag "$image_tag" "$project_dir"
