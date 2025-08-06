#!/bin/bash

cp /root/pp/.env.travel-map ./.env

docker compose build
docker compose stop
docker compose up
