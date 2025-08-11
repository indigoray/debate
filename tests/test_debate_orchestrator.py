"""
DebateOrchestrator 테스트 스위트
각 라운드별로 토론 진행이 원활한지 테스트하는 환경
"""

import unittest
import sys
import os
import yaml
import os
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.debate_orchestrator import DebateOrchestrator
from src.agents.panel_agent import PanelAgent
from src.agents.panel_human import PanelHuman


class TestDebateOrchestrator(unittest.TestCase):
    """DebateOrchestrator 종합 테스트 클래스"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화"""
        # 로깅 설정
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_debate_orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)
        
        # 테스트용 설정 로드
        cls.config = cls._load_test_config()
        cls.api_key = "test_api_key"
        
        # 테스트용 패널 에이전트 생성
        cls.test_panel_agents = cls._create_test_panel_agents()
        
        cls.logger.info("테스트 환경 초기화 완료")
    
    @classmethod
    def _load_test_config(cls) -> Dict[str, Any]:
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
    
    @classmethod
    def _create_test_panel_agents(cls) -> List:
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
    
    def setUp(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.orchestrator = DebateOrchestrator(self.config, self.api_key)
        self.test_topic = "인공지능의 윤리적 문제"
        self.logger.info(f"테스트 시작: {self._testMethodName}")
    
    def tearDown(self):
        """각 테스트 메서드 실행 후 정리"""
        self.logger.info(f"테스트 완료: {self._testMethodName}")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_orchestrator_initialization(self, mock_presenter, mock_response_generator):
        """오케스트레이터 초기화 테스트"""
        self.logger.info("오케스트레이터 초기화 테스트 시작")
        
        # Mock 객체들이 올바르게 생성되었는지 확인
        mock_presenter.assert_called_once_with(self.config)
        mock_response_generator.assert_called_once_with(self.config, self.api_key)
        
        # 설정이 올바르게 로드되었는지 확인
        self.assertEqual(self.orchestrator.debate_rounds, 3)
        self.assertEqual(self.orchestrator.config, self.config)
        self.assertEqual(self.orchestrator.api_key, self.api_key)
        
        self.logger.info("오케스트레이터 초기화 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_announce_debate_format(self, mock_presenter, mock_response_generator):
        """토론 방식 안내 테스트"""
        self.logger.info("토론 방식 안내 테스트 시작")
        
        # Mock 설정
        mock_presenter_instance = mock_presenter.return_value
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 테스트 실행
        self.orchestrator.announce_debate_format(
            self.test_topic, 
            10, 
            self.test_panel_agents
        )
        
        # Mock 메서드들이 호출되었는지 확인
        mock_presenter_instance.announce_debate_format.assert_called_once()
        mock_presenter_instance.display_topic_briefing_header.assert_called_once()
        mock_response_generator_instance.generate_topic_briefing.assert_called_once()
        mock_response_generator_instance.generate_manager_message.assert_called()
        
        self.logger.info("토론 방식 안내 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_introduce_panels(self, mock_presenter, mock_response_generator):
        """패널 소개 테스트"""
        self.logger.info("패널 소개 테스트 시작")
        
        # Mock 설정
        mock_presenter_instance = mock_presenter.return_value
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 테스트 실행
        self.orchestrator.introduce_panels(self.test_panel_agents)
        
        # 각 패널의 introduce 메서드가 호출되었는지 확인
        for agent in self.test_panel_agents:
            agent.introduce.assert_called_once()
        
        # Presenter와 ResponseGenerator 메서드들이 호출되었는지 확인
        mock_presenter_instance.display_panel_introduction_header.assert_called_once()
        mock_response_generator_instance.generate_manager_message.assert_called()
        
        self.logger.info("패널 소개 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_conduct_static_debate(self, mock_presenter, mock_response_generator):
        """정적 토론 진행 테스트"""
        self.logger.info("정적 토론 진행 테스트 시작")
        
        # Mock 설정
        mock_presenter_instance = mock_presenter.return_value
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 테스트 실행
        self.orchestrator.conduct_static_debate(self.test_topic, self.test_panel_agents)
        
        # 초기 의견 발표와 상호 토론이 진행되었는지 확인
        mock_presenter_instance.display_debate_start_header.assert_called_once()
        mock_presenter_instance.display_stage_header.assert_called()
        mock_response_generator_instance.generate_manager_message.assert_called()
        
        # 각 패널의 respond_to_topic과 respond_to_debate가 호출되었는지 확인
        for agent in self.test_panel_agents:
            agent.respond_to_topic.assert_called_once()
            # 라운드 수만큼 respond_to_debate가 호출되었는지 확인
            self.assertEqual(agent.respond_to_debate.call_count, self.config['debate']['debate_rounds'])
        
        self.logger.info("정적 토론 진행 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_conduct_dynamic_debate(self, mock_presenter, mock_response_generator):
        """동적 토론 진행 테스트"""
        self.logger.info("동적 토론 진행 테스트 시작")
        
        # Mock 설정
        mock_presenter_instance = mock_presenter.return_value
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정
        mock_analysis = {
            'next_action': 'continue_normal',
            'temperature': 'normal',
            'main_issue': '테스트 쟁점'
        }
        mock_response_generator_instance.analyze_debate_state.return_value = mock_analysis
        
        # 테스트 실행
        self.orchestrator.conduct_dynamic_debate(self.test_topic, self.test_panel_agents)
        
        # 동적 토론 관련 메서드들이 호출되었는지 확인
        mock_presenter_instance.display_debate_start_header.assert_called_once()
        mock_response_generator_instance.analyze_debate_state.assert_called()
        
        self.logger.info("동적 토론 진행 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_provoke_round(self, mock_presenter, mock_response_generator):
        """논쟁 유도 라운드 테스트"""
        self.logger.info("논쟁 유도 라운드 테스트 시작")
        
        # Mock 설정
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정 (논쟁 유도)
        mock_analysis = {
            'next_action': 'provoke_debate',
            'main_issue': '핵심 쟁점',
            'targeted_panels': ['김경제', '박사회']
        }
        
        # 메시지 분석 Mock 설정
        mock_message_analysis = {
            'targeted_panels': ['김경제', '박사회'],
            'response_type': 'debate',
            'is_clash': True
        }
        mock_response_generator_instance.analyze_manager_message.return_value = mock_message_analysis
        
        # 테스트 실행
        result = self.orchestrator._conduct_provoke_round(1, self.test_topic, self.test_panel_agents, mock_analysis)
        
        # 결과 확인
        self.assertTrue(result)
        
        # 지목된 패널들의 respond_to_debate가 호출되었는지 확인
        targeted_agents = [agent for agent in self.test_panel_agents if agent.name in ['김경제', '박사회']]
        for agent in targeted_agents:
            agent.respond_to_debate.assert_called()
        
        self.logger.info("논쟁 유도 라운드 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_clash_round(self, mock_presenter, mock_response_generator):
        """직접 대결 라운드 테스트"""
        self.logger.info("직접 대결 라운드 테스트 시작")
        
        # Mock 설정
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정 (직접 대결)
        mock_analysis = {
            'next_action': 'focus_clash',
            'main_issue': '핵심 쟁점'
        }
        
        # 테스트 실행
        result = self.orchestrator._conduct_clash_round(1, self.test_topic, self.test_panel_agents, mock_analysis)
        
        # 결과 확인
        self.assertTrue(result)
        
        # 첫 번째와 두 번째 패널의 respond_to_debate가 호출되었는지 확인
        self.test_panel_agents[0].respond_to_debate.assert_called()
        self.test_panel_agents[1].respond_to_debate.assert_called()
        
        self.logger.info("직접 대결 라운드 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_angle_change_round(self, mock_presenter, mock_response_generator):
        """새로운 관점 라운드 테스트"""
        self.logger.info("새로운 관점 라운드 테스트 시작")
        
        # Mock 설정
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정 (새로운 관점)
        mock_analysis = {
            'next_action': 'change_angle',
            'missing_perspective': '새로운 시각'
        }
        
        # 테스트 실행
        result = self.orchestrator._conduct_angle_change_round(1, self.test_topic, self.test_panel_agents, mock_analysis)
        
        # 결과 확인
        self.assertTrue(result)
        
        # 모든 패널의 respond_to_debate가 호출되었는지 확인
        for agent in self.test_panel_agents:
            agent.respond_to_debate.assert_called()
        
        self.logger.info("새로운 관점 라운드 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_evidence_round(self, mock_presenter, mock_response_generator):
        """근거 제시 라운드 테스트"""
        self.logger.info("근거 제시 라운드 테스트 시작")
        
        # Mock 설정
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정 (근거 요구)
        mock_analysis = {
            'next_action': 'pressure_evidence',
            'main_issue': '핵심 쟁점'
        }
        
        # 메시지 분석 Mock 설정
        mock_message_analysis = {
            'targeted_panels': ['김경제'],
            'response_type': 'individual',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = mock_message_analysis
        
        # 테스트 실행
        result = self.orchestrator._conduct_evidence_round(1, self.test_topic, self.test_panel_agents, mock_analysis)
        
        # 결과 확인
        self.assertTrue(result)
        
        # 지목된 패널의 respond_to_debate가 호출되었는지 확인
        targeted_agent = next(agent for agent in self.test_panel_agents if agent.name == '김경제')
        targeted_agent.respond_to_debate.assert_called()
        
        self.logger.info("근거 제시 라운드 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_clash_round_returns_bool_on_insufficient_panels(self, mock_presenter, mock_response_generator):
        """직접 대결 라운드: 패널이 2명 미만일 때 반환값 일관성 테스트"""
        self.logger.info("직접 대결 라운드 반환값 일관성 테스트 시작")

        limited_panels = self.test_panel_agents[:1]
        mock_analysis = {'next_action': 'focus_clash'}

        result = self.orchestrator._conduct_clash_round(1, self.test_topic, limited_panels, mock_analysis)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        self.logger.info("직접 대결 라운드 반환값 일관성 테스트 완료")

    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_presenter_banner_called_in_normal_round(self, mock_presenter, mock_response_generator):
        """일반 라운드에서 배너 출력 호출 여부 테스트"""
        self.logger.info("일반 라운드 배너 출력 호출 테스트 시작")

        mock_presenter_instance = mock_presenter.return_value

        # Mock 패널 2명 구성
        p1, p2 = self.test_panel_agents[0], self.test_panel_agents[1]
        panels = [p1, p2]

        analysis = {'next_action': 'continue_normal', 'temperature': 'normal'}
        result = self.orchestrator._conduct_normal_round(1, panels, analysis)
        self.assertTrue(result)

        mock_presenter_instance.display_round_banner.assert_called_once()
        self.logger.info("일반 라운드 배너 출력 호출 테스트 완료")

    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_normal_round(self, mock_presenter, mock_response_generator):
        """일반 라운드 테스트"""
        self.logger.info("일반 라운드 테스트 시작")
        
        # Mock 설정
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정 (일반 진행)
        mock_analysis = {
            'next_action': 'continue_normal',
            'temperature': 'normal'
        }
        
        # 테스트 실행
        result = self.orchestrator._conduct_normal_round(1, self.test_panel_agents, mock_analysis)
        
        # 결과 확인
        self.assertTrue(result)
        
        # 모든 패널의 respond_to_debate가 호출되었는지 확인
        for agent in self.test_panel_agents:
            agent.respond_to_debate.assert_called()
        
        self.logger.info("일반 라운드 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_conclude_debate(self, mock_presenter, mock_response_generator):
        """토론 마무리 테스트"""
        self.logger.info("토론 마무리 테스트 시작")
        
        # Mock 설정
        mock_presenter_instance = mock_presenter.return_value
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 테스트 실행
        self.orchestrator.conclude_debate(self.test_topic, self.test_panel_agents, "테스트 시스템 프롬프트")
        
        # 마무리 관련 메서드들이 호출되었는지 확인
        mock_presenter_instance.display_debate_conclusion_header.assert_called_once()
        mock_presenter_instance.display_final_opinions_header.assert_called_once()
        mock_presenter_instance.display_debate_conclusion_final_header.assert_called_once()
        
        # 각 패널의 final_statement가 호출되었는지 확인
        for agent in self.test_panel_agents:
            agent.final_statement.assert_called_once()
        
        # ResponseGenerator 메서드들이 호출되었는지 확인
        mock_response_generator_instance.generate_debate_summary.assert_called_once()
        mock_response_generator_instance.generate_conclusion.assert_called_once()
        
        self.logger.info("토론 마무리 테스트 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    @unittest.skipIf(os.getenv('EXCLUDE_USER_TESTS') == '1', 'User participation tests excluded')
    def test_add_user_as_panelist(self, mock_presenter, mock_response_generator):
        """사용자 패널 추가 테스트"""
        self.logger.info("사용자 패널 추가 테스트 시작")
        
        # 테스트 실행
        original_count = len(self.test_panel_agents)
        result = self.orchestrator.add_user_as_panelist(
            self.test_panel_agents, 
            "테스트사용자", 
            "테스트전문분야"
        )
        
        # 결과 확인
        self.assertEqual(len(result), original_count + 1)
        
        # 사용자 패널이 추가되었는지 확인
        user_panel = next((agent for agent in result if agent.name == "테스트사용자"), None)
        self.assertIsNotNone(user_panel)
        self.assertTrue(user_panel.is_human)
        
        self.logger.info("사용자 패널 추가 테스트 완료")
    
    def test_error_handling_in_provoke_round(self):
        """논쟁 유도 라운드에서의 오류 처리 테스트"""
        self.logger.info("논쟁 유도 라운드 오류 처리 테스트 시작")
        
        # 잘못된 분석 결과로 테스트
        invalid_analysis = {
            'next_action': 'provoke_debate',
            'main_issue': '핵심 쟁점'
            # targeted_panels가 없음
        }
        
        # Mock 설정
        with patch.object(self.orchestrator.response_generator, 'analyze_manager_message') as mock_analyze:
            mock_analyze.return_value = {
                'targeted_panels': [],  # 빈 리스트
                'response_type': 'free'
            }
            
            # 테스트 실행 - 오류가 발생하지 않아야 함
            result = self.orchestrator._conduct_provoke_round(1, self.test_topic, self.test_panel_agents, invalid_analysis)
            
            # 결과 확인 - 구체적으로 지목된 패널이 없으면 False 반환
            self.assertFalse(result)
        
        self.logger.info("논쟁 유도 라운드 오류 처리 테스트 완료")
    
    def test_error_handling_in_evidence_round(self):
        """근거 제시 라운드에서의 오류 처리 테스트"""
        self.logger.info("근거 제시 라운드 오류 처리 테스트 시작")
        
        # 잘못된 분석 결과로 테스트
        invalid_analysis = {
            'next_action': 'pressure_evidence',
            'main_issue': '핵심 쟁점'
            # targeted_panels가 없음
        }
        
        # Mock 설정
        with patch.object(self.orchestrator.response_generator, 'analyze_manager_message') as mock_analyze:
            mock_analyze.return_value = {
                'targeted_panels': [],  # 빈 리스트
                'response_type': 'free'
            }
            
            # 테스트 실행 - 오류가 발생하지 않아야 함
            result = self.orchestrator._conduct_evidence_round(1, self.test_topic, self.test_panel_agents, invalid_analysis)
            
            # 결과 확인 - 구체적으로 지목된 패널이 없으면 False 반환
            self.assertFalse(result)
        
        self.logger.info("근거 제시 라운드 오류 처리 테스트 완료")


class TestDebateOrchestratorIntegration(unittest.TestCase):
    """DebateOrchestrator 통합 테스트 클래스"""
    
    @classmethod
    def setUpClass(cls):
        """통합 테스트 클래스 초기화"""
        cls.logger = logging.getLogger(__name__)
        cls.config = TestDebateOrchestrator._load_test_config()
        cls.api_key = "test_api_key"
        cls.test_panel_agents = TestDebateOrchestrator._create_test_panel_agents()
        cls.test_topic = "인공지능의 윤리적 문제"
        
        cls.logger.info("통합 테스트 환경 초기화 완료")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_full_debate_flow(self, mock_presenter, mock_response_generator):
        """전체 토론 흐름 통합 테스트"""
        self.logger.info("전체 토론 흐름 통합 테스트 시작")
        
        # Mock 설정
        mock_presenter_instance = mock_presenter.return_value
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정
        mock_analysis = {
            'next_action': 'continue_normal',
            'temperature': 'normal',
            'main_issue': '테스트 쟁점'
        }
        mock_response_generator_instance.analyze_debate_state.return_value = mock_analysis
        
        # 오케스트레이터 생성
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        
        # 전체 토론 흐름 실행
        orchestrator.announce_debate_format(self.test_topic, 10, self.test_panel_agents)
        orchestrator.introduce_panels(self.test_panel_agents)
        orchestrator.conduct_debate(self.test_topic, self.test_panel_agents)
        orchestrator.conclude_debate(self.test_topic, self.test_panel_agents, "테스트 시스템 프롬프트")
        
        # 모든 주요 메서드들이 호출되었는지 확인
        mock_presenter_instance.announce_debate_format.assert_called_once()
        mock_presenter_instance.display_panel_introduction_header.assert_called_once()
        mock_presenter_instance.display_debate_start_header.assert_called_once()
        mock_presenter_instance.display_debate_conclusion_header.assert_called_once()
        
        # 각 패널의 모든 메서드들이 호출되었는지 확인
        for agent in self.test_panel_agents:
            agent.introduce.assert_called_once()
            agent.respond_to_topic.assert_called_once()
            agent.final_statement.assert_called_once()
            # respond_to_debate는 라운드 수에 따라 여러 번 호출됨
            self.assertGreater(agent.respond_to_debate.call_count, 0)
        
        self.logger.info("전체 토론 흐름 통합 테스트 완료")


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
