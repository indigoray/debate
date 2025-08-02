#!/usr/bin/env python3
"""
Debate Agents - AI 패널 토론 시뮬레이션 앱
메인 진입점
"""

import os
import sys
import logging
import yaml
from dotenv import load_dotenv
from colorama import init, Fore, Style

from src.agents.debate_manager import DebateManager
from src.utils.logger import setup_logger

# Colorama 초기화 (Windows 호환성)
init()

def load_config():
    """설정 파일 로드"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: config.yaml 파일을 찾을 수 없습니다.{Style.RESET_ALL}")
        sys.exit(1)

def main():
    """메인 함수"""
    # 환경변수 로드
    load_dotenv()
    
    # 설정 로드
    config = load_config()
    
    # 로거 설정
    logger = setup_logger(config['logging'])
    
    # OpenAI API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print(f"{Fore.RED}Error: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Tip: .env 파일을 생성하고 API 키를 설정하세요.{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"🎭 Debate Agents - AI 패널 토론 시뮬레이션")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    try:
        # 토론 주제 입력
        topic = input(f"\n{Fore.GREEN}토론 주제를 입력하세요: {Style.RESET_ALL}").strip()
        
        if not topic:
            print(f"{Fore.RED}토론 주제가 입력되지 않았습니다.{Style.RESET_ALL}")
            return
        
        # Debate Manager 초기화 및 토론 시작
        debate_manager = DebateManager(config, api_key)
        debate_manager.start_debate(topic)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}토론이 중단되었습니다.{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"토론 실행 중 오류 발생: {e}")
        print(f"{Fore.RED}오류가 발생했습니다: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()