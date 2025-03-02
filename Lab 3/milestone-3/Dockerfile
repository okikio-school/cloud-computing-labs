# Stage 0: GCP Apache Beam base dependencies
FROM apache/beam_python3.12_sdk:2.63.0 AS beam

# Stage 1: Build dependencies and setup environment
FROM ultralytics/ultralytics:8.3.81-cpu AS builder
WORKDIR /root

# Favor hardlinking if supported by ensuring both the pip cache and installation are on the same filesystem.
# Removes uv pip warnings about docker not being the same filesystem
ENV UV_LINK_MODE=hardlink


# Copy the checkpoints
COPY checkpoints ./checkpoints

# Copy just the requirements file first so that Docker can cache the pip install step
COPY requirements.txt .

# Install dependencies using a dedicated pip cache directory
RUN --mount=type=cache,target=/root/.cache/pip uv pip install --system --compile-bytecode --cache-dir=/root/.cache/pip -r requirements.txt

# Copy files from official SDK image, including script/dependencies.
COPY --from=beam /opt/apache/beam /opt/apache/beam

# This image now has all dependencies and caches baked in;
# no pip install will run on container bootup.
CMD ["bash"]

# Set the entrypoint to Apache Beam SDK launcher.
ENTRYPOINT ["/opt/apache/beam/boot"]


# Build
# docker build . -t milestones/m3:latest

# Run
# docker run -it --ipc=host -v "$(pwd)"/Dataset_Occluded_Pedestrian:/datasets milestones/m3:latest

# Run (via docker-compose)
# docker compose up -d