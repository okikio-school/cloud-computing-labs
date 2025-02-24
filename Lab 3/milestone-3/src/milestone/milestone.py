from ultralytics import YOLO
from PIL import Image
import depth_pro
import glob

# Load a model
model = YOLO("checkpoints/yolo11n.pt")

# Train the model
# train_results = model.train(
#     data="coco8.yaml",  # path to dataset YAML
#     epochs=100,  # number of training epochs
#     imgsz=640,  # training image size
#     device="cpu",  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
# )

# Evaluate model performance on the validation set
# metrics = model.val()

# Perform object detection on an image
results = model("Dataset_Occluded_Pedestrian/[AC]_*.*")
results[0].show()
print(results[0])

# Export the model to ONNX format
# path = model.export(format="onnx")  # return path to exported model


# Load model and preprocessing transform
# model, transform = depth_pro.create_model_and_transforms()
# model.eval()

# # Load and preprocess an image.
# image, _, f_px = depth_pro.load_rgb(image_path)
# image = transform(image)

# # Run inference.
# prediction = model.infer(image, f_px=f_px)
# depth = prediction["depth"]  # Depth in [m].
# focallength_px = prediction["focallength_px"]  # Focal length in pixels.

# # for a depth-based dataset
# boundary_f1 = SI_boundary_F1(predicted_depth, target_depth)

# # for a mask-based dataset (image matting / segmentation) 
# boundary_recall = SI_boundary_Recall(predicted_depth, target_mask)