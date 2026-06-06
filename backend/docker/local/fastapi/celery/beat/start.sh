#!/bin/bash

set -o errexit

set -o nounset

set -o pipefail

export PYTHONPATH=/src/backend

exec watchfiles \
    --filter python \
    --target-type command \
    "celery -A app.core.celery_app beat -l INFO" \
    /src
