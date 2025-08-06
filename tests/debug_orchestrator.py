"""
DebateOrchestrator 디버깅 도구
실제 오류를 진단하고 수정하기 위한 도구
"""

import sys
import os
import logging
import traceback
import yaml
from typing import Dict, Any, List, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.debate_orchestrator import DebateOrchestrator
from src.agents.panel_agent import PanelAgent
from src.agents.panel_human import PanelHuman


class DebateOrchestratorDebugger:
    """DebateOrchestrator 디버깅 클래스"""
    
    def __init__(self, config_path: str = None, api_key: str = None):
        """디버거 초기화"""
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.api_key = api_key or "test_api_key"
        self.test_panel_agents = self._create_test_panel_agents()
        self.test_topic = "인공지능의 윤리적 문제"
        
        self.logger.info("디버거 초기화 완료")
    
    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('debug_orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """설정 파일 로드"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            # 기본 테스트 설정
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
        
        self.logger.info(f"설정 로드 완료: {config_path or '기본 설정'}")
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
            agent = PanelAgent(
                name=agent_data['name'],
                expertise=agent_data['expertise'],
                background=agent_data['background'],
                personality=agent_data['personality'],
                config=self.config,
                api_key=self.api_key
            )
            agents.append(agent)
        
        self.logger.info(f"테스트 패널 에이전트 {len(agents)}개 생성 완료")
        return agents
    
    def debug_orchestrator_initialization(self) -> bool:
        """오케스트레이터 초기화 디버깅"""
        self.logger.info("=== 오케스트레이터 초기화 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            self.logger.info("✅ 오케스트레이터 초기화 성공")
            
            # 설정 확인
            self.logger.info(f"설정 로드 확인: debate_rounds={orchestrator.debate_rounds}")
            self.logger.info(f"API 키 설정 확인: {bool(orchestrator.api_key)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 오케스트레이터 초기화 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_announce_debate_format(self) -> bool:
        """토론 방식 안내 디버깅"""
        self.logger.info("=== 토론 방식 안내 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            orchestrator.announce_debate_format(
                self.test_topic, 
                10, 
                self.test_panel_agents
            )
            self.logger.info("✅ 토론 방식 안내 성공")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 토론 방식 안내 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_introduce_panels(self) -> bool:
        """패널 소개 디버깅"""
        self.logger.info("=== 패널 소개 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            orchestrator.introduce_panels(self.test_panel_agents)
            self.logger.info("✅ 패널 소개 성공")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 패널 소개 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_static_debate(self) -> bool:
        """정적 토론 디버깅"""
        self.logger.info("=== 정적 토론 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            orchestrator.conduct_static_debate(self.test_topic, self.test_panel_agents)
            self.logger.info("✅ 정적 토론 성공")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 정적 토론 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_dynamic_debate(self) -> bool:
        """동적 토론 디버깅"""
        self.logger.info("=== 동적 토론 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            orchestrator.conduct_dynamic_debate(self.test_topic, self.test_panel_agents)
            self.logger.info("✅ 동적 토론 성공")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 동적 토론 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_provoke_round(self) -> bool:
        """논쟁 유도 라운드 디버깅"""
        self.logger.info("=== 논쟁 유도 라운드 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            
            # 테스트용 분석 결과
            analysis = {
                'next_action': 'provoke_debate',
                'main_issue': '경제적 효율성 vs 사회적 가치',
                'targeted_panels': ['김경제', '박사회']
            }
            
            result = orchestrator._conduct_provoke_round(1, self.test_topic, self.test_panel_agents, analysis)
            self.logger.info(f"✅ 논쟁 유도 라운드 성공: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 논쟁 유도 라운드 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_clash_round(self) -> bool:
        """직접 대결 라운드 디버깅"""
        self.logger.info("=== 직접 대결 라운드 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            
            # 테스트용 분석 결과
            analysis = {
                'next_action': 'focus_clash',
                'main_issue': '자유시장 vs 규제'
            }
            
            result = orchestrator._conduct_clash_round(1, self.test_topic, self.test_panel_agents, analysis)
            self.logger.info(f"✅ 직접 대결 라운드 성공: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 직접 대결 라운드 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_angle_change_round(self) -> bool:
        """새로운 관점 라운드 디버깅"""
        self.logger.info("=== 새로운 관점 라운드 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            
            # 테스트용 분석 결과
            analysis = {
                'next_action': 'change_angle',
                'missing_perspective': '국제적 관점'
            }
            
            result = orchestrator._conduct_angle_change_round(1, self.test_topic, self.test_panel_agents, analysis)
            self.logger.info(f"✅ 새로운 관점 라운드 성공: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 새로운 관점 라운드 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_evidence_round(self) -> bool:
        """근거 제시 라운드 디버깅"""
        self.logger.info("=== 근거 제시 라운드 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            
            # 테스트용 분석 결과
            analysis = {
                'next_action': 'pressure_evidence',
                'main_issue': 'AI 윤리 가이드라인의 효과성'
            }
            
            result = orchestrator._conduct_evidence_round(1, self.test_topic, self.test_panel_agents, analysis)
            self.logger.info(f"✅ 근거 제시 라운드 성공: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 근거 제시 라운드 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_normal_round(self) -> bool:
        """일반 라운드 디버깅"""
        self.logger.info("=== 일반 라운드 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            
            # 테스트용 분석 결과
            analysis = {
                'next_action': 'continue_normal',
                'temperature': 'normal',
                'main_issue': '일반적인 토론 진행'
            }
            
            result = orchestrator._conduct_normal_round(1, self.test_panel_agents, analysis)
            self.logger.info(f"✅ 일반 라운드 성공: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 일반 라운드 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_conclude_debate(self) -> bool:
        """토론 마무리 디버깅"""
        self.logger.info("=== 토론 마무리 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            orchestrator.conclude_debate(self.test_topic, self.test_panel_agents, "테스트 시스템 프롬프트")
            self.logger.info("✅ 토론 마무리 성공")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 토론 마무리 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def debug_full_debate_flow(self) -> bool:
        """전체 토론 흐름 디버깅"""
        self.logger.info("=== 전체 토론 흐름 디버깅 시작 ===")
        
        try:
            orchestrator = DebateOrchestrator(self.config, self.api_key)
            
            # 전체 토론 흐름 실행
            orchestrator.announce_debate_format(self.test_topic, 10, self.test_panel_agents)
            orchestrator.introduce_panels(self.test_panel_agents)
            orchestrator.conduct_debate(self.test_topic, self.test_panel_agents)
            orchestrator.conclude_debate(self.test_topic, self.test_panel_agents, "테스트 시스템 프롬프트")
            
            self.logger.info("✅ 전체 토론 흐름 성공")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 전체 토론 흐름 실패: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def run_comprehensive_debug(self) -> Dict[str, bool]:
        """종합 디버깅 실행"""
        self.logger.info("=== 종합 디버깅 시작 ===")
        
        results = {}
        
        # 각 단계별 디버깅 실행
        debug_methods = [
            ('초기화', self.debug_orchestrator_initialization),
            ('토론 방식 안내', self.debug_announce_debate_format),
            ('패널 소개', self.debug_introduce_panels),
            ('정적 토론', self.debug_static_debate),
            ('동적 토론', self.debug_dynamic_debate),
            ('논쟁 유도 라운드', self.debug_provoke_round),
            ('직접 대결 라운드', self.debug_clash_round),
            ('새로운 관점 라운드', self.debug_angle_change_round),
            ('근거 제시 라운드', self.debug_evidence_round),
            ('일반 라운드', self.debug_normal_round),
            ('토론 마무리', self.debug_conclude_debate),
            ('전체 흐름', self.debug_full_debate_flow)
        ]
        
        for name, method in debug_methods:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"{name} 디버깅 시작")
            self.logger.info(f"{'='*50}")
            
            try:
                result = method()
                results[name] = result
                
                if result:
                    self.logger.info(f"✅ {name} 디버깅 성공")
                else:
                    self.logger.error(f"❌ {name} 디버깅 실패")
                    
            except Exception as e:
                self.logger.error(f"❌ {name} 디버깅 중 예외 발생: {e}")
                results[name] = False
        
        # 결과 요약
        self.logger.info(f"\n{'='*50}")
        self.logger.info("디버깅 결과 요약")
        self.logger.info(f"{'='*50}")
        
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        for name, result in results.items():
            status = "✅ 성공" if result else "❌ 실패"
            self.logger.info(f"{name}: {status}")
        
        self.logger.info(f"\n전체 결과: {success_count}/{total_count} 성공")
        
        return results


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DebateOrchestrator 디버깅 도구')
    parser.add_argument('--config', type=str, help='설정 파일 경로')
    parser.add_argument('--api-key', type=str, help='OpenAI API 키')
    parser.add_argument('--test', type=str, choices=[
        'init', 'announce', 'introduce', 'static', 'dynamic', 
        'provoke', 'clash', 'angle', 'evidence', 'normal', 
        'conclude', 'full', 'all'
    ], default='all', help='실행할 테스트')
    
    args = parser.parse_args()
    
    # 디버거 생성
    debugger = DebateOrchestratorDebugger(args.config, args.api_key)
    
    # 테스트 실행
    if args.test == 'all':
        results = debugger.run_comprehensive_debug()
    else:
        # 개별 테스트 실행
        test_methods = {
            'init': debugger.debug_orchestrator_initialization,
            'announce': debugger.debug_announce_debate_format,
            'introduce': debugger.debug_introduce_panels,
            'static': debugger.debug_static_debate,
            'dynamic': debugger.debug_dynamic_debate,
            'provoke': debugger.debug_provoke_round,
            'clash': debugger.debug_clash_round,
            'angle': debugger.debug_angle_change_round,
            'evidence': debugger.debug_evidence_round,
            'normal': debugger.debug_normal_round,
            'conclude': debugger.debug_conclude_debate,
            'full': debugger.debug_full_debate_flow
        }
        
        method = test_methods.get(args.test)
        if method:
            result = method()
            print(f"테스트 결과: {'성공' if result else '실패'}")
        else:
            print(f"알 수 없는 테스트: {args.test}")


if __name__ == '__main__':
    main()
