"""
공통 유틸리티 함수
"""
import logging
from typing import Optional, Dict, Any


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    로깅 설정
    
    Args:
        service_name: 서비스 이름
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 로그 포맷
        
    Returns:
        설정된 Logger 객체
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Logger 생성
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 이미 핸들러가 있으면 제거
    if logger.handlers:
        logger.handlers.clear()
    
    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 포맷터 생성
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(console_handler)
    
    return logger


def create_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Dict[str, Any]:
    """
    표준 응답 형식 생성
    
    Args:
        data: 응답 데이터
        message: 응답 메시지
        status_code: HTTP 상태 코드
        
    Returns:
        표준 응답 딕셔너리
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "status_code": status_code
    }


def create_error_response(message: str = "Error", status_code: int = 400, error: Any = None) -> Dict[str, Any]:
    """
    표준 에러 응답 형식 생성
    
    Args:
        message: 에러 메시지
        status_code: HTTP 상태 코드
        error: 에러 상세 정보
        
    Returns:
        표준 에러 응답 딕셔너리
    """
    response = {
        "success": False,
        "message": message,
        "status_code": status_code
    }
    if error is not None:
        response["error"] = error
    return response

