#!/bin/bash
set -e

SERVICE_TYPE="$1"

echo "Docker entrypoint executing for service type: $SERVICE_TYPE"

if [ "$SERVICE_TYPE" = "web" ]; then
    echo "Dispatching to web_setup.sh"
    exec /app/scripts/web_setup.sh
elif [ "$SERVICE_TYPE" = "celery_worker" ]; then
    echo "Dispatching to celery_setup.sh"
    exec /app/scripts/celery_setup.sh
else
    echo "Unknown service type: $SERVICE_TYPE"
    echo "Executing command: $@"
    exec "$@"
fi
