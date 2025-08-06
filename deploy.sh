#!/bin/bash

cp /root/pp/.env.travel-map ./.env

docker compose -f ./deployment/docker-compose.yml build
docker compose -f ./deployment/docker-compose.yml stop
docker compose -f ./deployment/docker-compose.yml up --detach
