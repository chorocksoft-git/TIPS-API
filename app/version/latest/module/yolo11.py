from ultralytics import YOLO
import numpy as np

model = YOLO("model/best.pt")
#model = YOLO("D:/텍티컬리스트/TIPS_project/runs/detect/train13/weights/best.pt")

label = { 0: 'Allied Firearms',
          1: 'Allied Uniforms',
          2: 'Allied Equipment',
          3: 'Multicam',
          4: 'Enemy Firearms',
          5: 'Enemy Uniforms',
          6: 'Enemy Equipment',
          7: 'Animals',
          8: 'Civilians',}

label_initials = {
    0: 'A-F',   # Allied Firearms
    1: 'A-U',   # Allied Uniforms
    2: 'A-E',   # Allied Equipment
    3: 'MC',    # Multicam
    4: 'E-F',   # Enemy Firearms
    5: 'E-U',   # Enemy Uniforms
    6: 'E-E',   # Enemy Equipment
    7: 'ANI',   # Animals
    8: 'CIV'    # Civilians
}

def run_yolo(image):
    results = model(image)
    boxes = results[0].boxes
    return boxes

# --- [추가] 서버 실행 시 1회 자동 웜업 ---
dummy_img = np.zeros((640, 640, 3), dtype=np.uint8) # 1. 까만 빈 이미지 생성
model(dummy_img)
