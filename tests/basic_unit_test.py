#!/usr/bin/env python3
"""
기본 단위 테스트 - Mock 없이 기본 기능만 테스트
"""

import sys
import os
import unittest

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.debate_orchestrator import DebateOrchestrator


class TestDebateOrchestratorBasic(unittest.TestCase):
    """기본 기능 테스트 (Mock 없음)"""
    
    def setUp(self):
        """테스트 설정"""
        self.config = {
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
        self.api_key = "test_api_key"
    
    def test_orchestrator_creation(self):
        """오케스트레이터 생성 테스트"""
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            self.assertIsNotNone(orchestrator)
            self.assertEqual(orchestrator.debate_rounds, 3)
            self.assertEqual(orchestrator.config, self.config)
            self.assertEqual(orchestrator.api_key, self.api_key)
            print("✅ 오케스트레이터 생성 성공")
        except Exception as e:
            self.fail(f"오케스트레이터 생성 실패: {e}")
    
    def test_config_loading(self):
        """설정 로딩 테스트"""
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        
        # 설정 값 확인
        self.assertEqual(orchestrator.debate_rounds, 3)
        self.assertEqual(self.config['debate']['mode'], 'dynamic')
        self.assertEqual(self.config['debate']['dynamic_settings']['max_rounds'], 6)
        print("✅ 설정 로딩 성공")
    
    def test_add_user_as_panelist(self):
        """사용자 패널 추가 테스트"""
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        
        # 테스트용 패널 리스트
        test_panels = []
        
        # 사용자 추가
        result = orchestrator.add_user_as_panelist(
            test_panels, 
            "테스트사용자", 
            "테스트전문분야"
        )
        
        # 결과 확인
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "테스트사용자")
        self.assertTrue(result[0].is_human)
        print("✅ 사용자 패널 추가 성공")
    
    def test_add_user_as_panelist_with_existing_panels(self):
        """기존 패널이 있을 때 사용자 추가 테스트"""
        orchestrator = DebateOrchestrator(self.config, self.api_key)
        
        # Mock 패널 생성
        from unittest.mock import Mock
        mock_panel1 = Mock()
        mock_panel1.name = "패널1"
        mock_panel1.is_human = False
        
        mock_panel2 = Mock()
        mock_panel2.name = "패널2"
        mock_panel2.is_human = False
        
        test_panels = [mock_panel1, mock_panel2]
        original_count = len(test_panels)
        
        # 사용자 추가
        result = orchestrator.add_user_as_panelist(
            test_panels, 
            "테스트사용자", 
            "테스트전문분야"
        )
        
        # 결과 확인
        self.assertEqual(len(result), original_count + 1)
        
        # 사용자 패널이 추가되었는지 확인
        user_panel = next((agent for agent in result if agent.name == "테스트사용자"), None)
        self.assertIsNotNone(user_panel)
        self.assertTrue(user_panel.is_human)
        print("✅ 기존 패널과 함께 사용자 추가 성공")


class TestDebateOrchestratorMethods(unittest.TestCase):
    """메서드 테스트 (Mock 사용)"""
    
    def setUp(self):
        """테스트 설정"""
        self.config = {
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
        self.api_key = "test_api_key"
    
    def test_normal_round_basic(self):
        """일반 라운드 기본 테스트"""
        from unittest.mock import Mock, patch
        
        # Mock 패널 생성
        mock_panel1 = Mock()
        mock_panel1.name = "패널1"
        mock_panel1.is_human = False
        mock_panel1.respond_to_debate.return_value = "패널1의 응답"
        
        mock_panel2 = Mock()
        mock_panel2.name = "패널2"
        mock_panel2.is_human = False
        mock_panel2.respond_to_debate.return_value = "패널2의 응답"
        
        test_panels = [mock_panel1, mock_panel2]
        
        # Mock ResponseGenerator와 DebatePresenter
        with patch('src.agents.debate_orchestrator.ResponseGenerator') as mock_response_gen, \
             patch('src.agents.debate_orchestrator.DebatePresenter') as mock_presenter:
            
            # Mock 설정
            mock_response_gen.return_value.generate_manager_message.return_value = "매니저 메시지"
            mock_presenter.return_value.display_manager_message.return_value = None
            mock_presenter.return_value.display_line_break.return_value = None
            
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            
            # 분석 결과
            analysis = {
                'next_action': 'continue_normal',
                'temperature': 'normal'
            }
            
            # 일반 라운드 실행
            result = orchestrator._conduct_normal_round(1, test_panels, analysis)
            
            # 결과 확인
            self.assertTrue(result)
            
            # 각 패널의 respond_to_debate가 호출되었는지 확인
            mock_panel1.respond_to_debate.assert_called()
            mock_panel2.respond_to_debate.assert_called()
            
            print("✅ 일반 라운드 기본 테스트 성공")


def main():
    """메인 테스트 실행"""
    print("🧪 기본 단위 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestDebateOrchestratorBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestDebateOrchestratorMethods))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("🎉 모든 테스트가 성공했습니다!")
        return 0
    else:
        print(f"⚠️ {len(result.failures)}개 실패, {len(result.errors)}개 오류가 발생했습니다.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
