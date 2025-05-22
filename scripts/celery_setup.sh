#!/bin/bash
set -e

echo "Starting Celery worker..."
exec celery -A CVProject worker --loglevel=info
