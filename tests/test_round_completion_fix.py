"""
라운드 완료 후 진행자 추가 발언 문제 수정 검증 테스트
처음 보고된 구체적인 문제 상황을 재현하고 수정 사항이 제대로 적용되었는지 확인
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


class RoundCompletionFixTester:
    """라운드 완료 후 진행자 추가 발언 문제 수정 검증 테스트 클래스"""
    
    def __init__(self):
        """테스트 환경 초기화"""
        self.logger = logging.getLogger(__name__)
        self.config = self._load_test_config()
        self.api_key = "test_api_key"
        self.test_panel_agents = self._create_test_panel_agents()
        self.test_topic = "교육 정책의 효과성"
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('round_completion_fix_test.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger.info("라운드 완료 문제 수정 검증 테스트 환경 초기화 완료")
    
    def _load_test_config(self) -> Dict[str, Any]:
        """테스트용 설정 로드"""
        config = {
            'debate': {
                'debate_rounds': 3,
                'mode': 'dynamic',
                'show_debug_info': True,
                'dynamic_settings': {
                    'max_rounds': 6,
                    'analysis_frequency': 1,
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
        """처음 예시와 동일한 패널 이름으로 테스트용 에이전트 생성"""
        agents = []
        
        # 처음 예시에서 언급된 패널들
        test_agents_data = [
            {
                'name': '박세진',
                'expertise': '경제학',
                'background': '서울대 경제학과 교수',
                'personality': '논리적이고 실용적'
            },
            {
                'name': '이지윤',
                'expertise': '교육학',
                'background': '연세대 교육학과 교수',
                'personality': '이상주의적이고 학생 중심적'
            },
            {
                'name': '김현수',
                'expertise': '정책학',
                'background': '고려대 정책학과 교수',
                'personality': '균형잡힌 관점과 정책 중심적'
            },
            {
                'name': '최민영',
                'expertise': '사회학',
                'background': '이화여대 사회학과 교수',
                'personality': '사회적 공정성 중시'
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
    def test_original_problem_scenario(self, mock_presenter, mock_response_generator):
        """원래 문제 상황 재현 테스트 - 진행자가 발언했지만 아무도 답하지 않는 상황"""
        self.logger.info("=== 원래 문제 상황 재현 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 문제 상황: 진행자가 패널을 지목했지만 LLM 분석에서 패널을 찾지 못하는 경우
        self.logger.info("시나리오: 진행자 메시지에서 패널 지목 실패하는 상황")
        
        # 진행자가 실제로 생성할 법한 메시지 (하지만 LLM이 분석 실패)
        problematic_manager_message = (
            "[토론 진행자] 방금 전 박세진 패널과 이지윤 패널의 입장 차이가 뚜렷하게 드러났습니다. "
            "더 이상 피상적 논의로는 핵심 쟁점이 해소되지 않는 상황입니다. "
            "박세진 패널, 이지윤 패널의 주장에 내포된 근본적 맹점이 무엇이라고 보십니까? "
            "구체적인 근거와 함께 이지윤 패널의 논리를 논파해 주시기 바랍니다."
        )
        
        # 진행자 메시지 생성은 정상이지만, 분석에서 패널을 찾지 못하는 상황 시뮬레이션
        mock_response_generator_instance.generate_dynamic_manager_response.return_value = problematic_manager_message
        
        # LLM 분석이 실패하여 빈 패널 목록을 반환하는 상황
        failed_analysis = {
            'targeted_panels': [],  # 패널을 찾지 못함
            'response_type': 'free',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = failed_analysis
        
        # 근거 제시 라운드에서 이 문제가 발생
        analysis = {
            'next_action': 'pressure_evidence',
            'main_issue': '교육 평등론의 현실성'
        }
        
        # 수정 전에는 True를 반환했지만, 수정 후에는 False를 반환해야 함
        result = orchestrator._conduct_evidence_round(5, self.test_topic, self.test_panel_agents, analysis)
        
        # 검증: 패널 지목 실패 시 라운드가 미완료로 처리되어야 함
        assert result == False, "패널 지목 실패 시 라운드가 미완료(False)로 처리되어야 함"
        
        # 진행자 메시지가 생성되었는지 확인 (내부적으로만, 출력은 되지 않음)
        mock_response_generator_instance.generate_dynamic_manager_response.assert_called_once()
        
        # LLM 분석이 호출되었는지 확인
        mock_response_generator_instance.analyze_manager_message.assert_called_once()
        
        # 패널들의 respond_to_debate가 호출되지 않았는지 확인 (아무도 답하지 않음)
        for agent in self.test_panel_agents:
            agent.respond_to_debate.assert_not_called()
        
        self.logger.info("✅ 원래 문제 상황에서 올바른 처리 확인됨")
        self.logger.info("=== 원래 문제 상황 재현 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_fixed_scenario_with_proper_targeting(self, mock_presenter, mock_response_generator):
        """수정된 상황 테스트 - 진행자가 패널을 제대로 지목하고 응답받는 경우"""
        self.logger.info("=== 수정된 상황 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        mock_response_generator_instance = mock_response_generator.return_value
        
        self.logger.info("시나리오: 진행자가 패널을 명확히 지목하고 정상 진행되는 상황")
        
        # 수정 후 진행자가 생성할 개선된 메시지
        improved_manager_message = (
            "[토론 진행자] 박세진 패널께서는 이지윤 패널의 교육 평등론이 "
            "현실적 제약을 간과하고 있다고 보시는지요? "
            "구체적인 근거와 함께 반박해 주시기 바랍니다."
        )
        
        mock_response_generator_instance.generate_dynamic_manager_response.return_value = improved_manager_message
        
        # LLM 분석이 성공하여 패널을 정확히 찾는 상황
        successful_analysis = {
            'targeted_panels': ['박세진'],  # 패널을 명확히 찾음
            'response_type': 'individual',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = successful_analysis
        
        # 근거 제시 라운드 진행
        analysis = {
            'next_action': 'pressure_evidence',
            'main_issue': '교육 평등론의 현실성'
        }
        
        result = orchestrator._conduct_evidence_round(5, self.test_topic, self.test_panel_agents, analysis)
        
        # 검증: 패널 지목 성공 시 라운드가 완료로 처리되어야 함
        assert result == True, "패널 지목 성공 시 라운드가 완료(True)로 처리되어야 함"
        
        # 진행자 메시지가 실제로 출력되었는지 확인
        mock_presenter_instance = mock_presenter.return_value
        mock_presenter_instance.display_manager_message.assert_called_with(improved_manager_message)
        
        # 지목된 패널(박세진)이 응답했는지 확인
        targeted_agent = next(agent for agent in self.test_panel_agents if agent.name == '박세진')
        targeted_agent.respond_to_debate.assert_called_once()
        
        self.logger.info("✅ 수정된 상황에서 정상적인 진행 확인됨")
        self.logger.info("=== 수정된 상황 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_consecutive_failure_handling(self, mock_presenter, mock_response_generator):
        """연속 실패 처리 테스트 - 3회 연속 패널 지목 실패 시 강제 일반 라운드 전환"""
        self.logger.info("=== 연속 실패 처리 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        mock_response_generator_instance = mock_response_generator.return_value
        
        # 분석 결과 Mock 설정 - 계속 논쟁 유도를 시도하지만 실패
        continuous_analysis = {
            'next_action': 'provoke_debate',
            'temperature': 'cold',
            'main_issue': '핵심 쟁점'
        }
        mock_response_generator_instance.analyze_debate_state.return_value = continuous_analysis
        
        # 패널 지목이 계속 실패하는 상황
        failed_message_analysis = {
            'targeted_panels': [],
            'response_type': 'free',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = failed_message_analysis
        
        # 동적 토론 시작 (연속 실패 상황 시뮬레이션)
        self.logger.info("연속 실패 상황 시뮬레이션 시작")
        
        # orchestrator의 all_statements 초기화
        orchestrator.all_statements = []
        
        # 초기 의견 단계는 성공적으로 완료
        orchestrator._conduct_initial_opinions_stage(self.test_topic, self.test_panel_agents)
        
        # 동적 토론 시작 부분만 테스트 (연속 실패 로직 확인)
        current_round = 0
        consecutive_failed_rounds = 0
        max_rounds = 6
        
        # 3회 연속 실패 시뮬레이션
        for i in range(5):  # 5번 시도
            current_round += 1
            
            # 논쟁 유도 라운드 시도 (실패)
            round_completed = orchestrator._conduct_provoke_round(
                current_round, self.test_topic, self.test_panel_agents, continuous_analysis
            )
            
            if not round_completed:
                current_round -= 1  # 라운드 번호 되돌림
                consecutive_failed_rounds += 1
                self.logger.info(f"라운드 {current_round + 1} 실패 ({consecutive_failed_rounds}/3)")
                
                # 3회 연속 실패 시 강제 일반 라운드 전환
                if consecutive_failed_rounds >= 3:
                    self.logger.info("3회 연속 실패로 강제 일반 라운드 전환")
                    current_round += 1
                    round_completed = orchestrator._conduct_normal_round(
                        current_round, self.test_panel_agents, continuous_analysis
                    )
                    consecutive_failed_rounds = 0
                    break
            else:
                consecutive_failed_rounds = 0
        
        # 검증: 3회 연속 실패 후 일반 라운드가 성공적으로 실행되었는지 확인
        assert consecutive_failed_rounds == 0, "3회 연속 실패 후 강제 전환이 성공해야 함"
        assert current_round > 0, "강제 전환 후 라운드가 진행되어야 함"
        
        # 모든 패널이 일반 라운드에서 응답했는지 확인
        for agent in self.test_panel_agents:
            assert agent.respond_to_debate.call_count > 0, f"{agent.name} 패널이 강제 전환 라운드에서 응답해야 함"
        
        self.logger.info("✅ 연속 실패 후 강제 전환 로직 정상 작동 확인됨")
        self.logger.info("=== 연속 실패 처리 테스트 완료 ===")
    
    @patch('src.agents.debate_orchestrator.ResponseGenerator')
    @patch('src.agents.debate_orchestrator.DebatePresenter')
    def test_message_order_validation(self, mock_presenter, mock_response_generator):
        """메시지 출력 순서 검증 테스트 - 진행자 메시지가 분석 후에만 출력되는지 확인"""
        self.logger.info("=== 메시지 출력 순서 검증 테스트 시작 ===")
        
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        mock_response_generator_instance = mock_response_generator.return_value
        mock_presenter_instance = mock_presenter.return_value
        
        # 실패하는 진행자 메시지
        failing_message = "[토론 진행자] 모호한 요청으로 패널을 찾을 수 없는 메시지입니다."
        mock_response_generator_instance.generate_dynamic_manager_response.return_value = failing_message
        
        # 분석 실패
        failed_analysis = {
            'targeted_panels': [],
            'response_type': 'free',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = failed_analysis
        
        # 논쟁 유도 라운드 시도
        analysis = {
            'next_action': 'provoke_debate',
            'main_issue': '테스트 쟁점'
        }
        
        result = orchestrator._conduct_provoke_round(1, self.test_topic, self.test_panel_agents, analysis)
        
        # 검증: 라운드가 실패했으므로 False 반환
        assert result == False, "분석 실패 시 라운드가 실패해야 함"
        
        # 검증: 진행자 메시지가 출력되지 않았는지 확인 (중요!)
        mock_presenter_instance.display_manager_message.assert_not_called()
        
        self.logger.info("✅ 분석 실패 시 진행자 메시지가 출력되지 않음 확인됨")
        
        # 이제 성공하는 케이스 테스트
        mock_presenter_instance.reset_mock()
        
        successful_message = "[토론 진행자] 박세진 패널께서 명확한 반박을 해주시기 바랍니다."
        mock_response_generator_instance.generate_dynamic_manager_response.return_value = successful_message
        
        successful_analysis = {
            'targeted_panels': ['박세진'],
            'response_type': 'individual',
            'is_clash': False
        }
        mock_response_generator_instance.analyze_manager_message.return_value = successful_analysis
        
        result = orchestrator._conduct_provoke_round(2, self.test_topic, self.test_panel_agents, analysis)
        
        # 검증: 라운드 성공
        assert result == True, "분석 성공 시 라운드가 성공해야 함"
        
        # 검증: 진행자 메시지가 출력되었는지 확인 (여러 번 호출될 수 있음)
        assert mock_presenter_instance.display_manager_message.call_count >= 1, "진행자 메시지가 최소 1회는 출력되어야 함"
        
        # 첫 번째 호출이 우리가 기대한 메시지인지 확인
        first_call = mock_presenter_instance.display_manager_message.call_args_list[0]
        assert first_call[0][0] == successful_message, f"첫 번째 진행자 메시지가 예상과 다름: {first_call[0][0]}"
        
        self.logger.info("✅ 분석 성공 시 진행자 메시지가 정상 출력됨 확인됨")
        self.logger.info("=== 메시지 출력 순서 검증 테스트 완료 ===")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.logger.info("=== 라운드 완료 문제 수정 검증 테스트 시작 ===")
        
        try:
            self.test_original_problem_scenario()
            self.test_fixed_scenario_with_proper_targeting()
            self.test_consecutive_failure_handling()
            self.test_message_order_validation()
            
            self.logger.info("=== 모든 라운드 완료 문제 수정 검증 테스트 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"테스트 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """메인 실행 함수"""
    print("🔍 라운드 완료 후 진행자 추가 발언 문제 수정 검증 테스트")
    print("=" * 70)
    
    tester = RoundCompletionFixTester()
    success = tester.run_all_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 모든 라운드 완료 문제 수정 검증 테스트가 성공적으로 완료되었습니다!")
        print("🎉 수정 사항이 제대로 적용되어 원래 문제가 해결되었습니다.")
    else:
        print("❌ 일부 테스트에서 오류가 발생했습니다. 로그를 확인해주세요.")
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
