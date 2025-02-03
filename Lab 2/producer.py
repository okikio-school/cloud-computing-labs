from google.cloud import pubsub_v1      # pip install google-cloud-pubsub  ##to install
import glob                             # for searching for json file 
import json
import os 

# Search the current directory for the JSON file (including the service account key) 
# to set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];

# Set the project_id with your project ID
project_id="cloud-computing-448508";
topic_name = "imagesData";   # change it for your topic name if needed

# create a publisher and get the topic path for the publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)
print(f"Published messages with ordering keys to {topic_path}.")
 

# Define the image directory
image_files = list(glob.glob("./Dataset_Occluded_Pedestrian/*.*")) 

# Publish each image
for image_path in image_files:
    # Read the image file in binary mode
    with image_path.open("rb") as img_file:
        image_data = img_file.read()

    # Extract the image name
    image_name = image_path.name

    # send the image
    print("Producing a record: {}".format(image_name))
    future = publisher.publish(topic_path, image_data, key=image_name)
    #ensure that the publishing has been completed successfully
    future.result()

    # send the value    
    future = publisher.publish(topic_path, message);
    
    
    future.result()