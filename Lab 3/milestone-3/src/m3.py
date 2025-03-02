from ultralytics import YOLO
from PIL import Image
import glob

import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# Model Initialization
# ---------------------------
# Load YOLO model (ensure your checkpoint path is correct)
model = YOLO("checkpoints/yolov8n.pt") # "checkpoints/yolo11n.pt"

# Set up MiDaS model
model_type = "DPT_Large"  # Adjust model type as needed (e.g., "DPT_Large" for higher accuracy)
midas = torch.hub.load("intel-isl/MiDaS", model_type)

# Move model to GPU if available
if torch.cuda.is_available():
    device = torch.device("cuda")
    print("PyTourch using CUDA")
else:
    device = torch.device("cpu")
    print("PyTourch using CPU")

midas.to(device)
midas.eval()

# Load MiDaS transforms
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
if model_type in ["DPT_Large", "DPT_Hybrid"]:
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform

# ---------------------------
# Process Images from Glob
# ---------------------------
# Use glob to obtain a list of image paths (update the pattern as needed)
img_paths = glob.glob("/datasets/[AC]_*.*")
# img_paths = glob.glob("/datasets/A_004.png")

if not img_paths:
    print("No images found with the given glob pattern.")

# Loop over each image
for img_path in img_paths:
    print(f"\nProcessing image: {img_path}")
    
    # Load image using PIL and convert to a NumPy array (RGB)
    image_pil = Image.open(img_path).convert("RGB")
    image_np = np.array(image_pil)
    
    # ---------------------------
    # YOLO Object Detection
    # ---------------------------
    # Run YOLO detection on the image (stream mode returns a list of results)
    results = model(
        img_path, 
        stream=True, 
        imgsz=1280,   # Increase resolution to help detect small/distant objects
        conf=0.25     # Lower confidence threshold to catch smaller or partially occluded persons
    )
    
    # Filter detections to pedestrians only (assuming class index 0 represents a person)
    person_boxes = []
    for result in results:
        # print("=== YOLO Detection Result ===")
        # print("Boxes:", result.boxes)
        # print("Masks:", result.masks)
        # print("Keypoints:", result.keypoints)
        # print("Probabilities:", result.probs)
        # print("OBB:", result.obb)
        
        for box in result.boxes:
            if int(box.cls[0]) == 0:
                person_boxes.append(box)
    
    # print("Filtered Person Boxes:", person_boxes)
    
    # ---------------------------
    # MiDaS Full Image Depth Estimation
    # ---------------------------
    # Prepare the full image for depth estimation
    input_batch = transform(image_np).to(device)
    
    with torch.no_grad():
        prediction = midas(input_batch)
        # Resize the prediction to the original image resolution
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=image_np.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()
    depth_map = prediction.cpu().numpy()
    
    # ---------------------------
    # Compute and Print Pedestrian Depth Information
    # ---------------------------
    print("\n--- Pedestrian Depth Estimates ---")
    for idx, box in enumerate(person_boxes):
        # Get bounding box coordinates
        coords = box.xyxy.cpu().numpy()[0]
        x1, y1, x2, y2 = map(int, coords)
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image_np.shape[1], x2)
        y2 = min(image_np.shape[0], y2)
        
        # Extract the corresponding region from the depth map and compute average depth
        depth_crop = depth_map[y1:y2, x1:x2]
        avg_depth = np.mean(depth_crop)
        
        print(f"Pedestrian {idx+1}: Bounding Box [x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}], Average Depth: {avg_depth:.4f}")
    
    # ---------------------------
    # Optional Visualization
    # ---------------------------
    # Normalize the depth map for visualization
    depth_min, depth_max = depth_map.min(), depth_map.max()
    depth_norm = (depth_map - depth_min) / (depth_max - depth_min + 1e-6)
    depth_vis = (depth_norm * 255).astype(np.uint8)
    depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_PLASMA)
    
    # Overlay YOLO person bounding boxes on the depth map visualization
    for box in person_boxes:
        coords = box.xyxy.cpu().numpy()[0]
        x1, y1, x2, y2 = map(int, coords)
        cv2.rectangle(depth_vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(depth_vis, cv2.COLOR_BGR2RGB))
    plt.title(f"Depth Map with Pedestrian Bounding Boxes: {img_path}")
    plt.axis("off")
    plt.show()