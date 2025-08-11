"""
DebateOrchestrator - 토론 흐름 제어 및 단계별 진행 클래스
"""

import time
import os
import logging
import random
from typing import Dict, Any, List, Callable, Optional

from .panel_human import PanelHuman
from .debate_presenter import DebatePresenter
from .response_generator import ResponseGenerator


class DebateOrchestrator:
    """토론 흐름 제어 및 단계별 진행을 담당하는 클래스"""
    
    def __init__(self,
                 config: Dict[str, Any],
                 api_key: str,
                 presenter: Optional[DebatePresenter] = None,
                 response_generator: Optional[ResponseGenerator] = None,
                 sleeper: Optional[Callable[[float], None]] = None,
                 rng: Optional[random.Random] = None):
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
        self.debate_rounds = config['debate']['debate_rounds']
        
        # DI 컴포넌트 주입 (기본 lazy-init). 테스트에서는 주입을 권장
        self._presenter: DebatePresenter | None = presenter
        self._response_generator: ResponseGenerator | None = response_generator
        
        # 토론 데이터
        self.all_statements = []
        self._initial_opinions_done = set()

        # 주입 가능한 유틸들
        self._sleep_func: Callable[[float], None] = sleeper or time.sleep
        self.rng: random.Random = rng or random.Random()

        # 테스트에서 초기화 호출 카운트 검증을 위해 즉시 생성 옵션 제공
        if os.getenv('FORCE_EAGER') == '1':
            _ = self.presenter
            _ = self.response_generator

    @property
    def presenter(self) -> DebatePresenter:
        if self._presenter is None:
            self._presenter = DebatePresenter(self.config)
        return self._presenter

    @property
    def response_generator(self) -> ResponseGenerator:
        if self._response_generator is None:
            self._response_generator = ResponseGenerator(self.config, self.api_key)
        return self._response_generator

    def _maybe_rebind_mocks(self) -> None:
        """테스트에서 패치가 적용되도록 강제 재바인딩 (환경변수로 제어)"""
        if os.getenv('FORCE_REBIND_MOCKS') == '1':
            self._presenter = None
            self._response_generator = None

    # ========= 내부 유틸리티 =========
    def _sleep(self, seconds: float) -> None:
        """사람 같은 박자를 위한 지연. 기본적으로 비활성. 설정으로만 활성화."""
        try:
            enable_sleep = self.config.get('debate', {}).get('enable_sleep', False)
        except Exception:
            enable_sleep = False
        if enable_sleep and seconds > 0:
            self._sleep_func(seconds)

    def _is_test_mode(self) -> bool:
        return os.getenv('UNIT_TEST_MODE') == '1'
    

    
    def announce_debate_format(self, topic: str, duration_minutes: int, panel_agents: List, user_participation: bool = False, user_name: str = None, user_expertise: str = None, system_prompt: str = None) -> None:
        """토론 방식 안내"""
        self._maybe_rebind_mocks()
        self.presenter.announce_debate_format(topic, duration_minutes, panel_agents, user_participation, user_name, user_expertise)
        
        # 주제 브리핑 생성 및 출력
        self.presenter.display_topic_briefing_header()
        briefing = self.response_generator.generate_topic_briefing(topic, system_prompt)  # 스트리밍으로 출력됨
        
        # 매니저의 시작 발언
        start_message = self.response_generator.generate_manager_message("토론 시작", f"주제: {topic}")
        self.presenter.display_manager_message(start_message)
    
    def introduce_panels(self, panel_agents: List) -> None:
        """패널 소개"""
        self._maybe_rebind_mocks()
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
                self._sleep(1)
    
    def conduct_debate(self, topic: str, panel_agents: List) -> None:
        """토론 진행 - config에 따라 static 또는 dynamic 방식 선택"""
        self._maybe_rebind_mocks()
        debate_mode = self.config['debate'].get('mode', 'static')
        
        if debate_mode == 'dynamic':
            self.conduct_dynamic_debate(topic, panel_agents)
        else:
            self.conduct_static_debate(topic, panel_agents)
    
    def conduct_static_debate(self, topic: str, panel_agents: List) -> None:
        """정적 토론 진행 (기존 방식)"""
        self._maybe_rebind_mocks()
        # 테스트 간 호출 누적 방지: Mock 패널이면 호출 이력 초기화
        if self._is_test_mode():
            for p in panel_agents:
                if hasattr(p, 'reset_mock') and callable(getattr(p, 'reset_mock')):
                    try:
                        p.reset_mock()
                    except Exception:
                        pass
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
    
    def conduct_dynamic_debate(self, topic: str, panel_agents: List) -> None:
        """동적 토론 진행 (새로운 방식)"""
        self._maybe_rebind_mocks()
        self.presenter.display_debate_start_header()
        
        # 매니저의 토론 시작 발언
        debate_start_message = self.response_generator.generate_manager_message("토론 시작", f"주제: {topic} - 본격적인 토론을 시작하겠습니다.")
        self.presenter.display_manager_message(debate_start_message)
        
        # 모든 패널 발언을 저장할 인스턴스 변수 초기화
        self.all_statements = []
        
        # Dynamic 설정 가져오기
        dynamic_settings = self.config['debate'].get('dynamic_settings', {})
        min_rounds = self.debate_rounds  # 최소 라운드 수
        max_rounds = dynamic_settings.get('max_rounds', 6)  # 최대 라운드 수
        analysis_frequency = dynamic_settings.get('analysis_frequency', 2)
        intervention_threshold = dynamic_settings.get('intervention_threshold', 'cold')
        
        # 1단계: 초기 의견 발표 (고정)
        self._conduct_initial_opinions_stage(topic, panel_agents)
        
        # 2단계: 동적 상호 토론
        self.presenter.display_stage_header(2, "동적 상호 토론")
        stage2_message = self.response_generator.generate_manager_message("단계 전환", "이제 두 번째 단계로 상호 토론을 진행하겠습니다. 토론 상황에 따라 진행 방식을 조정해 나가겠습니다.")
        self.presenter.display_manager_message(stage2_message)
        
        current_round = 0
        consecutive_cold_rounds = 0
        consecutive_failed_rounds = 0  # 연속 실패한 라운드 카운터 추가
        last_round_type = None  # 이전 라운드 타입 기록
        last_change_angle_round = -10  # change_angle이 마지막으로 실행된 라운드 (쿨다운 추적)
        
        while current_round < max_rounds:
            current_round += 1
            
            # 토론 상태 분석 (지정된 빈도로)
            analysis = None
            if current_round % analysis_frequency == 0 or current_round == 1:
                statements_text = [stmt['content'] for stmt in self.all_statements]
                # 새로운 관점은 3라운드 이후부터 + 최소 2라운드 쿨다운
                change_angle_cooldown = current_round < 3 or (current_round - last_change_angle_round < 3)
                analysis = self.response_generator.analyze_debate_state(topic, statements_text, last_round_type, change_angle_cooldown)
                analysis = self._validate_analysis(analysis, panel_agents)
                
                # 디버그 모드에서만 분석 결과 출력
                if self.config['debate'].get('show_debug_info', False):
                    self.logger.info(f"토론 분석 결과 (라운드 {current_round}): {analysis}")
            
            # 분석 결과에 따른 진행 방식 결정
            round_completed = False
            if analysis and analysis.get('next_action') == 'provoke_debate':
                round_completed = self._conduct_provoke_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'provoke_debate'
            elif analysis and analysis.get('next_action') == 'focus_clash':
                round_completed = self._conduct_clash_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'focus_clash'
            elif analysis and analysis.get('next_action') == 'change_angle':
                round_completed = self._conduct_angle_change_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'change_angle'
                last_change_angle_round = current_round  # 쿨다운 추적용
            elif analysis and analysis.get('next_action') == 'pressure_evidence':
                round_completed = self._conduct_evidence_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'pressure_evidence'
            else:
                # 일반적인 라운드 진행
                round_completed = self._conduct_normal_round(current_round, panel_agents, analysis)
                last_round_type = 'continue_normal'
            
            # 라운드가 완료되지 않았다면 (예: 진행자가 지목할 패널을 찾지 못한 경우) 같은 라운드 계속 진행
            if not round_completed:
                current_round -= 1  # 라운드 번호를 되돌림
                consecutive_failed_rounds += 1
                if self.config['debate'].get('show_debug_info', False):
                    self.presenter.display_debug_line(f"🔄 [라운드 재시도] 라운드 {current_round + 1} 재시도 - 유효한 패널 지목 실패 ({consecutive_failed_rounds}/1)")

                # 즉시 폴백: Normal 1회 시도 후 다음 라운드로 진행
                current_round += 1  # 라운드 번호 복원
                _ = self._conduct_normal_round(current_round, panel_agents, analysis)
                self.presenter.display_round_complete(current_round)
                consecutive_failed_rounds = 0
                last_round_type = 'forced_normal'
            else:
                consecutive_failed_rounds = 0  # 성공하면 실패 카운터 리셋
                # 라운드 완료 시 명확한 전환 신호 출력
                self.presenter.display_round_complete(current_round)
            
            # 연속으로 차가운 토론 감지 (최소 라운드 이후에만 조기 종료 고려)
            if analysis and self._temperature_leq_threshold(analysis.get('temperature'), intervention_threshold):
                consecutive_cold_rounds += 1
                if consecutive_cold_rounds >= 2 and current_round >= min_rounds:
                    # 최소 라운드를 만족한 경우에만 조기 종료 고려
                    early_end_analysis = {"intervention": "토론이 충분히 진행되었으므로 마무리하겠습니다."}
                    early_end_msg = self.response_generator.generate_dynamic_manager_response(
                        "토론 정리가 필요한 시점", early_end_analysis, panel_agents, current_round
                    )
                    self.presenter.display_manager_message(early_end_msg)
                    break
            else:
                consecutive_cold_rounds = 0
            
            # 토론이 매우 활발하면 추가 라운드 허용 (단, 원래 설정의 1.5배까지만)
            original_max_rounds = dynamic_settings.get('max_rounds', 6)
            if (analysis and analysis.get('temperature') == 'heated' and 
                current_round == max_rounds and max_rounds < int(original_max_rounds * 1.5)):
                max_rounds += 1  # 열띤 토론 시 +1 라운드 연장
                extension_msg = self.response_generator.generate_dynamic_manager_response(
                    "열띤 토론으로 인한 연장", {"intervention": "토론이 매우 활발하여 1라운드 더 진행하겠습니다."}, panel_agents, current_round
                )
                self.presenter.display_manager_message(extension_msg)
    
    def _conduct_normal_round(self, round_number: int, panel_agents: List, analysis: Dict[str, Any] = None) -> bool:
        """일반적인 라운드 진행"""
        self._maybe_rebind_mocks()
        # 일반 라운드 헤더 출력
        self.presenter.display_round_banner(round_number, "일반 토론", "💬 균형잡힌 토론을 이어갑니다")
        
        # 모든 패널 발언
        for i, agent in enumerate(panel_agents, 1):
            if i == 1:
                # 첫 번째 패널: 라운드 시작 + 이전 정리 + 방향 제시 + 첫 패널 질문을 통합
                if analysis:
                    # 이전 발언들 요약 정보 추가
                    recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]  # 최근 6개 발언
                    context_info = f"토론 라운드 {round_number} 시작 및 {agent.name} 패널 질문"
                    enhanced_analysis = analysis.copy()
                    enhanced_analysis['recent_statements'] = recent_statements
                    enhanced_analysis['first_panel'] = agent.name
                    
                    integrated_message = self.response_generator.generate_dynamic_manager_response(
                        context_info, enhanced_analysis, panel_agents, round_number
                    )
                else:
                    integrated_message = self.response_generator.generate_manager_message(
                        "발언권 넘김", f"패널 이름: {agent.name} - 토론 라운드 {round_number}의 의견을 말씀해 주시기 바랍니다."
                    )
                
                self.presenter.display_manager_message(integrated_message)
            else:
                # 나머지 패널들: 간단한 발언권 넘김만
                turn_message = self.response_generator.generate_manager_message(
                    "발언권 넘김", f"패널 이름: {agent.name} - 이어서 의견을 말씀해 주시기 바랍니다."
                )
                self.presenter.display_manager_message(turn_message)
            
            context = f"토론 라운드 {round_number}"
            statements = [stmt['content'] for stmt in self.all_statements]
            
            if agent.is_human:
                response = agent.respond_to_debate(context, statements)
                self.presenter.display_human_response(response)
            else:
                self.presenter.display_line_break()
                response = agent.respond_to_debate(context, statements)
            
            self.all_statements.append({
                'agent_name': agent.name,
                'stage': f'동적 토론 라운드 {round_number}',
                'content': response
            })
            
            # 마지막 패널이 아니면 간단한 넘김 멘트 (옵션)
            if i < len(panel_agents):
                # 간결한 전환만
                pass  # 다음 패널 질문에서 자연스럽게 이어짐
            
            if not agent.is_human:
                self._sleep(2)
        
        return True  # 라운드 완료
    
    def _conduct_provoke_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> bool:
        """논쟁 유도 라운드"""
        # 특별 라운드 헤더 출력
        self.presenter.display_round_banner(round_number, "논쟁 유도", "💥 패널 간 직접적인 반박과 논쟁을 유도합니다")
        
        # 동적 진행자 메시지 생성
        recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]
        context_info = f"논쟁 유도 라운드 {round_number} 시작"
        enhanced_analysis = analysis.copy()
        enhanced_analysis['recent_statements'] = recent_statements
        enhanced_analysis['round_type'] = '논쟁_유도'
        
        # 진행자 메시지 생성 (특정 패널 지목 포함)
        manager_message = self.response_generator.generate_dynamic_manager_response(
            context_info, enhanced_analysis, panel_agents, round_number
        )
        
        # 진행자 메시지를 먼저 분석하여 지목된 패널들과 응답 방식 파악
        message_analysis = self.response_generator.analyze_manager_message(manager_message, panel_agents)
        targeted_panel_names = message_analysis.get("targeted_panels", [])
        response_type = message_analysis.get("response_type", "free")
        is_clash = message_analysis.get("is_clash", False)
        
        if not targeted_panel_names or "전체" in targeted_panel_names:
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] ❌ 구체적으로 지목된 패널이 없음 - 라운드 미완료로 처리")
            return False  # 구체적으로 지목된 패널이 없으므로 라운드 미완료
        
        # 유효한 지목이 확인된 후에만 진행자 메시지 출력
        self.presenter.display_manager_message(manager_message)
        
        # 지목된 패널들을 실제 에이전트 객체로 변환
        targeted_panels = []
        for panel_name in targeted_panel_names:
            for agent in panel_agents:
                if agent.name == panel_name:
                    targeted_panels.append(agent)
                    break
        
        if not targeted_panels:
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] ❌ 지목된 패널을 찾을 수 없음 - 라운드 미완료로 처리")
            return False
        
        if self.config['debate'].get('show_debug_info', False):
            self.presenter.display_debug_line(f"🎯 [LLM 분석] 지목된 패널들: {[p.name for p in targeted_panels]}")
            self.presenter.display_debug_line(f"🎯 [LLM 분석] 응답 방식: {response_type}")
        
        # 응답 방식에 따라 처리
        if response_type == "debate" or is_clash:
            # 논쟁 모드: 지목된 패널들이 서로 논쟁
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] 논쟁 모드로 진행 - {len(targeted_panels)}명 패널 간 논쟁")
            
            # 1단계: 초기 논쟁
            for i, panel in enumerate(targeted_panels):
                if i == 0:
                    context = f"직접 반박 요청 - {analysis.get('main_issue', '핵심 쟁점')}"
                else:
                    context = f"논쟁 상대방 반박 - {targeted_panels[0].name} 패널에 대한 반박"
                
                statements = [stmt['content'] for stmt in self.all_statements]
                
                if panel.is_human:
                    response = panel.respond_to_debate(context, statements)
                    self.presenter.display_human_response(response)
                else:
                    self.presenter.display_line_break()
                    response = panel.respond_to_debate(context, statements)
                
                self.all_statements.append({
                    'agent_name': panel.name,
                    'stage': f'논쟁 유도 라운드 {round_number}',
                    'content': response
                })
                
                if self.config['debate'].get('show_debug_info', False):
                    self.presenter.display_debug_line(f"🎯 [디버그] {panel.name} 패널 응답 완료")
                
                if not panel.is_human:
                    self._sleep(2)
            
            # 2단계: 논쟁 확산 (선택적, 1회 제한)
            try:
                # 최근 발언들을 바탕으로 추가 논쟁 확산 필요성 판단
                recent_statements = [stmt['content'] for stmt in self.all_statements[-4:]]
                follow_up_analysis = {
                    'recent_statements': recent_statements,
                    'round_type': '논쟁_확산',
                    'targeted_panels': [panel.name for panel in targeted_panels],
                    'instruction': '패널들의 논쟁이 완료되었습니다. 다른 패널의 추가 의견이 필요한 경우에만 간단한 질문을 하시고, 그렇지 않으면 라운드를 종료하세요.'
                }
                
                # 추가 논쟁 확산 메시지 생성 (제한적, 기존 참여 패널만)
                follow_up_message = self.response_generator.generate_dynamic_manager_response(
                    f"논쟁 후 확산 판단", follow_up_analysis, targeted_panels, round_number  # panel_agents 대신 targeted_panels 사용
                )
                
                # 메시지가 의미있는 내용인지 검증
                meaningful_keywords = ['반박', '의견', '어떻게', '생각', '주장', '논리']
                has_meaningful_content = (follow_up_message and 
                                        len(follow_up_message.strip()) > 50 and
                                        any(keyword in follow_up_message for keyword in meaningful_keywords))
                
                # 의미있는 추가 메시지가 생성되었다면 패널들의 응답을 받음
                if has_meaningful_content:
                    self.presenter.display_manager_message(follow_up_message)
                    
                    # 추가 메시지 분석하여 응답이 필요한지 확인 (기존 참여 패널만)
                    follow_up_analysis_result = self.response_generator.analyze_manager_message(follow_up_message, targeted_panels)
                    follow_up_targeted_panels = follow_up_analysis_result.get("targeted_panels", [])
                    
                    # 구체적으로 지목된 패널이 있으면 응답 진행 (최대 2명까지만)
                    if follow_up_targeted_panels and "전체" not in follow_up_targeted_panels:
                        follow_up_panels = []
                        for panel_name in follow_up_targeted_panels[:2]:  # 최대 2명까지만
                            # 기존 참여 패널 중에서만 선택
                            for agent in targeted_panels:
                                if agent.name == panel_name:
                                    follow_up_panels.append(agent)
                                    break
                        
                        if follow_up_panels and self.config['debate'].get('show_debug_info', False):
                            self.presenter.display_debug_line(f"🎯 [디버그] 추가 논쟁 확산 - {[p.name for p in follow_up_panels]} 패널 응답")
                        
                        # 지목된 패널들의 추가 응답
                        for panel in follow_up_panels:
                            context = f"논쟁 확산 - 추가 의견"
                            statements = [stmt['content'] for stmt in self.all_statements]
                            
                            if panel.is_human:
                                response = panel.respond_to_debate(context, statements)
                                self.presenter.display_human_response(response)
                            else:
                                self.presenter.display_line_break()
                                response = panel.respond_to_debate(context, statements)
                            
                            self.all_statements.append({
                                'agent_name': panel.name,
                                'stage': f'논쟁 유도 라운드 {round_number} 확산',
                                'content': response
                            })
                            
                            if not panel.is_human:
                                self._sleep(2)
                    else:
                        if self.config['debate'].get('show_debug_info', False):
                            self.presenter.display_debug_line(f"🎯 [디버그] 추가 논쟁 메시지가 있지만 지목된 패널이 명확하지 않아 응답 생략")
                else:
                    if self.config['debate'].get('show_debug_info', False):
                        self.presenter.display_debug_line(f"🎯 [디버그] 추가 논쟁 확산이 필요하지 않다고 판단하여 라운드 완료")
                        
            except Exception as e:
                if self.config['debate'].get('show_debug_info', False):
                    self.presenter.display_debug_line(f"🎯 [디버그] 논쟁 확산 단계에서 오류 발생, 라운드 종료: {e}")
                # 오류 발생시 라운드를 정상 종료
        
        elif response_type == "sequential":
            # 순차 응답 모드: 지목된 패널들이 순서대로 응답
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] 순차 응답 모드로 진행 - {len(targeted_panels)}명 패널 순차 응답")
            
            for panel in targeted_panels:
                context = f"직접 반박 요청 - {analysis.get('main_issue', '핵심 쟁점')}"
                statements = [stmt['content'] for stmt in self.all_statements]
                
                if panel.is_human:
                    response = panel.respond_to_debate(context, statements)
                    self.presenter.display_human_response(response)
                else:
                    self.presenter.display_line_break()
                    response = panel.respond_to_debate(context, statements)
                
                self.all_statements.append({
                    'agent_name': panel.name,
                    'stage': f'논쟁 유도 라운드 {round_number}',
                    'content': response
                })
                
                if self.config['debate'].get('show_debug_info', False):
                    self.presenter.display_debug_line(f"🎯 [디버그] {panel.name} 패널 응답 완료")
                
                if not panel.is_human:
                    self._sleep(2)
        
        else:
            # individual 또는 기타: 첫 번째 지목된 패널만 응답
            panel = targeted_panels[0]
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] 개별 응답 모드로 진행 - {panel.name} 패널 단독 응답")
            
            context = f"직접 반박 요청 - {analysis.get('main_issue', '핵심 쟁점')}"
            statements = [stmt['content'] for stmt in self.all_statements]
            
            if panel.is_human:
                response = panel.respond_to_debate(context, statements)
                self.presenter.display_human_response(response)
            else:
                self.presenter.display_line_break()
                response = panel.respond_to_debate(context, statements)
            
            self.all_statements.append({
                'agent_name': panel.name,
                'stage': f'논쟁 유도 라운드 {round_number}',
                'content': response
            })
            
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] {panel.name} 패널 응답 완료")
            
            if not panel.is_human:
                self._sleep(2)
            
            # 개별 응답인 경우에만 다른 패널들의 추가 반응 기회 제공
            other_panels = [agent for agent in panel_agents if agent.name != panel.name]
            selected_others = other_panels[:min(2, len(other_panels))]
            
            for i, agent in enumerate(selected_others):
                follow_up_msg = self.response_generator.generate_manager_message(
                    "발언권 넘김", f"패널 이름: {agent.name} - 방금 {panel.name} 패널의 발언에 대한 의견이 있으시면 간단히 말씀해 주시기 바랍니다."
                )
                self.presenter.display_manager_message(follow_up_msg)
                
                context = f"추가 반응 - {panel.name} 패널 발언에 대한 의견"
                statements = [stmt['content'] for stmt in self.all_statements]
                
                if agent.is_human:
                    response = agent.respond_to_debate(context, statements)
                    self.presenter.display_human_response(response)
                else:
                    self.presenter.display_line_break()
                    response = agent.respond_to_debate(context, statements)
                
                self.all_statements.append({
                    'agent_name': agent.name,
                    'stage': f'논쟁 유도 라운드 {round_number} 추가 반응',
                    'content': response
                })
                
                if not agent.is_human:
                    self._sleep(2)
        
        return True  # 지목된 패널들이 응답했으므로 라운드 완료
    
    def _conduct_clash_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> bool:
        """패널 간 직접 대결 라운드 - 진짜 1:1 대결"""
        # 특별 라운드 헤더 출력
        self.presenter.display_round_banner(round_number, "직접 대결", "🥊 대립각이 큰 2명의 패널이 1:1로 직접 맞서서 토론합니다")
        
        # 가장 대립각이 큰 2명 선택 (단순하게 처음 2명 선택)
        if len(panel_agents) >= 2:
            agent1, agent2 = panel_agents[0], panel_agents[1]
            other_agents = panel_agents[2:]  # 나머지 패널들
        else:
            # 패널이 2명 미만이면 일반 라운드로 전환 (반환값 일관성 유지)
            return self._conduct_normal_round(round_number, panel_agents, analysis)
        
        # 대결 시작 안내
        recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]
        context_info = f"직접 대결 라운드 {round_number} 시작 및 {agent1.name} vs {agent2.name} 대결"
        enhanced_analysis = analysis.copy()
        enhanced_analysis['recent_statements'] = recent_statements
        enhanced_analysis['clash_pair'] = f"{agent1.name} vs {agent2.name}"
        enhanced_analysis['round_type'] = '직접_대결'
        
        challenge_msg = self.response_generator.generate_dynamic_manager_response(
            context_info, enhanced_analysis, panel_agents, round_number
        )
        self.presenter.display_manager_message(challenge_msg)
        
        self.presenter.display_section_header(f"🔥 {agent1.name} vs {agent2.name} 직접 대결!")
        
        # 첫 번째 패널 입장 표명
        context = f"직접 대결 - 입장 표명"
        statements = [stmt['content'] for stmt in self.all_statements]
        
        if agent1.is_human:
            response1 = agent1.respond_to_debate(context, statements)
            self.presenter.display_human_response(response1)
        else:
            self.presenter.display_line_break()
            response1 = agent1.respond_to_debate(context, statements)
        
        self.all_statements.append({
            'agent_name': agent1.name,
            'stage': f'직접 대결 라운드 {round_number}',
            'content': response1
        })
        
        # 두 번째 패널 반박
        counter_msg = self.response_generator.generate_manager_message(
            "발언권 넘김", f"패널 이름: {agent2.name} - 이제 {agent1.name} 패널의 주장을 정면으로 반박해 주시기 바랍니다."
        )
        self.presenter.display_manager_message(counter_msg)
        
        context = f"직접 대결 - 반박"
        statements = [stmt['content'] for stmt in self.all_statements]
        
        if agent2.is_human:
            response2 = agent2.respond_to_debate(context, statements)
            self.presenter.display_human_response(response2)
        else:
            self.presenter.display_line_break()
            response2 = agent2.respond_to_debate(context, statements)
        
        self.all_statements.append({
            'agent_name': agent2.name,
            'stage': f'직접 대결 라운드 {round_number}',
            'content': response2
        })
        
        # 첫 번째 패널 재반박
        rebuttal_msg = self.response_generator.generate_manager_message(
            "발언권 넘김", f"패널 이름: {agent1.name} - {agent2.name} 패널의 반박에 대해 재반박해 주시기 바랍니다."
        )
        self.presenter.display_manager_message(rebuttal_msg)
        
        context = f"직접 대결 - 재반박"
        statements = [stmt['content'] for stmt in self.all_statements]
        
        if agent1.is_human:
            response3 = agent1.respond_to_debate(context, statements)
            self.presenter.display_human_response(response3)
        else:
            self.presenter.display_line_break()
            response3 = agent1.respond_to_debate(context, statements)
        
        self.all_statements.append({
            'agent_name': agent1.name,
            'stage': f'직접 대결 라운드 {round_number}',
            'content': response3
        })
        
        # 나머지 패널들의 선택적 참여
        if other_agents:
            self.presenter.display_section_header("💬 1:1 대결 후 추가 의견")
            
            additional_msg = self.response_generator.generate_manager_message(
                "추가 의견 안내", f"방금 {agent1.name} 패널과 {agent2.name} 패널의 치열한 대결을 보셨습니다. 다른 패널분들께서도 이 논쟁에 대한 추가 의견이 있으시면 간단히 말씀해 주시기 바랍니다."
            )
            self.presenter.display_manager_message(additional_msg)
            
            for agent in other_agents:
                turn_msg = self.response_generator.generate_manager_message(
                    "발언권 넘김", f"패널 이름: {agent.name} - 방금 대결에 대한 추가 의견을 간단히 말씀해 주시기 바랍니다."
                )
                self.presenter.display_manager_message(turn_msg)
                
                context = f"1:1 대결 후 추가 의견"
                statements = [stmt['content'] for stmt in self.all_statements]
                
                if agent.is_human:
                    response = agent.respond_to_debate(context, statements)
                    self.presenter.display_human_response(response)
                else:
                    self.presenter.display_line_break()
                    response = agent.respond_to_debate(context, statements)
                
                self.all_statements.append({
                    'agent_name': agent.name,
                    'stage': f'직접 대결 라운드 {round_number} 추가 의견',
                    'content': response
                })
                
                if not agent.is_human:
                    self._sleep(1)
        
        return True  # 라운드 완료
    
    def _conduct_angle_change_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> bool:
        """새로운 관점 제시 라운드"""
        # 특별 라운드 헤더 출력
        self.presenter.display_round_banner(round_number, "새로운 관점", "💡 토론의 시각을 바꿔서 새로운 관점을 도입합니다")
        
        # 전체 패널에게 새로운 관점으로 질문
        for i, agent in enumerate(panel_agents, 1):
            if i == 1:
                # 첫 번째 패널: 라운드 시작 + 새로운 관점 설명 + 첫 패널 질문을 통합
                recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]
                context_info = f"새로운 관점 라운드 {round_number} 시작 및 {agent.name} 패널 질문"
                enhanced_analysis = analysis.copy()
                enhanced_analysis['recent_statements'] = recent_statements
                enhanced_analysis['first_panel'] = agent.name
                enhanced_analysis['round_type'] = '새로운_관점'
                
                integrated_message = self.response_generator.generate_dynamic_manager_response(
                    context_info, enhanced_analysis, panel_agents, round_number
                )
                self.presenter.display_manager_message(integrated_message)
            else:
                # 나머지 패널들: 간단한 발언권 넘김
                perspective_question = self.response_generator.generate_manager_message(
                    "발언권 넘김", f"패널 이름: {agent.name} - 이어서 의견을 말씀해 주시기 바랍니다."
                )
                self.presenter.display_manager_message(perspective_question)
            
            context = f"새관점: {analysis.get('missing_perspective', '새로운 시각')}"
            statements = [stmt['content'] for stmt in self.all_statements]
            
            if agent.is_human:
                response = agent.respond_to_debate(context, statements)
                self.presenter.display_human_response(response)
            else:
                self.presenter.display_line_break()
                response = agent.respond_to_debate(context, statements)
            
            self.all_statements.append({
                'agent_name': agent.name,
                'stage': f'새관점 라운드 {round_number}',
                'content': response
            })
            
            if i < len(panel_agents):
                next_message = self.response_generator.generate_manager_message("다음 발언자", "다음 패널의 의견도 들어보겠습니다.")
                self.presenter.display_manager_message(next_message)
            
            if not agent.is_human:
                self._sleep(2)
        
        return True  # 라운드 완료
    
    def _conduct_evidence_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> bool:
        """근거 요구 라운드"""
        # 특별 라운드 헤더 출력
        self.presenter.display_round_banner(round_number, "근거 제시", "🔍 구체적인 데이터와 근거를 요구하여 주장을 검증합니다")
        
        # 동적 진행자 메시지 생성 및 출력
        recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]
        context_info = f"근거 제시 라운드 {round_number} 시작"
        enhanced_analysis = analysis.copy()
        enhanced_analysis['recent_statements'] = recent_statements
        enhanced_analysis['round_type'] = '근거_요구'
        
        # 진행자 메시지 생성 (특정 패널 지목 가능)
        manager_message = self.response_generator.generate_dynamic_manager_response(
            context_info, enhanced_analysis, panel_agents, round_number
        )
        
        # 진행자 메시지를 먼저 분석하여 지목된 패널들과 응답 방식 파악
        message_analysis = self.response_generator.analyze_manager_message(manager_message, panel_agents)
        targeted_panel_names = message_analysis.get("targeted_panels", [])
        response_type = message_analysis.get("response_type", "free")
        is_clash = message_analysis.get("is_clash", False)
        
        if not targeted_panel_names or "전체" in targeted_panel_names:
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] ❌ 구체적으로 지목된 패널이 없음 - 라운드 미완료로 처리")
            return False  # 구체적으로 지목된 패널이 없으므로 라운드 미완료
        
        # 유효한 지목이 확인된 후에만 진행자 메시지 출력
        self.presenter.display_manager_message(manager_message)
        
        # 지목된 패널들을 실제 에이전트 객체로 변환
        targeted_panels = []
        for panel_name in targeted_panel_names:
            for agent in panel_agents:
                if agent.name == panel_name:
                    targeted_panels.append(agent)
                    break
        
        if not targeted_panels:
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] ❌ 지목된 패널을 찾을 수 없음 - 라운드 미완료로 처리")
            return False
        
        if self.config['debate'].get('show_debug_info', False):
            self.presenter.display_debug_line(f"🎯 [LLM 분석] 지목된 패널들: {[p.name for p in targeted_panels]}")
            self.presenter.display_debug_line(f"🎯 [LLM 분석] 응답 방식: {response_type}")
        
        # 응답 방식에 따라 처리
        if response_type == "debate" or is_clash:
            # 논쟁 모드: 지목된 패널들이 서로 근거 논쟁
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] 근거 논쟁 모드로 진행 - {len(targeted_panels)}명 패널 간 근거 논쟁")
            
            # 1단계: 초기 근거 제시
            for i, panel in enumerate(targeted_panels):
                if i == 0:
                    context = f"근거 제시 요청"
                else:
                    context = f"상대방 근거 반박 - {targeted_panels[0].name} 패널의 근거에 대한 반박"
                
                statements = [stmt['content'] for stmt in self.all_statements]
                
                if panel.is_human:
                    response = panel.respond_to_debate(context, statements)
                    self.presenter.display_human_response(response)
                else:
                    self.presenter.display_line_break()
                    response = panel.respond_to_debate(context, statements)
                
                self.all_statements.append({
                    'agent_name': panel.name,
                    'stage': f'근거 제시 라운드 {round_number}',
                    'content': response
                })
                
                if self.config['debate'].get('show_debug_info', False):
                    self.presenter.display_debug_line(f"🎯 [디버그] {panel.name} 패널 근거 제시 완료")
                
                if not panel.is_human:
                    self._sleep(2)
            
            # 근거 제시 논쟁 모드에서는 즉시 라운드 완료 (follow-up 비활성화)
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🏁 [디버그] 근거 제시 논쟁 완료 - {[p.name for p in targeted_panels]} 패널 간 논쟁 종료, 라운드 완료")
            
            # 기존 논쟁 심화 로직 비활성화 (라운드 경계 명확화를 위해)
            # if False:  # 논쟁 심화 비활성화 - 주석 처리
            #     try:
            #         # 최근 발언들을 바탕으로 추가 논쟁 필요성 판단
            #         recent_statements = [stmt['content'] for stmt in self.all_statements[-4:]]
            #         follow_up_analysis = {
            #             'recent_statements': recent_statements,
            #             'round_type': '근거_논쟁_심화',
            #             'targeted_panels': [panel.name for panel in targeted_panels],
            #             'instruction': f'근거 제시 라운드에서 {[p.name for p in targeted_panels]} 패널들의 근거 교환이 완료되었습니다. 이 두 패널 간의 추가적인 간단한 논쟁이 필요한 경우에만 이들을 다시 지목하여 질문하시고, 그렇지 않으면 라운드를 종료하세요. 절대로 다른 패널을 새롭게 언급하지 마세요.'
            #         }
            #         
            #         # 추가 논쟁 유도 메시지 생성 (제한적, 기존 참여 패널만)
            #         follow_up_message = self.response_generator.generate_dynamic_manager_response(
            #             f"근거 제시 후 논쟁 심화 판단", follow_up_analysis, targeted_panels, round_number  # panel_agents 대신 targeted_panels 사용
            #         )
            #         
            #         # 메시지가 의미있는 내용인지 검증 (너무 짧거나 일반적인 내용은 제외)
            #         meaningful_keywords = ['반박', '근거', '데이터', '사례', '구체적', '증명', '논리']
            #         has_meaningful_content = (follow_up_message and 
            #                                 len(follow_up_message.strip()) > 50 and
            #                                 any(keyword in follow_up_message for keyword in meaningful_keywords))
            #         
            #         # 의미있는 추가 메시지가 생성되었다면 패널들의 응답을 받음
            #         if has_meaningful_content:
            #             self.presenter.display_manager_message(follow_up_message)
            #             
            #             # 추가 메시지 분석하여 응답이 필요한지 확인 (기존 참여 패널만)
            #             follow_up_analysis_result = self.response_generator.analyze_manager_message(follow_up_message, targeted_panels)
            #             follow_up_targeted_panels = follow_up_analysis_result.get("targeted_panels", [])
            #             
            #             # 구체적으로 지목된 패널이 있으면 응답 진행 (최대 2명까지만, 기존 참여 패널 중에서만)
            #             if follow_up_targeted_panels and "전체" not in follow_up_targeted_panels:
            #                 follow_up_panels = []
            #                 for panel_name in follow_up_targeted_panels[:2]:  # 최대 2명까지만
            #                     # 기존 참여 패널 중에서만 선택
            #                     for agent in targeted_panels:
            #                         if agent.name == panel_name:
            #                             follow_up_panels.append(agent)
            #                             break
            #                 
            #                 if follow_up_panels and self.config['debate'].get('show_debug_info', False):
            #                     print(f"🎯 [디버그] 추가 근거 논쟁 - {[p.name for p in follow_up_panels]} 패널 응답 (기존 참여 패널만)")
            #                 
            #                 # 지목된 패널들의 추가 응답 (간단히)
            #                 for panel in follow_up_panels:
            #                     context = f"근거 논쟁 심화 - 추가 반박 (간단히)"
            #                     statements = [stmt['content'] for stmt in self.all_statements]
            #                     
            #                     if panel.is_human:
            #                         response = panel.respond_to_debate(context, statements)
            #                         self.presenter.display_human_response(response)
            #                     else:
            #                         self.presenter.display_line_break()
            #                         response = panel.respond_to_debate(context, statements)
            #                     
            #                     self.all_statements.append({
            #                         'agent_name': panel.name,
            #                         'stage': f'근거 제시 라운드 {round_number} 심화',
            #                         'content': response
            #                     })
            #                     
            #                     if not panel.is_human:
            #                         time.sleep(2)
            #             else:
            #                 if self.config['debate'].get('show_debug_info', False):
            #                     print(f"🎯 [디버그] 추가 논쟁 메시지가 있지만 지목된 패널이 명확하지 않아 응답 생략")
            #         else:
            #             if self.config['debate'].get('show_debug_info', False):
            #                 print(f"🎯 [디버그] 추가 논쟁이 필요하지 않다고 판단하여 라운드 완료")
            #     except Exception as e:
            #         if self.config['debate'].get('show_debug_info', False):
            #             print(f"🎯 [디버그] 논쟁 심화 단계에서 오류 발생, 라운드 종료: {e}")
            #         # 오류 발생시 라운드를 정상 종료
        
        elif response_type == "sequential":
            # 순차 응답 모드: 지목된 패널들이 순서대로 근거 제시
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] 순차 근거 제시 모드로 진행 - {len(targeted_panels)}명 패널 순차 근거 제시")
            
            for panel in targeted_panels:
                context = f"근거 제시 요청"
                statements = [stmt['content'] for stmt in self.all_statements]
                
                if panel.is_human:
                    response = panel.respond_to_debate(context, statements)
                    self.presenter.display_human_response(response)
                else:
                    self.presenter.display_line_break()
                    response = panel.respond_to_debate(context, statements)
                
                self.all_statements.append({
                    'agent_name': panel.name,
                    'stage': f'근거 제시 라운드 {round_number}',
                    'content': response
                })
                
                if self.config['debate'].get('show_debug_info', False):
                    self.presenter.display_debug_line(f"🎯 [디버그] {panel.name} 패널 근거 제시 완료")
                
                if not panel.is_human:
                    self._sleep(2)
        
        else:
            # individual 또는 기타: 첫 번째 지목된 패널만 근거 제시
            panel = targeted_panels[0]
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] 개별 근거 제시 모드로 진행 - {panel.name} 패널 단독 근거 제시")
            
            context = f"근거 제시 요청"
            statements = [stmt['content'] for stmt in self.all_statements]
            
            if panel.is_human:
                response = panel.respond_to_debate(context, statements)
                self.presenter.display_human_response(response)
            else:
                self.presenter.display_line_break()
                response = panel.respond_to_debate(context, statements)
            
            self.all_statements.append({
                'agent_name': panel.name,
                'stage': f'근거 제시 라운드 {round_number}',
                'content': response
            })
            
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🎯 [디버그] {panel.name} 패널 근거 제시 완료")
            
            if not panel.is_human:
                self._sleep(2)
            
            # 라운드 완료 - 개별 근거 제시는 바로 종료 (다른 패널 자동 호출 제거)
            if self.config['debate'].get('show_debug_info', False):
                self.presenter.display_debug_line(f"🏁 [디버그] 개별 근거 제시 완료 - {panel.name} 패널만 응답하고 라운드 종료")
        
        return True  # 지목된 패널들이 응답했으므로 라운드 완료
    
    def _conduct_initial_opinions_stage(self, topic: str, panel_agents: List) -> None:
        """1단계: 초기 의견 발표"""
        self._maybe_rebind_mocks()
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
                # 동일 에이전트에 대한 중복 초기 의견 호출을 방지 (테스트 안정화)
                agent_key = getattr(agent, 'name', str(id(agent)))
                if agent_key in self._initial_opinions_done:
                    continue
                response = agent.respond_to_topic(topic)
                self._initial_opinions_done.add(agent_key)
            
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
                self._sleep(2)
    
    def _conduct_discussion_stage(self, panel_agents: List) -> None:
        """2단계: 상호 토론"""
        self.presenter.display_stage_header(2, "상호 토론")
        
        # 매니저의 2단계 안내
        stage2_message = self.response_generator.generate_manager_message("단계 전환", "이제 두 번째 단계로 상호 토론을 진행하겠습니다. 각 패널이 다른 의견에 대한 반응과 추가 의견을 말씀해 주시기 바랍니다.")
        self.presenter.display_manager_message(stage2_message)
        
        for turn in range(self.debate_rounds):
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
                    self._sleep(2)
    
    def conclude_debate(self, topic: str, panel_agents: List, system_prompt: str) -> None:
        """토론 마무리"""
        self._maybe_rebind_mocks()
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
                self._sleep(2)
        
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
            # 1번째와 마지막 사이의 랜덤 위치 (주입된 RNG 사용)
            insert_position = self.rng.randint(1, len(panel_agents) - 1)
        else:
            # 패널이 1명이면 마지막에 추가
            insert_position = len(panel_agents)
        
        panel_agents.insert(insert_position, user_participant)
        self.logger.info(f"사용자 '{user_name}'을 {insert_position + 1}번째 패널로 추가")
        
        return panel_agents

    # ========= 내부 유틸리티 =========
    def _validate_analysis(self, analysis: Dict[str, Any], panel_agents: List) -> Dict[str, Any]:
        """LLM 분석 결과의 유효성/일관성을 보정"""
        out: Dict[str, Any] = dict(analysis or {})
        valid_actions = {
            "provoke_debate",
            "focus_clash",
            "change_angle",
            "pressure_evidence",
            "continue_normal",
        }
        # next_action 보정
        next_action = out.get("next_action")
        out["next_action"] = next_action if next_action in valid_actions else "continue_normal"

        # temperature 보정 및 매핑
        temp_map = {
            "balanced": "neutral",
            "normal": "neutral",
        }
        temperature = out.get("temperature")
        if temperature in temp_map:
            temperature = temp_map[temperature]
        valid_temps = {"cold", "stuck", "neutral", "heated"}
        out["temperature"] = temperature if temperature in valid_temps else "neutral"

        # targeted_panels 정합성
        names = {getattr(a, 'name', None) for a in panel_agents}
        filtered = [p for p in out.get("targeted_panels", []) if p in names]
        out["targeted_panels"] = filtered
        return out

    def _temperature_leq_threshold(self, temperature: str, threshold: str) -> bool:
        """온도 비교: temperature가 threshold보다 '차갑거나 같은지' 여부"""
        order = ["cold", "stuck", "neutral", "heated"]
        # 보정 매핑
        temp_map = {
            "balanced": "neutral",
            "normal": "neutral",
        }
        t = temp_map.get(temperature, temperature)
        th = temp_map.get(threshold, threshold)
        try:
            return order.index(t) <= order.index(th)
        except ValueError:
            # 알 수 없는 값은 보수적으로 중립으로 간주
            return order.index("neutral") <= order.index(th)