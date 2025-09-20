#!/usr/bin/env bash
set -euo pipefail

SITES_ENABLED="/etc/nginx/sites-enabled"

echo "Updating nginx sites-enabled."
echo "Removing following files:"
ls $SITES_ENABLED
rm "$SITES_ENABLED/*"

echo "Copping files."
cp ./nginx/* $SITES_ENABLED

echo "Reloding nginx."
nginx -t
systemctl reload nginx

echo "Script finished."
