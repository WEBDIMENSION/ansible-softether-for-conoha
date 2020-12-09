#!/usr/bin/env bash
docker rm -f act-softeher-tests-build
docker rm -f softether_client
docker rm -f softether_server
act push
