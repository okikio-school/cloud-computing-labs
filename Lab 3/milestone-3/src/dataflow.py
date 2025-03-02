from ultralytics import YOLO
from PIL import Image
import glob

import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt

import argparse
import logging
import base64
import json
import os
import io

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

class ProcessImageDoFn(beam.DoFn):
    def setup(self):
        # Load YOLO model pretrained on COCO (e.g., yolov8n.pt)
        self.yolo_model = YOLO("checkpoints/yolov8n.pt")
        
        # Set up MiDaS for depth estimation.
        model_type = "DPT_Large"  # Change to "MiDaS_small" or "DPT_Hybrid" for higher or lower accuracy.
        self.midas = torch.hub.load("intel-isl/MiDaS", model_type)
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.midas.to(self.device)
        self.midas.eval()
        
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        if model_type in ["DPT_Large", "DPT_Hybrid"]:
            self.transform = midas_transforms.dpt_transform
        else:
            self.transform = midas_transforms.small_transform

    def process(self, element):
        """
        Expects a dict with:
          - "ID": identifier for the image.
          - "Image": a base64-encoded string of the image.
        Returns a dict with the ID and a list of detections; each detection contains the bounding box and average depth.
        """
        image_id = element.get("ID", "unknown")
        image_data = element.get("Image")
        if not image_data:
            yield {"ID": image_id, "error": "No image data provided"}
            return

        try:
            # Decode the base64 string into bytes, then load into a PIL Image.
            image_bytes = base64.b64decode(image_data)
            image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_np = np.array(image_pil)
        except Exception as e:
            yield {"ID": image_id, "error": f"Failed to decode image: {e}"}
            return

        # Run YOLO detection on the image.
        try:
            # Passing the numpy array directly; using a larger resolution (imgsz=1280)
            # and a lower confidence threshold (conf=0.25) to help detect small/distant persons.
            yolo_results = self.yolo_model(
                image_np,
                imgsz=1280,
                conf=0.25,
                stream=True
            )
        except Exception as e:
            yield {"ID": image_id, "error": f"YOLO detection error: {e}"}
            return

        # Filter detections for persons (COCO person class is index 0).
        person_boxes = []
        for result in yolo_results:
            for box in result.boxes:
                if int(box.cls[0]) == 0:
                    person_boxes.append(box)

        # Run MiDaS to compute the full-image depth map.
        try:
            input_batch = self.transform(image_np).to(self.device)
            with torch.no_grad():
                prediction = self.midas(input_batch)
                # Resize the depth map to match the original image resolution.
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=image_np.shape[:2],
                    mode="bicubic",
                    align_corners=False
                ).squeeze()
            depth_map = prediction.cpu().numpy()
        except Exception as e:
            yield {"ID": image_id, "error": f"MiDaS depth estimation error: {e}"}
            return

        # For each detected person, extract the bounding box and compute average depth.
        detections = []
        for box in person_boxes:
            coords = box.xyxy.cpu().numpy()[0]
            x1, y1, x2, y2 = map(int, coords)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image_np.shape[1], x2), min(image_np.shape[0], y2)
            depth_crop = depth_map[y1:y2, x1:x2]
            avg_depth = float(np.mean(depth_crop)) if depth_crop.size > 0 else 0.0
            detections.append({
                "box": [x1, y1, x2, y2],
                "avg_depth": avg_depth
            })

        yield {"ID": image_id, "detections": detections}

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_topic', required=True,
                        help='Input Pub/Sub topic of the form "projects/<PROJECT>/topics/<TOPIC>".')
    parser.add_argument('--output_topic', required=True,
                        help='Output Pub/Sub topic of the form "projects/<PROJECT>/topics/<TOPIC>".')
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    # Pipeline options for Dataflow.
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(topic=known_args.input_topic)
            | "Decode to JSON" >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
            | "Process Images" >> beam.ParDo(ProcessImageDoFn())
            | "Encode to JSON" >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
            | "Write to Pub/Sub" >> beam.io.WriteToPubSub(topic=known_args.output_topic)
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()