#!/bin/bash

export GOPATH=$GOPATH:`cd .. && pwd`
echo $GOPATH
GOOS=linux GOARCH=amd64 go build -v -o sync-s sync-server
GOOS=linux GOARCH=amd64 go build -v -o sync-c sync-client
GOOS=linux GOARCH=amd64 go build -v -o analyse analyse-log
