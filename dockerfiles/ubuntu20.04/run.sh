#!/usr/bin/env bash
docker build . -t softether_client
docker run -itd --privileged  --name sc sc
#docker run -itd --privileged -v <host_dir>:<container_dir> -p <host_port>:<container_port> --name <container_name> <image_tag>
docker exec -it sc bash
