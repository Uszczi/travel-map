#!/bin/bash

set -e

DIRNAME=$(basename "$PWD")
cp /root/pp/.env.$DIRNAME ./.env

docker compose -f ./deployment/docker-compose.yml build
docker compose -f ./deployment/docker-compose.yml run --rm --no-deps app alembic upgrade head
./deployment/update_nginx.sh
docker compose -f ./deployment/docker-compose.yml up --detach
