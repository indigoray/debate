"""
DebateOrchestrator - 토론 흐름 제어 및 단계별 진행 클래스
"""

import time
import logging
import random
from typing import Dict, Any, List

from .panel_human import PanelHuman
from .debate_presenter import DebatePresenter
from .response_generator import ResponseGenerator


class DebateOrchestrator:
    """토론 흐름 제어 및 단계별 진행을 담당하는 클래스"""
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        DebateOrchestrator 초기화
        
        Args:
            config: 설정 딕셔너리
            api_key: OpenAI API 키
        """
        self.config = config
        self.api_key = api_key
        self.logger = logging.getLogger('debate_agents.orchestrator')
        
        # 토론 설정
        self.max_turns = config['debate']['max_turns_per_agent']
        
        # 컴포넌트들
        self.presenter = DebatePresenter(config)
        self.response_generator = ResponseGenerator(config, api_key)
        
        # 토론 데이터
        self.all_statements = []
    
    def announce_debate_format(self, topic: str, duration_minutes: int, panel_agents: List, user_participation: bool = False, user_name: str = None, user_expertise: str = None, system_prompt: str = None) -> None:
        """토론 방식 안내"""
        self.presenter.announce_debate_format(topic, duration_minutes, panel_agents, user_participation, user_name, user_expertise)
        
        # 주제 브리핑 생성 및 출력
        self.presenter.display_topic_briefing_header()
        briefing = self.response_generator.generate_topic_briefing(topic, system_prompt)  # 스트리밍으로 출력됨
        
        # 매니저의 시작 발언
        start_message = self.response_generator.generate_manager_message("토론 시작", f"주제: {topic}")
        self.presenter.display_manager_message(start_message)
    
    def introduce_panels(self, panel_agents: List) -> None:
        """패널 소개"""
        self.presenter.display_panel_introduction_header()
        
        # 매니저의 소개 발언
        intro_message = self.response_generator.generate_manager_message("패널 소개", "")
        self.presenter.display_manager_message(intro_message)
        
        for i, agent in enumerate(panel_agents, 1):
            if agent.is_human:
                # 사용자 소개는 기존 방식 유지
                intro = agent.introduce()
                self.presenter.display_human_response(intro)
            else:
                # AI 패널은 스트리밍 출력 (get_response에서 이미 출력됨)
                self.presenter.display_line_break()
                intro = agent.introduce()
            
            # 다음 패널 소개 전 매니저 발언
            if i < len(panel_agents):
                transition_message = self.response_generator.generate_manager_message("패널 전환", f"{agent.name} 패널의 소개가 끝났습니다. 다음 패널을 소개하겠습니다.")
                self.presenter.display_manager_message(transition_message)
            
            # 사용자가 아닌 경우만 대기
            if not agent.is_human:
                time.sleep(1)
    
    def conduct_debate(self, topic: str, panel_agents: List) -> None:
        """토론 진행"""
        self.presenter.display_debate_start_header()
        
        # 매니저의 토론 시작 발언
        debate_start_message = self.response_generator.generate_manager_message("토론 시작", f"주제: {topic} - 본격적인 토론을 시작하겠습니다.")
        self.presenter.display_manager_message(debate_start_message)
        
        # 모든 패널 발언을 저장할 인스턴스 변수 초기화
        self.all_statements = []
        
        # 1단계: 초기 의견 발표
        self._conduct_initial_opinions_stage(topic, panel_agents)
        
        # 2단계: 상호 토론
        self._conduct_discussion_stage(panel_agents)
    
    def _conduct_initial_opinions_stage(self, topic: str, panel_agents: List) -> None:
        """1단계: 초기 의견 발표"""
        self.presenter.display_stage_header(1, "초기 의견 발표")
        
        # 매니저의 1단계 안내
        stage1_message = self.response_generator.generate_manager_message("단계 안내", "첫 번째 단계로 각 패널의 초기 의견을 들어보겠습니다.")
        self.presenter.display_manager_message(stage1_message)
        
        for i, agent in enumerate(panel_agents, 1):
            # 발언권 넘김
            turn_message = self.response_generator.generate_manager_message("발언권 넘김", f"패널 이름: {agent.name} - 첫 번째 의견을 말씀해 주시기 바랍니다.")
            self.presenter.display_manager_message(turn_message)
            
            if agent.is_human:
                # 사용자 응답은 기존 방식 유지
                response = agent.respond_to_topic(topic)
                self.presenter.display_human_response(response)
            else:
                # AI 패널은 스트리밍 출력 (get_response에서 이미 출력됨)
                self.presenter.display_line_break()
                response = agent.respond_to_topic(topic)
            
            self.all_statements.append({
                'agent_name': agent.name,
                'stage': '초기 의견',
                'content': response
            })
            
            # 다음 발언자 안내 (마지막 패널이 아닌 경우에만)
            if i < len(panel_agents):
                next_message = self.response_generator.generate_manager_message("다음 발언자", f"감사합니다. 이제 다음 패널의 의견을 들어보겠습니다.")
                self.presenter.display_manager_message(next_message)
            
            # 사용자가 아닌 경우만 대기
            if not agent.is_human:
                time.sleep(2)
    
    def _conduct_discussion_stage(self, panel_agents: List) -> None:
        """2단계: 상호 토론"""
        self.presenter.display_stage_header(2, "상호 토론")
        
        # 매니저의 2단계 안내
        stage2_message = self.response_generator.generate_manager_message("단계 전환", "이제 두 번째 단계로 상호 토론을 진행하겠습니다. 각 패널이 다른 의견에 대한 반응과 추가 의견을 말씀해 주시기 바랍니다.")
        self.presenter.display_manager_message(stage2_message)
        
        for turn in range(self.max_turns - 1):
            self.presenter.display_round_header(turn + 1)
            
            # 라운드 시작 안내
            round_message = self.response_generator.generate_manager_message("라운드 시작", f"토론 라운드 {turn + 1}을 시작하겠습니다.")
            self.presenter.display_manager_message(round_message)
            
            for i, agent in enumerate(panel_agents, 1):
                # 발언권 넘김
                turn_message = self.response_generator.generate_manager_message("발언권 넘김", f"패널 이름: {agent.name} - 이번 라운드의 의견을 말씀해 주시기 바랍니다.")
                self.presenter.display_manager_message(turn_message)
                
                context = f"토론 라운드 {turn + 1}"
                # respond_to_debate를 위해 기존 statements 형태 유지
                statements = [stmt['content'] for stmt in self.all_statements]
                
                if agent.is_human:
                    # 사용자 응답은 기존 방식 유지
                    response = agent.respond_to_debate(context, statements)
                    self.presenter.display_human_response(response)
                else:
                    # AI 패널은 스트리밍 출력 (get_response에서 이미 출력됨)
                    self.presenter.display_line_break()
                    response = agent.respond_to_debate(context, statements)
                
                self.all_statements.append({
                    'agent_name': agent.name,
                    'stage': f'토론 라운드 {turn + 1}',
                    'content': response
                })
                
                # 다음 발언자 안내 (마지막 패널이 아닌 경우에만)
                if i < len(panel_agents):
                    next_message = self.response_generator.generate_manager_message("다음 발언자", f"감사합니다. 다음 패널의 의견을 들어보겠습니다.")
                    self.presenter.display_manager_message(next_message)
                
                # 사용자가 아닌 경우만 대기
                if not agent.is_human:
                    time.sleep(2)
    
    def conclude_debate(self, topic: str, panel_agents: List, system_prompt: str) -> None:
        """토론 마무리"""
        self.presenter.display_debate_conclusion_header()
        
        # 매니저의 마무리 시작 발언
        conclude_message = self.response_generator.generate_manager_message("토론 마무리", "이제 토론을 마무리하는 시간입니다.")
        self.presenter.display_manager_message(conclude_message)
        
        # 토론 요약 생성
        summary = self.response_generator.generate_debate_summary(topic, system_prompt)
        
        self.presenter.display_final_opinions_header()
        
        # 매니저의 최종 의견 안내
        final_message = self.response_generator.generate_manager_message("최종 의견 안내", "이제 각 패널의 최종 의견을 들어보겠습니다.")
        self.presenter.display_manager_message(final_message)
        
        for i, agent in enumerate(panel_agents, 1):
            # 발언권 넘김
            turn_message = self.response_generator.generate_manager_message("발언권 넘김", f"패널 이름: {agent.name} - 최종 의견을 말씀해 주시기 바랍니다.")
            self.presenter.display_manager_message(turn_message)
            
            # 현재 패널 제외한 다른 패널들의 발언 수집
            other_panels_statements = [
                stmt for stmt in self.all_statements 
                if stmt['agent_name'] != agent.name
            ]
            
            # 모든 패널에 동일한 인터페이스 사용 (시그니처 통일됨)
            if agent.is_human:
                # 사용자 응답은 기존 방식 유지
                final_response = agent.final_statement(topic, summary, other_panels_statements)
                self.presenter.display_human_response(final_response)
            else:
                # AI 패널은 스트리밍 출력 (get_response에서 이미 출력됨)
                self.presenter.display_line_break()
                final_response = agent.final_statement(topic, summary, other_panels_statements)
            
            # 다음 발언자 안내 (마지막 패널이 아닌 경우에만)
            if i < len(panel_agents):
                next_message = self.response_generator.generate_manager_message("다음 발언자", f"감사합니다. 다음 패널의 최종 의견을 들어보겠습니다.")
                self.presenter.display_manager_message(next_message)
            
            # 사용자가 아닌 경우만 대기
            if not agent.is_human:
                time.sleep(2)
        
        # 최종 결론
        self.presenter.display_debate_conclusion_final_header()
        
        # 매니저의 결론 안내
        conclusion_message = self.response_generator.generate_manager_message("결론 안내", "이제 토론의 종합적인 결론을 말씀드리겠습니다.")
        self.presenter.display_manager_message(conclusion_message)
        
        self.presenter.display_line_break()
        conclusion = self.response_generator.generate_conclusion(topic, panel_agents, summary, system_prompt)  # 스트리밍으로 출력됨
        
        # 매니저의 마무리 인사
        closing_message = self.response_generator.generate_manager_message("마무리 인사", "오늘 토론에 참여해 주신 모든 패널께 감사드립니다. 토론을 마칩니다.")
        self.presenter.display_manager_message(closing_message)
    
    def add_user_as_panelist(self, panel_agents: List, user_name: str, user_expertise: str) -> List:
        """사용자를 패널리스트로 추가"""
        user_participant = PanelHuman(user_name, user_expertise)
        
        # 랜덤한 위치에 사용자 삽입 (첫 번째나 마지막이 아닌 중간 위치)
        if len(panel_agents) > 1:
            # 1번째와 마지막 사이의 랜덤 위치
            insert_position = random.randint(1, len(panel_agents))
        else:
            # 패널이 1명이면 마지막에 추가
            insert_position = len(panel_agents)
        
        panel_agents.insert(insert_position, user_participant)
        self.logger.info(f"사용자 '{user_name}'을 {insert_position + 1}번째 패널로 추가")
        
        return panel_agents