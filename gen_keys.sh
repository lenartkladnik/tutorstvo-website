#!/usr/bin/env bash
set -e

mkdir -p "./keys"
if [ ! -f "./keys/private_key.pem" ] && [ ! -f "./keys/public_key.pem" ]; then
    docker run --rm -v "$(pwd)/keys:/keys" python:3.13.7-slim bash -c "pip install py-vapid --quiet --root-user-action && cd /keys && vapid --gen"
fi
