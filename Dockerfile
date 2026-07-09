# Use an explicit, long-term support Ubuntu baseline
FROM ubuntu:24.04

# Prevent interactive geometric timezone prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install standard C++ compilation tooling and native Linux Qt5 developer headers
RUN apt-get update && apt-get install -y \
    build-essential \
    qtbase5-dev \
    qt5-qmake \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up our isolated workspace inside the container
WORKDIR /st_workspace

# 2. Copy the frozen legacy archives from your host disk into the container filesystem
COPY third_party/fftw-3.3.10.tar.gz /tmp/
COPY third_party/gsl-2.8.tar.gz /tmp/

# 3. Compile and globally install FFTW from your local archive
RUN cd /tmp && \
    tar -xzf fftw-3.3.10.tar.gz && \
    cd fftw-3.3.10 && \
    ./configure && \
    make -j$(nproc) && \
    make install

# 4. Compile and globally install GSL from your local archive
RUN cd /tmp && \
    tar -xzf gsl-2.8.tar.gz && \
    cd gsl-2.8 && \
    ./configure && \
    make -j$(nproc) && \
    make install

# Clean up temporary build artifacts inside the image to keep the footprint lean
RUN rm -rf /tmp/fftw-* /tmp/gsl-*

# Inform the compiler runtime environment where to immediately find our new libraries
ENV LD_LIBRARY_PATH=/usr/local/lib

# Default action when launching the container is opening a bash shell terminal
CMD ["/bin/bash"]
