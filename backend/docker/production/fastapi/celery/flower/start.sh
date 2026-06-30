#!/bin/bash

set -o errexit

set -o nounset

set -o pipefail

export PYTHONPATH=/src/backend

exec celery \
    -A app.core.celery_app \
    -b "${CELERY_BROKER_URL}" \
    flower \
    --basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"

