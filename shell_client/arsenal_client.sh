#!/bin/bash

server=${ARSENAL_URL:-"http://127.0.0.1:7777"}
action=$1; shift
args=${@}

server_curl="curl -s ${server}"

case $action in
resource-create)
  echo "hello"
  ;;
resource-list)
  ${server_curl}/v1/resources | jq .resources
  ;;
*)
  echo "Sorry, unsupported."
  ;;
esac


