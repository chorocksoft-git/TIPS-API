# Description: 공통 모듈
# 로그 세팅
import datetime
import logging
import logging.handlers
import os

from common.const import LOG_FILE_PATH

# 로그 파일 형식 - yyyymmdd.log
LOG_FILE_NAME = os.path.join(LOG_FILE_PATH, datetime.datetime.now().strftime('%Y%m%d') + '.log')

log_skip_list = ['/docs', '/redoc', '/openapi.json']


def get_logger(name):
    logger = logging.getLogger(name)
    
    # 중복 핸들러 추가 방지
    if not logger.handlers: 
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

        # 콘솔 출력용 핸들러
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # 매일 로그 파일을 생성한다.
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=LOG_FILE_NAME, when='midnight', interval=1, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger