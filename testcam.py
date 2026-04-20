import cv2

print("Hunting for the camera...")
found_camera = False

# Check the first 5 camera slots
for i in range(5):
    print(f"Testing slot {i}...")
    
    # We let OpenCV pick the best backend automatically this time
    cap = cv2.VideoCapture(i) 
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✅ SUCCESS: Your camera is alive and living at slot {i}!")
            found_camera = True
            cap.release()
            break
    
    cap.release()

if not found_camera:
    print("❌ ERROR: Python checked slots 0-4 and found nothing.")