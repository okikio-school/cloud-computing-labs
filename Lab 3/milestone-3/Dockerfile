FROM ultralytics/ultralytics:latest-python

COPY ./requirements.txt ./

RUN pip install -r ./requirements.txt

# Build
# docker build . -t milestones/m3:latest

# Run
# docker run -it --ipc=host -v "$(pwd)"/Dataset_Occluded_Pedestrian:/datasets milestones/m3:latest