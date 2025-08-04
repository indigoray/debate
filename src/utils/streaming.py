"""
스트리밍 출력 유틸리티
"""

import sys
import time
import openai
from typing import Iterator, Optional, List
from colorama import Fore, Style


def stream_openai_response(
    client: openai.OpenAI,
    model: str,
    messages: list,
    max_tokens: int,
    temperature: float,
    color: str = "",
    typing_speed: float = 0.02
) -> str:
    """
    OpenAI API 응답을 스트리밍으로 출력
    
    Args:
        client: OpenAI 클라이언트
        model: 사용할 모델
        messages: 메시지 리스트
        max_tokens: 최대 토큰 수
        temperature: 온도 설정
        color: 출력 색상 (Colorama 색상)
        typing_speed: 타이핑 속도 (초 단위 지연)
    
    Returns:
        완성된 응답 텍스트
    """
    complete_response = ""
    
    # OutputInterceptor인지 확인 (ConsoleCapture가 활성화된 상태인지)
    is_capturing = hasattr(sys.stdout, 'captured_output')
    captured_output = getattr(sys.stdout, 'captured_output', None) if is_capturing else None
    original_stdout = getattr(sys.stdout, 'original_stdout', sys.stdout) if is_capturing else sys.stdout
    
    try:
        # 스트리밍 모드로 API 호출
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )
        
        # 색상 적용 시작
        color_start = color if color else ""
        if color_start:
            original_stdout.write(color_start)
            original_stdout.flush()
            if captured_output is not None:
                captured_output.append(color_start)
        
        # 스트리밍 출력
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                complete_response += content
                
                # 한 글자씩 출력 (타이핑 효과)
                for char in content:
                    original_stdout.write(char)
                    original_stdout.flush()
                    if captured_output is not None:
                        captured_output.append(char)
                    time.sleep(typing_speed)
        
        # 색상 리셋
        if color_start:
            original_stdout.write(Style.RESET_ALL)
            original_stdout.flush()
            if captured_output is not None:
                captured_output.append(Style.RESET_ALL)
        
        # 줄바꿈
        original_stdout.write('\n')
        original_stdout.flush()
        if captured_output is not None:
            captured_output.append('\n')
        
    except Exception as e:
        error_msg = f"{Fore.RED}스트리밍 출력 중 오류 발생: {e}{Style.RESET_ALL}\n"
        original_stdout.write(error_msg)
        original_stdout.flush()
        if captured_output is not None:
            captured_output.append(error_msg)
        complete_response = f"[오류] 응답을 생성하는 중 오류가 발생했습니다."
    
    return complete_response


def stream_text(text: str, color: str = "", typing_speed: float = 0.03) -> None:
    """
    기존 텍스트를 스트리밍 방식으로 출력
    
    Args:
        text: 출력할 텍스트
        color: 출력 색상 (Colorama 색상)
        typing_speed: 타이핑 속도 (초 단위 지연)
    """
    # OutputInterceptor인지 확인 (ConsoleCapture가 활성화된 상태인지)
    is_capturing = hasattr(sys.stdout, 'captured_output')
    captured_output = getattr(sys.stdout, 'captured_output', None) if is_capturing else None
    original_stdout = getattr(sys.stdout, 'original_stdout', sys.stdout) if is_capturing else sys.stdout
    
    # 색상 적용 시작
    if color:
        original_stdout.write(color)
        original_stdout.flush()
        if captured_output is not None:
            captured_output.append(color)
    
    # 스트리밍 출력
    for char in text:
        original_stdout.write(char)
        original_stdout.flush()
        if captured_output is not None:
            captured_output.append(char)
        time.sleep(typing_speed)
    
    # 색상 리셋
    if color:
        original_stdout.write(Style.RESET_ALL)
        original_stdout.flush()
        if captured_output is not None:
            captured_output.append(Style.RESET_ALL)
    
    # 줄바꿈
    original_stdout.write('\n')
    original_stdout.flush()
    if captured_output is not None:
        captured_output.append('\n')


def get_typing_speed(config: dict = None) -> float:
    """
    타이핑 속도 설정을 반환
    
    Args:
        config: 설정 딕셔너리
    
    Returns:
        타이핑 속도 (초 단위, 0이면 즉시 출력)
    """
    if not config:
        return 0.02  # 기본값
    
    output_config = config.get('output', {})
    return output_config.get('typing_speed', 0.02)