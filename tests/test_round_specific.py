"""
라운드별 상세 테스트 스크립트
각 라운드의 구체적인 동작을 테스트하는 환경
"""

import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.debate_orchestrator import DebateOrchestrator
from src.agents.panel_agent import PanelAgent


class RoundSpecificTester:
    """라운드별 상세 테스트 클래스"""
    
    def __init__(self):
        """테스트 환경 초기화"""
        self.logger = logging.getLogger(__name__)
        self.config = self._load_test_config()
        self.api_key = "test_api_key"
        self.test_panel_agents = self._create_test_panel_agents()
        self.test_topic = "인공지능의 윤리적 문제"
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('round_specific_test.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger.info("라운드별 테스트 환경 초기화 완료")
    
    def _load_test_config(self) -> Dict[str, Any]:
        """테스트용 설정 로드"""
        config = {
            'debate': {
                'debate_rounds': 3,
                'mode': 'dynamic',
                'show_debug_info': True,
                'dynamic_settings': {
                    'max_rounds': 6,
                    'analysis_frequency': 2,
                    'intervention_threshold': 'cold'
                }
            },
            'ai': {
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000
            },
            'presentation': {
                'show_timestamps': True,
                'show_agent_names': True
            }
        }
        return config
    
    def _create_test_panel_agents(self) -> List:
        """테스트용 패널 에이전트 생성"""
        agents = []
        
        # 테스트용 AI 패널 에이전트들
        test_agents_data = [
            {
                'name': '김경제',
                'expertise': '경제학',
                'background': '서울대 경제학과 교수',
                'personality': '논리적이고 데이터 중심적'
            },
            {
                'name': '박사회',
                'expertise': '사회학',
                'background': '연세대 사회학과 교수',
                'personality': '인간 중심적이고 공감적'
            },
            {
                'name': '이기술',
                'expertise': '기술학',
                'background': 'KAIST 컴퓨터공학과 교수',
                'personality': '혁신적이고 미래 지향적'
            },
            {
                'name': '최정책',
                'expertise': '정책학',
                'background': '고려대 정책학과 교수',
                'personality': '실용적이고 정책 중심적'
            }
        ]
        
        for agent_data in test_agents_data:
            agent = Mock(spec=PanelAgent)
            agent.name = agent_data['name']
            agent.expertise = agent_data['expertise']
            agent.background = agent_data['background']
            agent.personality = agent_data['personality']
            agent.is_human = False
            
            # Mock 메서드들 설정
            agent.introduce.return_value = f"{agent.name}입니다. {agent.expertise} 전문가입니다."
            agent.respond_to_topic.return_value = f"{agent.name}의 초기 의견입니다."
            agent.respond_to_debate.return_value = f"{agent.name}의 토론 응답입니다."
            agent.final_statement.return_value = f"{agent.name}의 최종 의견입니다."
            
            agents.append(agent)
        
        return agents
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_provoke_round_scenarios(self, mock_presenter, mock_response_generator):
        """논쟁 유도 라운드 시나리오 테스트"""
        self.logger.info("=== 논쟁 유도 라운드 시나리오 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 시나리오 1: 2명 패널 간 논쟁
        self.logger.info("시나리오 1: 2명 패널 간 논쟁 테스트")
        analysis_1 = {
            'next_action': 'provoke_debate',
            'main_issue': '경제적 효율성 vs 사회적 가치',
            'targeted_panels': ['김경제', '박사회']
        }
        
        message_analysis_1 = {
            'targeted_panels': ['김경제', '박사회'],
            'response_type': 'debate',
            'is_clash': True
        }
        mock_response_generator_instance.analyze_manager_message.return_value = message_analysis_1
        
        result_1 = orchestrator._conduct_provoke_round(1, self.test_topic, self.test_panel_agents, analysis_1)
        self.logger.info(f"시나리오 1 결과: {result_1}")
        
        # 시나리오 2: 개별 패널 지목
        self.logger.info("시나리오 2: 개별 패널 지목 테스트")
        analysis_2 = {
            'next_action': 'provoke_debate',
            'main_issue': '기술 발전의 속도',
            'targeted_panels': ['이기술']
        }
        
        message_analysis_2 = {
            'targeted_panels': ['이기술'],
            'response_type': 'individual',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = message_analysis_2
        
        result_2 = orchestrator._conduct_provoke_round(2, self.test_topic, self.test_panel_agents, analysis_2)
        self.logger.info(f"시나리오 2 결과: {result_2}")
        
        # 시나리오 3: 잘못된 분석 결과 (오류 처리)
        self.logger.info("시나리오 3: 잘못된 분석 결과 테스트")
        analysis_3 = {
            'next_action': 'provoke_debate',
            'main_issue': '테스트 쟁점'
            # targeted_panels가 없음
        }
        
        message_analysis_3 = {
            'targeted_panels': [],
            'response_type': 'free'
        }
        mock_response_generator_instance.analyze_manager_message.return_value = message_analysis_3
        
        result_3 = orchestrator._conduct_provoke_round(3, self.test_topic, self.test_panel_agents, analysis_3)
        self.logger.info(f"시나리오 3 결과: {result_3}")
        
        self.logger.info("=== 논쟁 유도 라운드 시나리오 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_clash_round_scenarios(self, mock_presenter, mock_response_generator):
        """직접 대결 라운드 시나리오 테스트"""
        self.logger.info("=== 직접 대결 라운드 시나리오 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        
        # 시나리오 1: 정상적인 1:1 대결
        self.logger.info("시나리오 1: 정상적인 1:1 대결 테스트")
        analysis_1 = {
            'next_action': 'focus_clash',
            'main_issue': '자유시장 vs 규제'
        }
        
        result_1 = orchestrator._conduct_clash_round(1, self.test_topic, self.test_panel_agents, analysis_1)
        self.logger.info(f"시나리오 1 결과: {result_1}")
        
        # 시나리오 2: 패널이 2명 미만인 경우
        self.logger.info("시나리오 2: 패널이 2명 미만인 경우 테스트")
        limited_panels = self.test_panel_agents[:1]  # 1명만
        
        result_2 = orchestrator._conduct_clash_round(2, self.test_topic, limited_panels, analysis_1)
        self.logger.info(f"시나리오 2 결과: {result_2}")
        
        self.logger.info("=== 직접 대결 라운드 시나리오 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_angle_change_round_scenarios(self, mock_presenter, mock_response_generator):
        """새로운 관점 라운드 시나리오 테스트"""
        self.logger.info("=== 새로운 관점 라운드 시나리오 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        
        # 시나리오 1: 새로운 관점 제시
        self.logger.info("시나리오 1: 새로운 관점 제시 테스트")
        analysis_1 = {
            'next_action': 'change_angle',
            'missing_perspective': '국제적 관점'
        }
        
        result_1 = orchestrator._conduct_angle_change_round(1, self.test_topic, self.test_panel_agents, analysis_1)
        self.logger.info(f"시나리오 1 결과: {result_1}")
        
        # 시나리오 2: 다른 새로운 관점
        self.logger.info("시나리오 2: 다른 새로운 관점 테스트")
        analysis_2 = {
            'next_action': 'change_angle',
            'missing_perspective': '미래 세대 관점'
        }
        
        result_2 = orchestrator._conduct_angle_change_round(2, self.test_topic, self.test_panel_agents, analysis_2)
        self.logger.info(f"시나리오 2 결과: {result_2}")
        
        self.logger.info("=== 새로운 관점 라운드 시나리오 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_evidence_round_scenarios(self, mock_presenter, mock_response_generator):
        """근거 제시 라운드 시나리오 테스트"""
        self.logger.info("=== 근거 제시 라운드 시나리오 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 시나리오 1: 개별 근거 제시
        self.logger.info("시나리오 1: 개별 근거 제시 테스트")
        analysis_1 = {
            'next_action': 'pressure_evidence',
            'main_issue': 'AI 윤리 가이드라인의 효과성'
        }
        
        message_analysis_1 = {
            'targeted_panels': ['김경제'],
            'response_type': 'individual',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = message_analysis_1
        
        result_1 = orchestrator._conduct_evidence_round(1, self.test_topic, self.test_panel_agents, analysis_1)
        self.logger.info(f"시나리오 1 결과: {result_1}")
        
        # 시나리오 2: 순차 근거 제시
        self.logger.info("시나리오 2: 순차 근거 제시 테스트")
        analysis_2 = {
            'next_action': 'pressure_evidence',
            'main_issue': 'AI 규제의 경제적 영향'
        }
        
        message_analysis_2 = {
            'targeted_panels': ['김경제', '이기술'],
            'response_type': 'sequential',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = message_analysis_2
        
        result_2 = orchestrator._conduct_evidence_round(2, self.test_topic, self.test_panel_agents, analysis_2)
        self.logger.info(f"시나리오 2 결과: {result_2}")
        
        # 시나리오 3: 근거 논쟁
        self.logger.info("시나리오 3: 근거 논쟁 테스트")
        analysis_3 = {
            'next_action': 'pressure_evidence',
            'main_issue': 'AI 윤리 교육의 필요성'
        }
        
        message_analysis_3 = {
            'targeted_panels': ['박사회', '최정책'],
            'response_type': 'debate',
            'is_clash': True
        }
        mock_response_generator_instance.analyze_manager_message.return_value = message_analysis_3
        
        result_3 = orchestrator._conduct_evidence_round(3, self.test_topic, self.test_panel_agents, analysis_3)
        self.logger.info(f"시나리오 3 결과: {result_3}")
        
        self.logger.info("=== 근거 제시 라운드 시나리오 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_normal_round_scenarios(self, mock_presenter, mock_response_generator):
        """일반 라운드 시나리오 테스트"""
        self.logger.info("=== 일반 라운드 시나리오 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        
        # 시나리오 1: 분석 결과가 있는 경우
        self.logger.info("시나리오 1: 분석 결과가 있는 경우 테스트")
        analysis_1 = {
            'next_action': 'continue_normal',
            'temperature': 'normal',
            'main_issue': '일반적인 토론 진행'
        }
        
        result_1 = orchestrator._conduct_normal_round(1, self.test_panel_agents, analysis_1)
        self.logger.info(f"시나리오 1 결과: {result_1}")
        
        # 시나리오 2: 분석 결과가 없는 경우
        self.logger.info("시나리오 2: 분석 결과가 없는 경우 테스트")
        result_2 = orchestrator._conduct_normal_round(2, self.test_panel_agents, None)
        self.logger.info(f"시나리오 2 결과: {result_2}")
        
        self.logger.info("=== 일반 라운드 시나리오 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_dynamic_debate_flow(self, mock_presenter, mock_response_generator):
        """동적 토론 흐름 테스트"""
        self.logger.info("=== 동적 토론 흐름 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 다양한 분석 결과 시뮬레이션
        analysis_sequence = [
            {'next_action': 'continue_normal', 'temperature': 'normal'},
            {'next_action': 'provoke_debate', 'temperature': 'cold', 'main_issue': '논쟁 유도'},
            {'next_action': 'focus_clash', 'temperature': 'heated'},
            {'next_action': 'change_angle', 'temperature': 'normal', 'missing_perspective': '새로운 관점'},
            {'next_action': 'pressure_evidence', 'temperature': 'cold', 'main_issue': '근거 요구'},
            {'next_action': 'continue_normal', 'temperature': 'normal'}
        ]
        
        # 각 라운드별로 다른 분석 결과 반환
        mock_response_generator_instance.analyze_debate_state.side_effect = analysis_sequence
        
        # 메시지 분석 Mock 설정
        mock_message_analysis = {
            'targeted_panels': ['김경제', '박사회'],
            'response_type': 'debate',
            'is_clash': True
        }
        mock_response_generator_instance.analyze_manager_message.return_value = mock_message_analysis
        
        # 동적 토론 실행
        self.logger.info("동적 토론 실행 시작")
        orchestrator.conduct_dynamic_debate(self.test_topic, self.test_panel_agents)
        self.logger.info("동적 토론 실행 완료")
        
        # 분석 메서드가 여러 번 호출되었는지 확인
        self.logger.info(f"분석 메서드 호출 횟수: {mock_response_generator_instance.analyze_debate_state.call_count}")
        
        self.logger.info("=== 동적 토론 흐름 테스트 완료 ===")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.logger.info("=== 모든 라운드별 테스트 시작 ===")
        
        try:
            self.test_provoke_round_scenarios()
            self.test_clash_round_scenarios()
            self.test_angle_change_round_scenarios()
            self.test_evidence_round_scenarios()
            self.test_normal_round_scenarios()
            self.test_dynamic_debate_flow()
            
            self.logger.info("=== 모든 라운드별 테스트 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"테스트 실행 중 오류 발생: {e}")
            return False


def main():
    """메인 실행 함수"""
    tester = RoundSpecificTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ 모든 라운드별 테스트가 성공적으로 완료되었습니다.")
    else:
        print("❌ 일부 테스트에서 오류가 발생했습니다. 로그를 확인해주세요.")
    
    return success


if __name__ == '__main__':
    main()
