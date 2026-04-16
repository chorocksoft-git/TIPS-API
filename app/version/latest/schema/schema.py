from typing import List

from pydantic import BaseModel


# [수정] 화면 표시에 최적화하여 불필요한 파라미터 제거 및 거리(distance) 추가
class DetectionBoxExtended(BaseModel):
    # 좌표 정보는 그리기 위해 필수
    x1: float
    y1: float
    x2: float
    y2: float

    # 시각화 정보
    confidence: float  # AI 탐지 신뢰도
    cls: int  # 객체 클래스 ID
    cls_txt: str  # 객체 클래스 ID
    cls_init: str
    cls_color: str
    cls_color_code: str


# [수정] Summary에 '가장 가까운 거리' 정보 추가
class AnalysisSummary(BaseModel):
    status: str  # SAFE / CAUTION / WARNING
    distance: float  # [추가] 가장 가까운 객체와의 거리 (예: "15m") - 없으면 "N/A"


class DetectionResponse(BaseModel):
    summary: AnalysisSummary
    detections: List[DetectionBoxExtended]


# [추가] xywhn 결과용 확장 모델 (화면 표시 최적화)
class DetectionWHNormExtended(BaseModel):
    x_center_norm: float
    y_center_norm: float
    width_norm: float
    height_norm: float
    confidence: float
    cls: int
    cls_txt: str
    cls_init: str


# [추가] xywhn 응답 래퍼
class DetectionResponseWHNorm(BaseModel):
    summary: AnalysisSummary
    detections: List[DetectionWHNormExtended]


# [추가] xyxyn 결과용 확장 모델 (화면 표시 최적화)
class DetectionXYXYNormExtended(BaseModel):
    x1_norm: float
    y1_norm: float
    x2_norm: float
    y2_norm: float
    confidence: float
    cls: int
    cls_txt: str
    cls_init: str


# [추가] xyxyn 응답 래퍼
class DetectionResponseXYXYNorm(BaseModel):
    summary: AnalysisSummary
    detections: List[DetectionXYXYNormExtended]


class DetectionBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    cls: int
    cls_txt: str


class DetectionWH(BaseModel):
    x_center: float
    y_center: float
    width: float
    height: float
    confidence: float
    cls: int
    cls_txt: str


class DetectionWHNorm(BaseModel):
    x_center_norm: float
    y_center_norm: float
    width_norm: float
    height_norm: float
    confidence: float
    cls: int
    cls_txt: str


class DetectionXYXYNorm(BaseModel):
    x1_norm: float
    y1_norm: float
    x2_norm: float
    y2_norm: float
    confidence: float
    cls: int
    cls_txt: str
