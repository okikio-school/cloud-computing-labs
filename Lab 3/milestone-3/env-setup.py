import cv2
import torch
from ultralytics import YOLO

import os

# Set a dedicated cache directory to avoid conflicts on Dataflow workers.
torch_cache_dir = './checkpoints/torch_cache'
# os.makedirs(torch_cache_dir, exist_ok=True)
# os.environ['TORCH_HOME'] = torch_cache_dir

# Alternatively, you can set the cache directory using torch.hub.set_dir:
torch.hub.set_dir(torch_cache_dir)

# ---------------------------
# Model Initialization
# ---------------------------
# Load YOLO model (ensure your checkpoint path is correct)
model = YOLO("./checkpoints/yolov8n.pt") # "checkpoints/yolo11n.pt"

# Load a model (see https://github.com/intel-isl/MiDaS/#Accuracy for an overview)
# model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
# model_type = "DPT_Hybrid"   # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)
model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)

midas = torch.hub.load("intel-isl/MiDaS", model_type, trust_repo=True)

# Move model to GPU if available
if torch.cuda.is_available():
    device = torch.device("cuda")
    print("PyTourch using CUDA")
else:
    device = torch.device("cpu")
    print("PyTourch using CPU")

midas.to(device)
midas.eval()

# Load transforms to resize and normalize the image for large or small model
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

print("Done")