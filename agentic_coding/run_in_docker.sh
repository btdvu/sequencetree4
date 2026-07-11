#!/bin/bash
# dev.sh — Cross-Platform & Agent-Friendly Launch Script

# 1. Detect if the environment is interactive (human vs. agent)
if [ -t 0 ]; then
    DOCKER_FLAGS="-it"
else
    # Agent/Headless mode: drop the pseudo-TTY allocation to prevent stalling
    DOCKER_FLAGS="-i"
fi

# 2. Check if a display is actually available
if [ -n "$DISPLAY" ]; then
    HAS_DISPLAY=true
else
    HAS_DISPLAY=false
fi

# 3. Configure OS-specific graphics routing *only* if a display exists
X11_MOUNT=""
DISPLAY_ENV=""

if [ "$HAS_DISPLAY" = true ]; then
    if [ "$(uname)" = "Darwin" ]; then
        echo "🍏 macOS GUI detected. Configuring XQuartz..."
        xhost +localhost > /dev/null 2>&1
        DISPLAY_ENV="host.docker.internal:0"
    else
        echo "🐧 Linux GUI detected. Configuring native X11..."
        xhost +SI:localuser:$(id -un) > /dev/null 2>&1
        DISPLAY_ENV=$DISPLAY
        X11_MOUNT="-v /tmp/.X11-unix:/tmp/.X11-unix"
    fi
else
    echo "🤖 Headless execution detected. Disabling X11 forwarding..."
fi

# 4. Run the container safely
# Added --net=host to ensure the agent's background API calls aren't dropped
docker run $DOCKER_FLAGS --rm \
    --name sequencetree_workspace \
    --net=host \
    -v "$(pwd)":/st_workspace \
    -w /st_workspace \
    $X11_MOUNT \
    ${DISPLAY_ENV:+-e DISPLAY=$DISPLAY_ENV} \
    --user "$(id -u):$(id -g)" \
    sequencetree_env:base "$@"