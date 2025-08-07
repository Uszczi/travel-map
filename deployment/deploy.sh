#!/bin/bash

DIRNAME=$(basename "$PWD")
cp /root/pp/.env.$DIRNAME ./.env

docker compose -f ./deployment/docker-compose.yml build
docker compose -f ./deployment/docker-compose.yml up --detach
