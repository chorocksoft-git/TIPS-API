import io
import os
from datetime import datetime

from PIL import Image
from fastapi import APIRouter, File, UploadFile
from module.yolo11 import run_yolo, label, label_initials

# schema import
from schema.schema import (
    DetectionBoxExtended, DetectionResponse, AnalysisSummary,
    DetectionWHNormExtended, DetectionResponseWHNorm,
    DetectionXYXYNormExtended, DetectionResponseXYXYNorm
)

ai_router = APIRouter(
    prefix="/ai/latest",
    responses={404: {"description": "Not found"}},
    tags=["latest"]
)

# ---------------------------------------------------------
# [설정] 이미지 저장 경로 설정
# ---------------------------------------------------------
UPLOAD_DIR = "./uploaded_images"
RESULT_DIR = "./saved_results"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

# ---------------------------------------------------------
# [Constants] 거리 계산용 클래스별 평균 실제 크기(m) 정의
# ---------------------------------------------------------
FOCAL_LENGTH_FACTOR = 1000   # 임의의 초점 거리 상수 (Pixel 단위, 현장 튜닝 필요)

# 각 인식 물체의 대략적인 평균 높이(m) 정의
CLASS_HEIGHTS = {
    0: 0.8,  # Allied Firearms (총기류 대략적 길이)
    1: 1.7,  # Allied Uniforms (사람 평균 키)
    2: 1.0,  # Allied Equipment (군장, 헬멧 등)
    3: 1.7,  # Multicam (사람 평균 키)
    4: 0.8,  # Enemy Firearms (총기류)
    5: 1.7,  # Enemy Uniforms (사람 평균 키)
    6: 1.0,  # Enemy Equipment (군장, 헬멧 등)
    7: 0.6,  # Animals (군견 등 동물 평균 높이)
    8: 1.7,  # Civilians (사람 평균 키)
    9: 0.5,  # Drones (드론 평균 두께/높이)
}

# ---------------------------------------------------------
# [Helper Functions] 비즈니스 로직
# ---------------------------------------------------------

def save_image_file(image_bytes: bytes, filename: str) -> str:
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        print(f"[INFO] Uploaded image saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"[ERROR] Failed to save uploaded image: {e}")
        return None

def save_result_image(results, filename: str) -> str:
    filepath = os.path.join(RESULT_DIR, f"result_{filename}")
    try:
        im_array = results[0].plot()
        im = Image.fromarray(im_array[..., ::-1])  # RGB 변환
        im.save(filepath)
        print(f"[INFO] Result image saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"[ERROR] Failed to save result image: {e}")
        return None


def calculate_distance(box_height_px: float, cls_id: int) -> float:
    """
    클래스별 평균 크기(CLASS_HEIGHTS)와 픽셀 높이를 이용하여 거리를 계산합니다.
    """
    if box_height_px <= 0:
        return 0

    real_height = CLASS_HEIGHTS.get(cls_id, 1.7)
    distance = (real_height * FOCAL_LENGTH_FACTOR) / box_height_px
    return round(distance, 4)


def analyze_overall_situation(analysis_data: list) -> AnalysisSummary:
    cnt_multicam = 0
    cnt_enemy_firearms = 0
    cnt_enemy_uniform = 0
    cnt_enemy_equipment = 0
    cnt_drone = 0

    min_dist = float('inf')
    has_valid_dist = False

    for item in analysis_data:
        cid = item['cls']
        dist = item.get('distance')

        if cid == 3: cnt_multicam += 1
        if cid == 4: cnt_enemy_firearms += 1
        if cid == 5: cnt_enemy_uniform += 1
        if cid == 6: cnt_enemy_equipment += 1
        if cid == 9: cnt_drone += 1

        # 최단 거리 갱신
        if dist is not None and dist > 0:
            if dist < min_dist:
                min_dist = dist
                has_valid_dist = True

    final_distance = min_dist if has_valid_dist else 0

    status = "WARNING"
    if (cnt_multicam + cnt_enemy_uniform) <= 1 and cnt_enemy_firearms == 0 and cnt_enemy_equipment == 0 and cnt_drone == 0:
        status = "SAFE"
    elif (cnt_multicam + cnt_enemy_uniform) <= 2 and cnt_enemy_firearms <= 1 and cnt_enemy_equipment == 0 and cnt_drone <= 2:
        status = "CAUTION"

    return AnalysisSummary(
        status=status,
        distance=final_distance
    )


# ---------------------------------------------------------
# [API Endpoints]
# ---------------------------------------------------------

@ai_router.get("/")
def read_root():
    return {"TIPS AI API Server"}


# 1️⃣ xyxy 결과
@ai_router.post("/detect/xyxy", response_model=DetectionResponse)
async def detect_xyxy(file: UploadFile = File(...)):
    file_bytes = await file.read()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}.jpg"
    save_image_file(file_bytes, filename)

    image = Image.open(io.BytesIO(file_bytes))
    boxes = run_yolo(image)
    
    xyxy = boxes.xyxy.cpu().numpy()
    conf = boxes.conf.cpu().numpy()
    cls = boxes.cls.cpu().numpy()

    processed_detections = []
    analysis_data_list = []

    for (x1, y1, x2, y2), c, cl in zip(xyxy, conf, cls):
        cls_id = int(cl)
        cls_txt = label[cls_id]
        cls_init = label_initials[cls_id]
        confidence = float(c)

        if cls_id in [0, 1, 2, 7, 8]:
            cls_color = "green"
            cls_color_code = "#4CAF50"
        elif cls_id in [3, 9]:
            cls_color = "yellow"
            cls_color_code = "#FFEB3B"
        else:
            cls_color = "red"
            cls_color_code = "#F44336"

        box_height = abs(y2 - y1)
        distance_val = calculate_distance(box_height, cls_id)

        det_obj = DetectionBoxExtended(
            x1=float(x1),
            y1=float(y1),
            x2=float(x2),
            y2=float(y2),
            cls=cls_id,
            cls_txt=cls_txt,
            cls_init=cls_init,
            confidence=confidence,
            cls_color=cls_color,
            cls_color_code=cls_color_code
        )
        processed_detections.append(det_obj)
        analysis_data_list.append({'cls': cls_id, 'distance': distance_val})

    summary_result = analyze_overall_situation(analysis_data_list)

    return DetectionResponse(
        summary=summary_result,
        detections=processed_detections
    )


# 2️⃣ xywhn 결과
@ai_router.post("/detect/xywhn", response_model=DetectionResponseWHNorm)
async def detect_xywhn(file: UploadFile = File(...)):
    file_bytes = await file.read()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}.jpg"
    save_image_file(file_bytes, filename)

    image = Image.open(io.BytesIO(file_bytes))
    boxes = run_yolo(image)
    
    img_width, img_height = image.size

    xywhn = boxes.xywhn.cpu().numpy()
    conf = boxes.conf.cpu().numpy()
    cls = boxes.cls.cpu().numpy()

    processed_detections = []
    analysis_data_list = []

    for (x, y, w, h), c, cl in zip(xywhn, conf, cls):
        cls_id = int(cl)
        cls_txt = label[cls_id]
        cls_init = label_initials[cls_id]
        confidence = float(c)

        pixel_height = h * img_height
        distance_val = calculate_distance(pixel_height, cls_id)

        det_obj = DetectionWHNormExtended(
            x_center_norm=float(x),
            y_center_norm=float(y),
            width_norm=float(w),
            height_norm=float(h),
            cls=cls_id,
            cls_txt=cls_txt,
            cls_init=cls_init,
            confidence=confidence
        )
        processed_detections.append(det_obj)
        analysis_data_list.append({'cls': cls_id, 'distance': distance_val})

    summary_result = analyze_overall_situation(analysis_data_list)

    return DetectionResponseWHNorm(
        summary=summary_result,
        detections=processed_detections
    )


# 3️⃣ xyxyn 결과
@ai_router.post("/detect/xyxyn", response_model=DetectionResponseXYXYNorm)
async def detect_xyxyn(file: UploadFile = File(...)):
    file_bytes = await file.read()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}.jpg"
    save_image_file(file_bytes, filename)

    image = Image.open(io.BytesIO(file_bytes))
    boxes = run_yolo(image)
    
    img_width, img_height = image.size

    xyxyn = boxes.xyxyn.cpu().numpy()
    conf = boxes.conf.cpu().numpy()
    cls = boxes.cls.cpu().numpy()

    processed_detections = []
    analysis_data_list = []

    for (x1, y1, x2, y2), c, cl in zip(xyxyn, conf, cls):
        cls_id = int(cl)
        cls_txt = label[cls_id]
        cls_init = label_initials[cls_id]
        confidence = float(c)

        pixel_height = abs(y2 - y1) * img_height
        distance_val = calculate_distance(pixel_height, cls_id)

        det_obj = DetectionXYXYNormExtended(
            x1_norm=float(x1),
            y1_norm=float(y1),
            x2_norm=float(x2),
            y2_norm=float(y2),
            cls=cls_id,
            cls_txt=cls_txt,
            cls_init=cls_init,
            confidence=confidence
        )
        processed_detections.append(det_obj)
        analysis_data_list.append({'cls': cls_id, 'distance': distance_val})

    summary_result = analyze_overall_situation(analysis_data_list)

    return DetectionResponseXYXYNorm(
        summary=summary_result,
        detections=processed_detections
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('run:ai_router', host="0.0.0.0", port=8000, reload=True)
