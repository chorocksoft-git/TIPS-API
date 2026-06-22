# Tacticalist AI - TIPS API

전술 환경 객체 탐지 및 상황 판단을 위한 AI API 서버 저장소입니다.

## 1. 프로젝트 개요
* **목적**: 전술 상황(총기, 군복, 장비 등)에서의 실시간 객체 탐지 및 위협 수준 분석.
* **핵심 모델**: YOLO v11m 추가 학습 모델.
* **주요 성능**: mAP50 기준 **91.6%** 달성.

## 2. 핵심 기능
* **객체 탐지 (Object Detection)**: 10종의 전술 객체(아군/적군 장비, 민간인, 드론 등) 실시간 탐지.
* **상황 판단 (Situational Awareness)**: 탐지된 객체 종류와 수에 따라 상황을 3단계(`SAFE`, `CAUTION`, `WARNING`)로 분석.
* **거리 추정 (Distance Estimation)**: 바운딩 박스의 높이를 기반으로 객체와의 대략적인 거리(m) 계산.
* **다양한 출력 포맷**: XYXY, XYWHN(정규화), XYXYN(정규화) 등 다양한 좌표 형식 지원.

## 3. 탐지 대상 클래스 (9종)
| ID | 클래스명 (Full Name) | 약어 (Initials) |
|:---:|:---|:---:|
| 0 | Allied Firearms | A-F |
| 1 | Allied Uniforms | A-U |
| 2 | Allied Equipment | A-E |
| 3 | Multicam | MC |
| 4 | Enemy Firearms | E-F |
| 5 | Enemy Uniforms | E-U |
| 6 | Enemy Equipment | E-E |
| 7 | Animals | ANI |
| 8 | Civilians | CIV |
| 9 | Drones | DRN |

## 4. 주요 소스코드 구성
* `run.py`: FastAPI 서버 실행 엔트리 포인트 (Logging, CORS 설정 포함).
* `api.py`: 탐지 및 상황 분석 비즈니스 로직이 구현된 API 엔드포인트.
* `yolo11.py`: YOLO 모델 로드 및 추론 웜업(Warm-up) 처리.
* `schema.py`: Pydantic 기반의 데이터 입출력 스키마 정의.

## 5. 설치 및 실행 방법

### 환경 구축
```bash
pip install -r requirements.txt
```

### API 서버 실행
```bash
python run.py
```
서버 실행 후 `http://localhost:8000/docs`에서 Swagger UI를 통해 API 명세를 확인할 수 있습니다.
