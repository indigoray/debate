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
        self.debate_rounds = config['debate']['debate_rounds']
        
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
        """토론 진행 - config에 따라 static 또는 dynamic 방식 선택"""
        debate_mode = self.config['debate'].get('mode', 'static')
        
        if debate_mode == 'dynamic':
            self.conduct_dynamic_debate(topic, panel_agents)
        else:
            self.conduct_static_debate(topic, panel_agents)
    
    def conduct_static_debate(self, topic: str, panel_agents: List) -> None:
        """정적 토론 진행 (기존 방식)"""
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
        last_round_type = None  # 이전 라운드 타입 기록
        last_change_angle_round = -10  # change_angle이 마지막으로 실행된 라운드 (쿨다운 추적)
        
        while current_round < max_rounds:
            current_round += 1
            
            # 토론 상태 분석 (지정된 빈도로)
            analysis = None
            if current_round % analysis_frequency == 0 or current_round == 1:
                statements_text = [stmt['content'] for stmt in self.all_statements]
                change_angle_cooldown = current_round - last_change_angle_round < 3  # 2라운드 쿨다운
                analysis = self.response_generator.analyze_debate_state(topic, statements_text, last_round_type, change_angle_cooldown)
                
                # 디버그 모드에서만 분석 결과 출력
                if self.config['debate'].get('show_debug_info', False):
                    self.logger.info(f"토론 분석 결과 (라운드 {current_round}): {analysis}")
            
            # 분석 결과에 따른 진행 방식 결정
            if analysis and analysis.get('next_action') == 'provoke_debate':
                self._conduct_provoke_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'provoke_debate'
            elif analysis and analysis.get('next_action') == 'focus_clash':
                self._conduct_clash_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'focus_clash'
            elif analysis and analysis.get('next_action') == 'change_angle':
                self._conduct_angle_change_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'change_angle'
                last_change_angle_round = current_round  # 쿨다운 추적용
            elif analysis and analysis.get('next_action') == 'pressure_evidence':
                self._conduct_evidence_round(current_round, topic, panel_agents, analysis)
                last_round_type = 'pressure_evidence'
            else:
                # 일반적인 라운드 진행
                self._conduct_normal_round(current_round, panel_agents, analysis)
                last_round_type = 'continue_normal'
            
            # 연속으로 차가운 토론 감지 (최소 라운드 이후에만 조기 종료 고려)
            if analysis and analysis.get('temperature') in ['cold', 'stuck']:
                consecutive_cold_rounds += 1
                if consecutive_cold_rounds >= 2 and current_round >= min_rounds:
                    # 최소 라운드를 만족한 경우에만 조기 종료 고려
                    early_end_analysis = {"intervention": "토론이 충분히 진행되었으므로 마무리하겠습니다."}
                    early_end_msg = self.response_generator.generate_dynamic_manager_response(
                        "토론 정리가 필요한 시점", early_end_analysis, panel_agents
                    )
                    self.presenter.display_manager_message(early_end_msg)
                    break
            else:
                consecutive_cold_rounds = 0
            
            # 토론이 매우 활발하면 추가 라운드 허용 (단, 원래 설정의 1.5배까지만)
            original_max_rounds = dynamic_settings.get('max_rounds', 6)
            if (analysis and analysis.get('temperature') == 'heated' and 
                current_round == max_rounds and max_rounds < int(original_max_rounds * 1.5)):
                max_rounds += 1  # 2라운드 -> 1라운드로 축소
                extension_msg = self.response_generator.generate_dynamic_manager_response(
                    "열띤 토론으로 인한 연장", {"intervention": "토론이 매우 활발하여 1라운드 더 진행하겠습니다."}, panel_agents
                )
                self.presenter.display_manager_message(extension_msg)
    
    def _conduct_normal_round(self, round_number: int, panel_agents: List, analysis: Dict[str, Any] = None) -> None:
        """일반적인 라운드 진행"""
        # 일반 라운드 헤더 출력
        print(f"\n📝 === 일반 토론 라운드 {round_number} === 📝")
        print("💬 균형잡힌 토론을 이어갑니다")
        print("=" * 50)
        
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
                        context_info, enhanced_analysis, panel_agents
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
                time.sleep(2)
    
    def _conduct_provoke_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> None:
        """논쟁 유도 라운드"""
        # 특별 라운드 헤더 출력
        print(f"\n🔥 === 논쟁 유도 라운드 {round_number} === 🔥")
        print("💥 패널 간 직접적인 반박과 논쟁을 유도합니다")
        print("=" * 50)
        
        # 대립각이 큰 패널들을 우선 선택 (처음 2명, 나중에 더 정교한 선택 가능)
        selected_agents = panel_agents[:min(2, len(panel_agents))]
        
        for i, agent in enumerate(selected_agents):
            if i == 0:
                # 첫 번째 패널: 라운드 시작 + 논쟁 유도 설명 + 첫 패널 질문을 통합
                recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]
                context_info = f"논쟁 유도 라운드 {round_number} 시작 및 {agent.name} 패널 질문"
                enhanced_analysis = analysis.copy()
                enhanced_analysis['recent_statements'] = recent_statements
                enhanced_analysis['first_panel'] = agent.name
                enhanced_analysis['round_type'] = '논쟁_유도'
                
                integrated_message = self.response_generator.generate_dynamic_manager_response(
                    context_info, enhanced_analysis, panel_agents
                )
                self.presenter.display_manager_message(integrated_message)
            else:
                # 나머지 패널들: 간단한 발언권 넘김
                direct_question = self.response_generator.generate_manager_message(
                    "발언권 넘김", f"패널 이름: {agent.name} - 이어서 의견을 말씀해 주시기 바랍니다."
                )
                self.presenter.display_manager_message(direct_question)
            
            # 해당 패널의 응답 받기
            context = f"직접 반박 요청 - {analysis.get('main_issue', '핵심 쟁점')}"
            statements = [stmt['content'] for stmt in self.all_statements]
            
            if agent.is_human:
                response = agent.respond_to_debate(context, statements)
                self.presenter.display_human_response(response)
            else:
                self.presenter.display_line_break()
                response = agent.respond_to_debate(context, statements)
            
            self.all_statements.append({
                'agent_name': agent.name,
                'stage': f'논쟁 유도 라운드 {round_number}',
                'content': response
            })
            
            if not agent.is_human:
                time.sleep(2)
    
    def _conduct_clash_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> None:
        """패널 간 직접 대결 라운드 - 진짜 1:1 대결"""
        # 특별 라운드 헤더 출력
        print(f"\n⚔️  === 직접 대결 라운드 {round_number} === ⚔️")
        print("🥊 대립각이 큰 2명의 패널이 1:1로 직접 맞서서 토론합니다")
        print("=" * 60)
        
        # 가장 대립각이 큰 2명 선택 (단순하게 처음 2명 선택)
        if len(panel_agents) >= 2:
            agent1, agent2 = panel_agents[0], panel_agents[1]
            other_agents = panel_agents[2:]  # 나머지 패널들
        else:
            # 패널이 2명 미만이면 일반 라운드로 전환
            self._conduct_normal_round(round_number, panel_agents, analysis)
            return
        
        # 대결 시작 안내
        recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]
        context_info = f"직접 대결 라운드 {round_number} 시작 및 {agent1.name} vs {agent2.name} 대결"
        enhanced_analysis = analysis.copy()
        enhanced_analysis['recent_statements'] = recent_statements
        enhanced_analysis['clash_pair'] = f"{agent1.name} vs {agent2.name}"
        enhanced_analysis['round_type'] = '직접_대결'
        
        challenge_msg = self.response_generator.generate_dynamic_manager_response(
            context_info, enhanced_analysis, panel_agents
        )
        self.presenter.display_manager_message(challenge_msg)
        
        print(f"\n🔥 {agent1.name} vs {agent2.name} 직접 대결!")
        print(f"{'='*50}")
        
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
            print(f"\n💬 1:1 대결 후 추가 의견")
            print(f"{'='*40}")
            
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
                    time.sleep(1)
    
    def _conduct_angle_change_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> None:
        """새로운 관점 제시 라운드"""
        # 특별 라운드 헤더 출력
        print(f"\n🔄 === 새로운 관점 라운드 {round_number} === 🔄")
        print("💡 토론의 시각을 바꿔서 새로운 관점을 도입합니다")
        print("=" * 50)
        
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
                    context_info, enhanced_analysis, panel_agents
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
                time.sleep(2)
    
    def _conduct_evidence_round(self, round_number: int, topic: str, panel_agents: List, analysis: Dict[str, Any]) -> None:
        """근거 요구 라운드"""
        # 특별 라운드 헤더 출력
        print(f"\n📋 === 근거 제시 라운드 {round_number} === 📋")
        print("🔍 구체적인 데이터와 근거를 요구하여 주장을 검증합니다")
        print("=" * 50)
        
        # 각 패널에게 구체적 근거 요구
        for i, agent in enumerate(panel_agents, 1):
            if i == 1:
                # 첫 번째 패널: 라운드 시작 + 근거 요구 설명 + 첫 패널 질문을 통합
                recent_statements = [stmt['content'] for stmt in self.all_statements[-6:]]
                context_info = f"근거 제시 라운드 {round_number} 시작 및 {agent.name} 패널 질문"
                enhanced_analysis = analysis.copy()
                enhanced_analysis['recent_statements'] = recent_statements
                enhanced_analysis['first_panel'] = agent.name
                enhanced_analysis['round_type'] = '근거_요구'
                
                integrated_message = self.response_generator.generate_dynamic_manager_response(
                    context_info, enhanced_analysis, panel_agents
                )
                self.presenter.display_manager_message(integrated_message)
            else:
                # 나머지 패널들: 간단한 발언권 넘김
                evidence_request = self.response_generator.generate_manager_message(
                    "발언권 넘김", f"패널 이름: {agent.name} - 이어서 근거를 제시해 주시기 바랍니다."
                )
                self.presenter.display_manager_message(evidence_request)
            
            context = f"근거 제시 요청"
            statements = [stmt['content'] for stmt in self.all_statements]
            
            if agent.is_human:
                response = agent.respond_to_debate(context, statements)
                self.presenter.display_human_response(response)
            else:
                self.presenter.display_line_break()
                response = agent.respond_to_debate(context, statements)
            
            self.all_statements.append({
                'agent_name': agent.name,
                'stage': f'근거 제시 라운드 {round_number}',
                'content': response
            })
            
            if i < len(panel_agents):
                next_message = self.response_generator.generate_manager_message("다음 발언자", "다음 패널도 근거를 제시해주시기 바랍니다.")
                self.presenter.display_manager_message(next_message)
            
            if not agent.is_human:
                time.sleep(2)
    
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