# Stage 0: GCP Apache Beam base dependencies
FROM apache/beam_python3.9_sdk:2.63.0 AS beam

# Stage 1: Build dependencies and setup environment
FROM ultralytics/ultralytics:8.3.81-cpu AS builder
WORKDIR /root

# Copy the checkpoints
COPY checkpoints ./checkpoints

# Copy just the requirements file first so that Docker can cache the pip install step
COPY requirements.txt .

# Install dependencies using a dedicated pip cache directory
RUN --mount=type=cache,target=/root/.cache/pip uv pip install --system --compile-bytecode --cache-dir=/root/.cache/pip -r requirements.txt

# Optionally copy the pip cache if you plan to add more dependencies later
# COPY --from=builder /root/.cache /root/.cache

# Optionally copy the checkpoint files
# COPY --from=builder /root/checkpoints /root/checkpoints

# Copy files from official SDK image, including script/dependencies.
COPY --from=beam /opt/apache/beam /opt/apache/beam

# This image now has all dependencies and caches baked in;
# no pip install will run on container bootup.
CMD ["bash"]

# Set the entrypoint to Apache Beam SDK launcher.
# ENTRYPOINT ["/opt/apache/beam/boot"]


# Build
# docker build . -t milestones/m3:latest

# Run
# docker run -it --ipc=host -v "$(pwd)"/Dataset_Occluded_Pedestrian:/datasets milestones/m3:latest

# Run (via docker-compose)
# docker compose up -d