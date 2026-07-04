#!/bin/sh
# Build the database + catalog from content/, then serve. Ingest is the only writer;
# the server opens the DB read-only (immutable), so workers scale without contention.
set -e

python -m server.ingest

exec uvicorn server.app:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers "${WEB_CONCURRENCY:-4}" \
    --no-access-log
