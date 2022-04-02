#!/usr/bin/env bash

CONSULDATA=$1
JQ=$(which jq)

PRODDATA=$($JQ '.[] | select( .NodeMeta.stage == "prod")' ${CONSULDATA})
TESTDATA=$($JQ '.[] | select( .NodeMeta.stage == "test")' ${CONSULDATA})

echo "[prod]" > dynamicInventory/prod
echo "[test]" > dynamicInventory/test

METRICSLIST=$($JQ '. | select( .NodeMeta.env == "metrics").ServiceAddress | tostring' <<< $TESTDATA)

ML="[$(echo $METRICSLIST | tr -s '[:blank:]' ',')]"

items=$(echo "$TESTDATA" | jq -c -r '.')
for item in ${items[@]}; do
    HOST=$($JQ -r '.Node' <<< $item)
    AN_HOST=$($JQ -r '.Address' <<< $item)
	echo "$HOST ansible_host=$AN_HOST metric_list=$ML" >> dynamicInventory/test
    # whatever you are trying to do ...
done

