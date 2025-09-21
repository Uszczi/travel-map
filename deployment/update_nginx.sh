#!/usr/bin/env bash
set -euo pipefail

if [[ "$(basename "$PWD")" != "deployment" ]]; then
  if [[ -d "deployment" ]]; then
    cd deployment
  else
    echo "ERROR: Nie znaleziono katalogu 'deployment' względem bieżącego katalogu: $PWD" >&2
    exit 1
  fi
fi

SITES_ENABLED="/etc/nginx/sites-enabled"

echo "Updating nginx sites-enabled."
echo "Removing files."
rm -f "$SITES_ENABLED/default" \
      "$SITES_ENABLED/api.conf" \
      "$SITES_ENABLED/grafana.conf" \
      "$SITES_ENABLED/prometheus.conf"

echo "Copying files."
cp ./nginx/* "$SITES_ENABLED"

echo "Reloading nginx."
nginx -t
systemctl reload nginx

echo "Script finished."
