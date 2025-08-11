"""
DebatePresenter - 콘솔 출력 및 사용자 인터페이스 클래스
"""

import logging
from typing import Dict, Any, List
from colorama import Fore, Style


class DebatePresenter:
    """콘솔 출력 및 사용자 인터페이스를 담당하는 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        DebatePresenter 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.logger = logging.getLogger('debate_agents.presenter')
        self.show_debug_info = config['debate'].get('show_debug_info', True)
    
    def display_debug_info(self, system_prompt: str) -> None:
        """디버그 정보 출력"""
        if self.show_debug_info:
            print(f"\n{Fore.CYAN}🔧 DEBUG: Debate Manager System Prompt{Style.RESET_ALL}")
            print("=" * 80)
            print(f"{Fore.YELLOW}{system_prompt}{Style.RESET_ALL}")
            print("=" * 80)
    
    def display_panel_debug_info(self, panel_agents: List) -> None:
        """패널 에이전트들의 디버그 정보 출력"""
        if self.show_debug_info:
            print(f"\n{Fore.CYAN}🔧 DEBUG: Panel Agents System Prompts{Style.RESET_ALL}")
            
            for i, agent in enumerate(panel_agents, 1):
                if hasattr(agent, 'system_prompt'):  # AI 패널인 경우
                    print(f"\n{Fore.GREEN}📋 Panel {i}: {agent.name}{Style.RESET_ALL}")
                    print("-" * 80)
                    print(f"{Fore.YELLOW}{agent.system_prompt}{Style.RESET_ALL}")
                    print("-" * 80)
    
    def display_personas(self, personas: List[Dict[str, str]]) -> None:
        """생성된 페르소나를 출력"""
        print(f"\n{Fore.CYAN}👥 생성된 전문가 패널{Style.RESET_ALL}")
        print("=" * 80)
        
        for i, persona in enumerate(personas, 1):
            print(f"\n{Fore.GREEN}📋 전문가 {i}: {persona['name']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🏢 직업과 소속:{Style.RESET_ALL} {persona['expertise']}")
            print(f"{Fore.YELLOW}📚 배경:{Style.RESET_ALL} {persona['background']}")
            print(f"{Fore.YELLOW}💭 핵심 관점:{Style.RESET_ALL} {persona['perspective']}")
            print(f"{Fore.YELLOW}🎭 토론 스타일:{Style.RESET_ALL} {persona['debate_style']}")
            print("-" * 80)
    
    def ask_user_confirmation(self) -> bool:
        """사용자에게 토론 진행 여부를 묻기"""
        print(f"\n{Fore.CYAN}🤔 위 패널로 토론을 진행하시겠습니까?{Style.RESET_ALL}")
        print(f"{Fore.WHITE}[y/Y] 예, 토론을 시작합니다{Style.RESET_ALL}")
        print(f"{Fore.WHITE}[n/N] 아니오, 토론을 종료합니다{Style.RESET_ALL}")
        print(f"{Fore.WHITE}[r/R] 페르소나를 다시 생성합니다{Style.RESET_ALL}")
        
        while True:
            choice = input(f"\n{Fore.CYAN}선택하세요 (y/n/r): {Style.RESET_ALL}").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                print(f"{Fore.RED}토론을 종료합니다.{Style.RESET_ALL}")
                return False
            elif choice in ['r', 'regenerate']:
                return None  # 재생성 신호
            else:
                print(f"{Fore.RED}올바른 선택지를 입력해주세요 (y/n/r){Style.RESET_ALL}")
    
    def announce_debate_format(self, topic: str, duration_minutes: int, panel_agents: List, user_participation: bool = False, user_name: str = None, user_expertise: str = None) -> None:
        """토론 방식 안내"""
        print(f"\n{Fore.CYAN}📋 토론 진행 방식{Style.RESET_ALL}")
        print(f"주제: {Fore.YELLOW}{topic}{Style.RESET_ALL}")
        print(f"방식: 패널토론")
        print(f"시간: 약 {duration_minutes}분")
        
        if user_participation:
            print(f"참여자: {len(panel_agents)}명의 전문가 패널 (AI 전문가 {len(panel_agents)-1}명 + {user_name}님({user_expertise}))")
        else:
            print(f"참여자: {len(panel_agents)}명의 전문가 패널")
        
        print(f"진행: 순차 발언 → 상호 토론 → 최종 의견")
    
    def display_topic_briefing_header(self) -> None:
        """주제 브리핑 헤더 출력"""
        print(f"\n{Fore.CYAN}📰 주제 브리핑{Style.RESET_ALL}")
        print()  # 줄바꿈
    
    def display_manager_message(self, message: str) -> None:
        """매니저 메시지 출력"""
        # 이미 [토론 진행자]가 포함되어 있으면 그대로 출력, 없으면 추가
        if message.startswith("[토론 진행자]"):
            print(f"\n{Fore.MAGENTA}{message}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.MAGENTA}[토론 진행자] {message}{Style.RESET_ALL}")
    
    def display_panel_introduction_header(self) -> None:
        """패널 소개 헤더 출력"""
        print(f"\n{Fore.CYAN}👥 패널 소개{Style.RESET_ALL}")
    
    def display_debate_start_header(self) -> None:
        """토론 시작 헤더 출력"""
        print(f"\n{Fore.CYAN}🎭 토론 시작{Style.RESET_ALL}")
    
    def display_stage_header(self, stage_number: int, stage_name: str) -> None:
        """단계별 헤더 출력"""
        print(f"\n{Fore.MAGENTA}📢 {stage_number}단계: {stage_name}{Style.RESET_ALL}")
    
    def display_round_header(self, round_number: int) -> None:
        """라운드 헤더 출력"""
        print(f"\n{Fore.BLUE}--- 토론 라운드 {round_number} ---{Style.RESET_ALL}")

    def display_round_banner(self, round_number: int, title: str, subtitle: str = "") -> None:
        """라운드 배너/헤더 출력 (일원화)"""
        print(f"\n{Fore.MAGENTA}=== 라운드 {round_number}, {title} ==={Style.RESET_ALL}")
        if subtitle:
            print(subtitle)
        print("=" * 50)

    def display_section_header(self, title: str) -> None:
        """구분선이 포함된 섹션 헤더 출력"""
        print(f"\n{title}")
        print("=" * 50)

    def display_round_complete(self, round_number: int) -> None:
        """라운드 완료 표시"""
        if self.show_debug_info:
            print(f"🏁 [라운드 완료] 라운드 {round_number} 완료 - 다음 라운드로 전환")
        else:
            print(f"\n{'='*60}")
            print(f"🏁 라운드 {round_number} 완료")
            print(f"{'='*60}\n")

    def display_debug_line(self, message: str) -> None:
        """디버그 라인 출력(일원화)"""
        if self.show_debug_info:
            print(message)
    
    def display_debate_conclusion_header(self) -> None:
        """토론 마무리 헤더 출력"""
        print(f"\n{Fore.CYAN}📝 토론 마무리{Style.RESET_ALL}")
    
    def display_final_opinions_header(self) -> None:
        """최종 의견 헤더 출력"""
        print(f"\n{Fore.MAGENTA}📢 최종 의견{Style.RESET_ALL}")
    
    def display_debate_conclusion_final_header(self) -> None:
        """토론 결론 헤더 출력"""
        print(f"\n{Fore.CYAN}🎯 토론 결론{Style.RESET_ALL}")
    
    def display_human_response(self, response: str) -> None:
        """사용자 응답 출력"""
        print(f"\n{Fore.CYAN}{response}{Style.RESET_ALL}")
    
    def display_line_break(self) -> None:
        """줄바꿈 출력"""
        print()
    
    def display_progress_message(self, message: str) -> None:
        """진행 상황 메시지 출력"""
        print(f"\n{Fore.BLUE}{message}{Style.RESET_ALL}")
    
    def display_regeneration_message(self) -> None:
        """페르소나 재생성 메시지 출력"""
        print(f"\n{Fore.YELLOW}🔄 페르소나를 다시 생성합니다...{Style.RESET_ALL}")
    
    def get_user_input(self, prompt: str, color: str = Fore.GREEN) -> str:
        """컬러 프롬프트로 사용자 입력 받기"""
        return input(f"\n{color}{prompt}{Style.RESET_ALL}").strip()
    
    def display_welcome_message(self, user_name: str, user_expertise: str) -> None:
        """환영 메시지 출력"""
        print(f"\n{Fore.YELLOW}환영합니다, {user_name}님! ({user_expertise})으로 토론에 참여하게 됩니다.{Style.RESET_ALL}")
    
    def display_save_result(self, saved_file: str, abs_path: str) -> None:
        """토론 저장 결과 출력"""
        print(f"\n{Fore.GREEN}💾 토론 내용이 저장되었습니다:{Style.RESET_ALL}")
        print(f"   파일: {saved_file}")
        print(f"   경로: {abs_path}")
    
    def display_save_error(self, error: str) -> None:
        """토론 저장 오류 출력"""
        print(f"\n{Fore.YELLOW}⚠️ 토론 내용 저장 중 오류가 발생했습니다: {error}{Style.RESET_ALL}")
    
    def display_persona_generation_message(self) -> None:
        """페르소나 생성 메시지 출력"""
        print(f"\n{Fore.YELLOW}🤖 전문가 패널을 생성하고 있습니다...{Style.RESET_ALL}")