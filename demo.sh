#!/bin/bash
.tox/py34/bin/arsenal --arsenal_url http://127.0.0.1:7777/ resource-create -t server -a ironic_driver=fake -a cpu_count=2 -a cpu_cores=4 -a ram=1024 -a disk=480
.tox/py34/bin/arsenal --arsenal_url http://127.0.0.1:7777/ resource-create -t server -a ironic_driver=fake -a cpu_count=2 -a cpu_cores=4 -a ram=1536 -a disk=800
.tox/py34/bin/arsenal --arsenal_url http://127.0.0.1:7777/ resource-create -t server -a ironic_driver=fake -a cpu_count=2 -a cpu_cores=4 -a ram=2048 -a disk=2000

server_list=$(.tox/py34/bin/arsenal --json --arsenal_url http://127.0.0.1:7777/ resource-list | jq -r '.[].uuid')

relations=""
i=1
for server in $server_list; do
    relations="${relations} -r $i=$server"
    i=$(($i+1))
done

.tox/py34/bin/arsenal --arsenal_url http://127.0.0.1:7777/ resource-create -t pdu \
    -a snmp_driver=apc_rackpdu -a snmp_address=127.0.0.1 -a snmp_port=1161 \
    $relations

