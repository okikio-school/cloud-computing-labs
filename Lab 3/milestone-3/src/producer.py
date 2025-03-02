# environment variable setup for private key file
import os


import glob
import json
import time
import base64
from google.cloud import pubsub_v1  # pip install google-cloud-pubsub

# Search the current directory for the JSON file (including the service account key) 
# to set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];

# TODO : fill project id 
project_id = "cloud-computing-449706"
topic_id = "m3-image"


publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

# Scan the datasets folder for images
image_files = glob.glob("datasets/*.*")  # Adjust for specific formats if needed
for idx, image_path in enumerate(image_files):
    try:
        # Read the image and encode as base64
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

        # Create the Pub/Sub message payload
        message = {
            "ID": os.path.basename(image_path),  # Use the image path as the unique ID
            "Image": encoded_image
        }

        # Publish message to Pub/Sub
        future = publisher.publish(topic_path, json.dumps(message).encode('utf-8'))
        print(f"✅ Sent: {image_path}")

        time.sleep(0.1)  # Small delay to avoid overwhelming the queue

    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")