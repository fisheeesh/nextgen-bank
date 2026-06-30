#!/bin/bash

set -o errexit

set -o nounset

set -o pipefail

export PYTHONPATH=/src/backend

python -c "from app.core.ml.cleanup import cleanup_mlflow_runs; cleanup_mlflow_runs()"

exec celery \
    -A backend.app.core.celery_app \
    worker \
    -Q nextgen_tasks,ml_tasks \
    -l INFO
