#!/usr/bin/env python3
"""
Debate Agents - AI 패널 토론 시뮬레이션 앱
메인 진입점
"""

import os
import sys
import logging
import yaml
import pkg_resources
import shutil
from dotenv import load_dotenv
from colorama import init, Fore, Style

from src.agents.debate_manager import DebateManager
from src.utils.logger import setup_logger

# Colorama 초기화 (Windows 호환성)
init()

def load_config():
    """설정 파일 로드"""
    try:
        # 1. 현재 디렉토리에 config.yaml이 있는지 확인 (개발 환경)
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f), False  # False = 기존 파일 사용
        
        # 2. config.yaml이 없으면 config.yaml.example을 찾아서 복사
        elif os.path.exists('config.yaml.example'):
            print(f"{Fore.YELLOW}config.yaml 파일이 없습니다. config.yaml.example을 복사합니다...{Style.RESET_ALL}")
            shutil.copy2('config.yaml.example', 'config.yaml')
            print(f"{Fore.GREEN}config.yaml 파일이 생성되었습니다!{Style.RESET_ALL}")
            with open('config.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f), True  # True = 새로 생성됨
        
        # 3. 패키지 설치된 경우 - 패키지 내 config.yaml.example 찾기
        else:
            try:
                # 패키지 설치 경로에서 config.yaml.example 찾기
                package_example = None
                possible_paths = [
                    'config.yaml.example',
                    '../config.yaml.example',
                    '../../config.yaml.example'
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        package_example = path
                        break
                
                if package_example:
                    print(f"{Fore.YELLOW}설정 파일을 초기화합니다...{Style.RESET_ALL}")
                    shutil.copy2(package_example, 'config.yaml')
                    print(f"{Fore.GREEN}config.yaml 파일이 생성되었습니다!{Style.RESET_ALL}")
                    with open('config.yaml', 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f), True  # True = 새로 생성됨
                else:
                    # 마지막 대안 - 기본 설정 사용
                    print(f"{Fore.YELLOW}설정 파일을 찾을 수 없어 기본 설정을 사용합니다.{Style.RESET_ALL}")
                    default_config = {
                        'debate': {
                            'duration_minutes': 10,
                            'max_turns_per_agent': 3,
                            'panel_size': 4,
                            'show_debug_info': True
                        },
                        'ai': {
                            'model': 'gpt-4.1',
                            'temperature': 0.7,
                            'max_tokens': 1500,
                            'token_multipliers': {
                                'persona_generation': 2.0,
                                'conclusion': 2.0
                            }
                        },
                        'logging': {
                            'level': 'INFO',
                            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        }
                    }
                    return default_config, False
            except Exception as pkg_error:
                print(f"{Fore.YELLOW}패키지 설정 파일을 찾을 수 없어 기본 설정을 사용합니다: {pkg_error}{Style.RESET_ALL}")
                # 기본 설정 반환 (위와 동일)
                default_config = {
                    'debate': {
                        'duration_minutes': 10,
                        'max_turns_per_agent': 3,
                        'panel_size': 4,
                        'show_debug_info': True
                    },
                    'ai': {
                        'model': 'gpt-4.1',
                        'temperature': 0.7,
                        'max_tokens': 1500,
                        'token_multipliers': {
                            'persona_generation': 2.0,
                            'conclusion': 2.0
                        }
                    },
                    'logging': {
                        'level': 'INFO',
                        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    }
                }
                return default_config, False
                
    except Exception as e:
        print(f"{Fore.RED}Error: 설정 파일 로드 중 오류가 발생했습니다: {e}{Style.RESET_ALL}")
        sys.exit(1)

def main():
    """메인 함수"""
    # 환경변수 로드
    load_dotenv()
    
    # 설정 로드
    config, config_created = load_config()
    
    # 로거 설정
    logger = setup_logger(config['logging'])
    
    # OpenAI API 키 확인 (config.yaml 우선, 환경변수 차선)
    api_key = config.get('ai', {}).get('api_key') or os.getenv('OPENAI_API_KEY')
    
    # API 키가 'your_openai_api_key_here' 같은 플레이스홀더인 경우도 체크
    if not api_key or api_key in ['your_openai_api_key_here', 'your_actual_api_key_here', '']:
        if config_created:
            # 설정 파일이 새로 생성된 경우
            print(f"\n{Fore.CYAN}🔑 OpenAI API 키 설정이 필요합니다!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}📝 다음 단계를 따라주세요:{Style.RESET_ALL}")
            print(f"   1. OpenAI API 키를 발급받으세요: {Fore.BLUE}https://platform.openai.com/api-keys{Style.RESET_ALL}")
            print(f"   2. config.yaml 파일을 열어 다음 부분을 수정하세요:")
            print(f"      {Fore.GREEN}ai:")
            print(f"        api_key: {Fore.RED}your_openai_api_key_here{Style.RESET_ALL} {Fore.YELLOW}← 여기에 실제 API 키 입력{Style.RESET_ALL}")
            print(f"   3. 파일을 저장한 후 다시 실행하세요: {Fore.CYAN}debate-agents{Style.RESET_ALL}")
            print(f"\n{Fore.MAGENTA}💡 참고: API 키는 sk-로 시작하는 긴 문자열입니다.{Style.RESET_ALL}")
        else:
            # 기존 설정 파일이지만 API 키가 없는 경우
            print(f"{Fore.RED}❌ OpenAI API 키가 설정되지 않았습니다.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🔧 해결 방법:{Style.RESET_ALL}")
            print(f"   • config.yaml의 ai.api_key에 OpenAI API 키를 설정하거나")
            print(f"   • 환경변수 OPENAI_API_KEY를 설정하세요")
            print(f"   • API 키 발급: {Fore.BLUE}https://platform.openai.com/api-keys{Style.RESET_ALL}")
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
        
        # 사용자 참여 여부 확인
        print(f"\n{Fore.CYAN}🤔 토론에 함께 참여하시겠습니까?{Style.RESET_ALL}")
        print(f"   • yes: 토론자로 직접 참여합니다 (AI 패널 3명 + 사용자)")
        print(f"   • no: AI 패널들의 토론을 관람합니다 (AI 패널 4명)")
        
        while True:
            participate_choice = input(f"\n{Fore.GREEN}선택해주세요 (yes/no): {Style.RESET_ALL}").strip().lower()
            
            if participate_choice in ['yes', 'y', '네', '예']:
                user_participation = True
                print(f"\n{Fore.YELLOW}🎭 훌륭합니다! 당신도 토론자로 참여하게 됩니다.{Style.RESET_ALL}")
                break
            elif participate_choice in ['no', 'n', '아니오', '아니', '보기만']:
                user_participation = False
                print(f"\n{Fore.BLUE}👥 AI 패널들의 토론을 관람하시게 됩니다.{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}잘못된 입력입니다. 'yes' 또는 'no'를 입력해주세요.{Style.RESET_ALL}")
        
        # Debate Manager 초기화 및 토론 시작
        debate_manager = DebateManager(config, api_key)
        debate_manager.start_debate(topic, user_participation)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}토론이 중단되었습니다.{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"토론 실행 중 오류 발생: {e}")
        print(f"{Fore.RED}오류가 발생했습니다: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()