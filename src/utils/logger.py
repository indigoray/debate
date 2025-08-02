"""
로깅 설정 유틸리티
"""

import logging
import sys
from typing import Dict, Any

def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """
    로거 설정
    
    Args:
        config: 로깅 설정 딕셔너리
        
    Returns:
        설정된 로거 인스턴스
    """
    # 로거 생성
    logger = logging.getLogger('debate_agents')
    
    # 로그 레벨 설정
    level = getattr(logging, config.get('level', 'INFO').upper())
    logger.setLevel(level)
    
    # 이미 핸들러가 있으면 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()
    
    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(console_handler)
    
    # 상위 로거로 전파 방지
    logger.propagate = False
    
    return logger