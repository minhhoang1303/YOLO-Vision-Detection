from ultralytics import YOLO
import cv2

model_path = r"D:\AI\YOLO Vision Detection\projects\coc\runs\train\weights\best.pt"
test_img = r"D:\AI\YOLO Vision Detection\projects\coc\data\images\6338e7dc.jpg"

print(f"Testing model: {model_path}")
model = YOLO(model_path)
print(f"Model classes: {model.names}")

img = cv2.imread(test_img)
if img is None:
    print(f"Cannot read image: {test_img}")
else:
    print(f"Image shape: {img.shape}")
    results = model(img, conf=0.05, device='cpu')
    print(f"Results: {results}")
    
    for r in results:
        boxes = r.boxes
        print(f"Boxes: {len(boxes)}")
        for box in boxes:
            print(f"  Box: {box.xyxy[0].tolist()}, conf: {box.conf[0].item():.4f}, cls: {box.cls[0].item()}")
        
        if len(boxes) > 0:
            annotated = r.plot()
            cv2.imwrite(r"D:\AI\YOLO Vision Detection\debug\result.jpg", annotated)
            print("Saved result to debug/result.jpg")
