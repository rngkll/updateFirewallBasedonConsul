#!/usr/bin/env bash

CONSULDATA=$1
JQ=$(which jq)

PRODDATA=$($JQ '.[] | select( .NodeMeta.stage == "prod")' ${CONSULDATA})
TESTDATA=$($JQ '.[] | select( .NodeMeta.stage == "test")' ${CONSULDATA})

echo "[prod]" > dynamicInventory/prod
echo "[test]" > dynamicInventory/test

METRICSLIST=$($JQ '. | select( .NodeMeta.env == "metrics").ServiceAddress | tostring' <<< $TESTDATA)
BACKUPSLIST=$($JQ '. | select( .NodeMeta.env == "backups").ServiceAddress | tostring' <<< $TESTDATA)

ML="[$(echo $METRICSLIST | tr -s '[:blank:]' ',')]"
BL="[$(echo $BACKUPSLIST | tr -s '[:blank:]' ',')]"

items=$(echo "$TESTDATA" | jq -c -r '.')
for item in ${items[@]}; do
    HOST=$($JQ -r '.Node' <<< $item)
    AN_HOST=$($JQ -r '.Address' <<< $item)
	echo "$HOST ansible_host=$AN_HOST metrics_list=$ML backups_list=$BL" >> dynamicInventory/test
    # whatever you are trying to do ...
done

