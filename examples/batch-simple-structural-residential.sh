#!/bin/bash

if [ -z "$TOKEN" ]; then
    printf "please set the TOKEN environment variable\n"
    exit 1
fi
token="$TOKEN"

if [ -z "$1" ]; then

    id1=$(uuidgen)
    id2=$(uuidgen)
    id3=$(uuidgen)
    id4=$(uuidgen)
    ids="[\"$id1\",\"$id2\",\"$id3\",\"$id4\"]"

    printf "uuids to request results for:\n"
    printf "(restart script with this string supplied as first arg to skip straight to the results)\n"
    printf '"[\\"%s\\",\\"%s\\",\\"%s\\",\\"%s\\"]"\n' "$id1" "$id2" "$id3" "$id4"

    printf "\n\n/batch response:\n"
    curl --request POST \
        --url https://api.climaterisk.qa/v1/structural/simple/residential/batch \
        --header "Content-Type: application/json" \
        --header "Authorization: Basic $token" \
        --data "{\"item_id\":\"$id1\",\"geocoding\":{\"address\":\"1-1 Marunouchi, Chiyoda City, Tokyo 100-0005, Japan\"}}
                {\"item_id\":\"$id2\",\"geocoding\":{\"address\":\"221B Baker Street, Marylebone, London NW1 6XE, United Kingdom\"}}
                {\"item_id\":\"$id3\",\"geocoding\":{\"address\":\"75 Pitt Street, Sydney, NSW 2000, Australia\"}}
                {\"item_id\":\"$id4\",\"geocoding\":{\"address\":\"12 Long Street, Cape Town City Centre, 8001, South Africa\"}}"

    printf "\n\n/progress response - note the streaming:\n"
    curl --request POST \
        --no-buffer \
        --url https://api.climaterisk.qa/v1/structural/simple/residential/progress \
        --header "Content-Type: application/json" \
        --header "Authorization: Basic $token" \
        --data "$ids"

else
    ids="$1"
    printf "\n\nuuids provided; skipping straight to results\n"
fi

printf "\n\n/results retrieval:\n"
curl --request POST \
    --no-buffer \
	--no-progress-meter \
    --url https://api.climaterisk.qa/v1/structural/simple/residential/results \
    --header "Content-Type: application/json" \
    --header "Authorization: Basic $token" \
    --data "$ids" >results.json

printf "\n\nresults saved to results.json\n"

cat results.json | tr -d '\36' | jq | less
