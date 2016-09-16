#!/bin/bash
pdu_uuid=$1

if [ "$pdu_uuid" == "" ]; then
  exit 1
fi

.tox/py34/bin/arsenal --arsenal_url http://127.0.0.1:7777/ resource-update $pdu_uuid replace /attributes/snmp_address=192.168.0.1
.tox/py34/bin/arsenal --arsenal_url http://127.0.0.1:7777/ resource-update $pdu_uuid replace /attributes/snmp_driver=HELLO_SHIP_IT
