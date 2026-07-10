#!/bin/bash
# dev.sh — Cross-Platform Launch Script

# Check if the host operating system is a Mac (Darwin)
if [ "$(uname)" = "Darwin" ]; then
    echo "🍏 macOS detected. Configuring XQuartz network routing..."
    
    # 1. Open the local XQuartz network permissions
    xhost +localhost
    
    # 2. Force the display variable to route over the virtual network switch
    DISPLAY_ENV="host.docker.internal:0"
    X11_MOUNT=""
else
    echo "🐧 Linux detected. Configuring native X11 socket routing..."
    
    # Linux native graphics authorizations
    xhost +SI:localuser:$(id -un)
    DISPLAY_ENV=$DISPLAY
    X11_MOUNT="-v /tmp/.X11-unix:/tmp/.X11-unix"
fi

# Run the container with dynamically assigned graphics routing
docker run -it --rm \
    --name sequencetree_workspace \
    -v "$(pwd)":/st_workspace \
    -w /st_workspace \
    $X11_MOUNT \
    -e DISPLAY=$DISPLAY_ENV \
    --user "$(id -u):$(id -g)" \
    sequencetree_env:base "$@"