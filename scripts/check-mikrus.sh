#!/bin/bash

local_travel_map=$(git rev-parse --short HEAD)
local_travel_map_fe=$(cd ../travel-map-fe && git rev-parse --short HEAD)

mikrus_travel_map=$(curl https://api.mateuszpapuga.pl/version -s | jq -r .version)
mikrus_travel_map_fe=$(curl https://mateuszpapuga.pl/api/version -s | jq -r .version)

echo "Local travel-map    : $local_travel_map"
echo "Online travel-map   : $mikrus_travel_map"

echo "Local travel-map-fe : $local_travel_map_fe"
echo "Online travel-map-fe: $mikrus_travel_map_fe"
