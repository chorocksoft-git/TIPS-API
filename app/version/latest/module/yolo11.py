from ultralytics import YOLO
import numpy as np

model = YOLO("model/best.pt")
#model = YOLO("D:/텍티컬리스트/TIPS_project/runs/detect/train13/weights/best.pt")

# yolo11.py

label = { 
    0: 'Allied Firearms',
    1: 'Allied Uniforms',
    2: 'Allied Equipment',
    3: 'Multicam',
    4: 'Enemy Firearms',
    5: 'Enemy Uniforms',
    6: 'Enemy Equipment',
    7: 'Animals',
    8: 'Civilians',
    9: 'Drones'          # 👈 [추가] 9번 클래스
}

label_initials = {
    0: 'A-F',   
    1: 'A-U',   
    2: 'A-E',   
    3: 'MC',    
    4: 'E-F',   
    5: 'E-U',   
    6: 'E-E',   
    7: 'ANI',   
    8: 'CIV',
    9: 'DRN'            # 👈 [추가] 9번 클래스 이니셜
}

def run_yolo(image):
    results = model(image)
    boxes = results[0].boxes
    return boxes

# --- [추가] 서버 실행 시 1회 자동 웜업 ---
dummy_img = np.zeros((640, 640, 3), dtype=np.uint8) # 1. 까만 빈 이미지 생성
model(dummy_img)
