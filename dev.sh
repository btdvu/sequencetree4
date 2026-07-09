#!/bin/bash
# dev.sh

# 1. Grant the container permission to connect to your local desktop's X server/Xwayland
xhost +SI:localuser:$(id -un)

# 2. Spin up the workspace container from the frozen base toolchain image
docker run -it --rm \
    --name sequencetree_workspace \
    -v "$(pwd)":/st_workspace \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    --user "$(id -u):$(id -g)" \
    sequencetree_env:base
