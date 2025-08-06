"""
Debate Manager - 토론 진행 및 관리 에이전트 (메인 오케스트레이터)
"""

import logging
import os
from typing import Dict, Any, List
from colorama import Fore, Style
from autogen import ConversableAgent

from .panel_agent import PanelAgent
from .panel import Panel
from .panel_generator import PanelGenerator
from .response_generator import ResponseGenerator
from .debate_orchestrator import DebateOrchestrator
from .debate_presenter import DebatePresenter
from ..utils.output_capture import ConsoleCapture


class DebateManager:
    """토론 진행 및 관리 에이전트 (메인 오케스트레이터)"""
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        Debate Manager 초기화
        
        Args:
            config: 설정 딕셔너리
            api_key: OpenAI API 키
        """
        self.config = config
        self.api_key = api_key
        self.logger = logging.getLogger('debate_agents.manager')
        
        # 토론 설정
        self.duration_minutes = config['debate']['duration_minutes']
        self.panel_size = config['debate']['panel_size']  # 기본값, 사용자 참여시 조정됨
        self.show_debug_info = config['debate'].get('show_debug_info', True)
        
        # 사용자 참여 관련 변수 초기화
        self.user_participation = False
        self.user_name = None
        self.user_expertise = None
        
        # 패널들 (AI 패널과 인간 참여자 모두 포함)
        self.panel_agents: List[Panel] = []
        
        # 출력 캡처 객체
        self.console_capture = ConsoleCapture()
        
        # 컴포넌트들
        self.panel_generator = PanelGenerator(config, api_key)
        self.response_generator = ResponseGenerator(config, api_key)
        self.orchestrator = DebateOrchestrator(config, api_key)
        self.presenter = DebatePresenter(config)
        
        # AutoGen 에이전트 생성
        self.agent = ConversableAgent(
            name="DebateManager",
            system_message=self._create_system_prompt(),
            llm_config={
                "config_list": [{
                    "model": config['ai']['model'],
                    "api_key": api_key
                }]
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        self.logger.info("Debate Manager 초기화 완료")
        
        # 디버그 정보 출력
        if self.show_debug_info:
            self.presenter.display_debug_info(self._create_system_prompt())
    

    
    def _create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        base_prompt = self.config['agents']['debate_manager']['system_prompt']
        additional_instructions = self.config['agents']['debate_manager'].get('additional_instructions', [])
        response_constraints = self.config['agents']['debate_manager'].get('response_constraints', {})
        
        # 추가 지시사항을 문자열로 변환
        additional_text = ""
        if additional_instructions:
            additional_text = "\n\n## 추가 지시사항\n"
            for i, instruction in enumerate(additional_instructions, 1):
                additional_text += f"{i}. {instruction}\n"
        
        # 응답 제약 조건 텍스트 생성
        constraints_text = ""
        if response_constraints:
            constraints_text = "\n\n## 응답 제약 조건\n"
            for key, value in response_constraints.items():
                if value:  # 빈 값이 아닌 경우만 추가
                    constraints_text += f"- **{key}**: {value}\n"
        
        # 사용자 참여시 추가 지침
        user_participation_guide = ""
        if self.user_participation:
            user_participation_guide = f"""

## 사용자 참여자 대우 지침
- {self.user_name}님은 {self.user_expertise}로서 토론에 참여하는 **동등한 전문가 패널**입니다.
- AI 패널과 동일하게 존중하고 전문적으로 대우하세요.
- "{self.user_name} 패널께서"라고 호칭하며, 다른 패널들과 동일한 수준의 예의를 갖춰 진행하세요.
- 사용자의 의견도 다른 전문가 의견과 동등한 가치로 인정하고 언급하세요.
"""

        system_prompt = f"""
{base_prompt}

## 역할과 책임
1.  **토론 설계자**: 주제를 분석하여 가장 치열하고 흥미로운 토론이 될 수 있도록, 대립각이 명확한 전문가 패널을 구성하세요.
2.  **적극적 중재자**: 단순히 발언 기회를 주는 것을 넘어, 토론이 교착 상태에 빠지거나 논점이 흐려될 때 핵심을 찌르는 질문을 던져 논의를 심화시키세요.
3.  **논쟁 유도자**: 패널 간의 단순 의견 교환을 넘어, "방금 A패널의 주장에 대해 B패널께서는 어떻게 생각하십니까?" 와 같이 직접적인 반론과 재반론이 오가도록 적극적으로 유도하세요.
4.  **압박 질문**: 중립성을 유지하면서도, "그 주장의 구체적인 근거는 무엇입니까?", "그 관점의 잠재적 맹점은 없습니까?" 와 같이 패널들이 자신의 논리를 명확히 방어하도록 압박 질문을 사용할 수 있습니다.
5.  **종합 정리자**: 토론 종료 시, 각 패널의 최종 의견을 듣고, 단순 요약을 넘어 합의점, 대립점, 그리고 남은 과제까지 종합적으로 정리하여 제시하세요.{user_participation_guide}

## 토론 진행 방식
- **1단계 (초기 의견 발표)**: 각 패널이 자신의 핵심 주장을 제시합니다.
- **2단계 (지정 반론 및 상호 토론)**: 진행자가 특정 패널을 지목해 반론을 유도하고, 이어서 자유로운 상호 토론을 진행합니다. (라운드 방식)
- **3단계 (심화 토론)**: 쟁점을 좁혀 더 깊이 있는 논쟁을 진행합니다.
- **4단계 (최종 의견 발표 및 정리)**: 각 패널의 최종 의견을 듣고, 진행자가 전체 토론을 종합적으로 결론 냅니다.
- 토론 시간: 약 {self.duration_minutes}분
{constraints_text}{additional_text}
응답할 때는 항상 **[토론 진행자]** 로 시작하세요.
"""
        return system_prompt
    
    def create_panel_agents(self, topic: str) -> List[Panel]:
        """주제부터 시작해서 패널 생성까지 완료 (PanelGenerator로 위임)"""
        return self.panel_generator.create_panel_agents(topic, self.panel_size, self._create_system_prompt())
    
    def ask_user_confirmation(self) -> bool:
        """사용자에게 토론 진행 여부를 묻기 (DebatePresenter로 위임)"""
        return self.presenter.ask_user_confirmation()
    
    def start_debate(self, topic: str, user_participation: bool = False) -> None:
        """토론 시작 (메인 오케스트레이터)"""
        self.user_participation = user_participation
        
        # 콘솔 출력 캡처 시작
        self.console_capture.start_capture()
        
        # 사용자 참여시 패널 수 조정 및 사용자 정보 입력
        if user_participation:
            self._handle_user_participation()
        
        while True:
            self.presenter.display_progress_message("🔍 주제 분석 및 전문가 패널 구성 중...")
            
            # 1. 패널 에이전트 생성 (페르소나 생성부터 에이전트 생성까지 한 번에)
            self.panel_agents = self.create_panel_agents(topic)
            
            # 2. 설정에 따라 사용자 확인 (페르소나 미리보기는 제거)
            if self.show_debug_info:
                # 패널 정보 출력
                self.presenter.display_panel_debug_info(self.panel_agents)
                user_choice = self.ask_user_confirmation()
                
                if user_choice is None:  # 재생성 요청
                    self.presenter.display_regeneration_message()
                    continue
                elif not user_choice:  # 종료 요청
                    return
                # user_choice가 True면 토론 진행
            
            # 3. 사용자 참여시 사용자 정보 추가
            if self.user_participation:
                self.panel_agents = self.orchestrator.add_user_as_panelist(
                    self.panel_agents, self.user_name, self.user_expertise
                )
            
            # 4. 토론 방식 안내
            self.orchestrator.announce_debate_format(
                topic, self.duration_minutes, self.panel_agents, 
                self.user_participation, self.user_name, self.user_expertise, 
                self._create_system_prompt()
            )
            
            # 5. 패널 소개
            self.orchestrator.introduce_panels(self.panel_agents)
            
            # 6. 토론 진행
            self.orchestrator.conduct_debate(topic, self.panel_agents)
            
            # 7. 토론 마무리
            self.orchestrator.conclude_debate(topic, self.panel_agents, self._create_system_prompt())
            
            # 토론이 완료되면 루프 종료
            break
        
        # 토론 완료 후 마크다운 파일로 저장
        self._save_debate_results(topic)
    
    def _handle_user_participation(self) -> None:
        """사용자 참여 처리"""
        self.panel_size = 3  # AI 패널 3명
        
        # 사용자 이름 입력
        self.user_name = self.presenter.get_user_input("토론에서 사용할 이름을 입력해주세요: ")
        if not self.user_name:
            self.user_name = "참여자"
        
        # 사용자 전문성/배경 입력
        print(f"\n{Fore.CYAN}💡 토론에서 어떤 입장으로 참여하시겠습니까?{Style.RESET_ALL}")
        print("예시: 직장인, 대학생, 개인투자자, 경제학 전공자, 금융업 종사자, 창업가 등")
        
        self.user_expertise = self.presenter.get_user_input("귀하의 배경이나 전문분야를 입력해주세요: ")
        if not self.user_expertise:
            self.user_expertise = "시민 참여자"
        
        self.presenter.display_welcome_message(self.user_name, self.user_expertise)
    
    def _save_debate_results(self, topic: str) -> None:
        """토론 결과 저장"""
        try:
            # 출력 캡처 중지
            self.console_capture.stop_capture()
            
            # 마크다운 파일로 저장
            saved_file = self.console_capture.save_to_markdown(topic)
            
            self.presenter.display_save_result(saved_file, os.path.abspath(saved_file))
            
        except Exception as e:
            self.presenter.display_save_error(str(e))
            self.logger.error(f"마크다운 파일 저장 실패: {e}")
