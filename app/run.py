import importlib
from fastapi import FastAPI
from fastapi import Response, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from starlette.types import Message

from common.utils import get_logger, log_skip_list

VERSION = "latest"  # 원하는 버전 선택

try:
    api = importlib.import_module(f"version.{VERSION}.api.api")
    ai_router = api.ai_router
except ImportError as e:
    print("error : ", e)
    print(f"!! Module {VERSION}.api not found")

app = FastAPI(
    title="TIPS API", description="API for TIPS", version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 나중에 도메인 제한 필요
    allow_credentials=True,
    allow_methods=["*"],  # 나중에 메소드 제한 필요
    allow_headers=["*"],  # 나중에 헤더 제한 필요
)

app.include_router(ai_router)
logger = get_logger("main")


# log
def log_debug(req_body: bytes, res_body: bytes):
    try:
        logger.debug(req_body.decode('utf-8'))
    except UnicodeDecodeError:
        # 바이너리 데이터면 base64로 로그 저장 (짧게)
        logger.debug(f"[binary req_body] size={len(req_body)} bytes")

    try:
        logger.debug(res_body.decode('utf-8'))
    except UnicodeDecodeError:
        logger.debug(f"[binary res_body] size={len(res_body)} bytes")
        

async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {'type': 'http.request', 'body': body}

    request._receive = receive


@app.middleware('http')
async def some_middleware(request: Request, call_next):
    # swagger 문서는 로그 남기지 않음
    if request.url.path in log_skip_list:
        return await call_next(request)

    req_body = await request.body()
    await set_body(request, req_body)
    response = await call_next(request)

    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk

    task = BackgroundTask(log_debug, req_body, res_body)
    return Response(content=res_body, status_code=response.status_code,
                    headers=dict(response.headers), media_type=response.media_type, background=task)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('run:app', host="0.0.0.0", port=8000, reload=True)
