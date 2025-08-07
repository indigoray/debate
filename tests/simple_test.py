#!/usr/bin/env python3
"""
간단한 테스트 - 기본 import와 초기화만 테스트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_import():
    """기본 import 테스트"""
    print("🔍 Import 테스트 시작...")
    
    try:
        # 기본 모듈 import 테스트
        from src.agents import debate_orchestrator
        print("✅ debate_orchestrator 모듈 import 성공")
        
        from src.agents.debate_orchestrator import DebateOrchestrator
        print("✅ DebateOrchestrator 클래스 import 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ Import 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_initialization():
    """기본 초기화 테스트"""
    print("\n🔍 기본 초기화 테스트 시작...")
    
    try:
        from src.agents.debate_orchestrator import DebateOrchestrator
        
        # 테스트용 설정
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
        
        api_key = "test_api_key"
        
        # 오케스트레이터 생성
        orchestrator = DebateOrchestrator(config, api_key)
        print("✅ DebateOrchestrator 초기화 성공")
        
        # 기본 속성 확인
        print(f"   - debate_rounds: {orchestrator.debate_rounds}")
        print(f"   - config 로드: {bool(orchestrator.config)}")
        print(f"   - api_key 설정: {bool(orchestrator.api_key)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 간단한 테스트 시작")
    print("=" * 50)
    
    # Import 테스트
    import_success = test_import()
    
    # 초기화 테스트
    init_success = test_basic_initialization()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    if import_success:
        print("✅ Import 테스트: 성공")
    else:
        print("❌ Import 테스트: 실패")
    
    if init_success:
        print("✅ 초기화 테스트: 성공")
    else:
        print("❌ 초기화 테스트: 실패")
    
    if import_success and init_success:
        print("\n🎉 모든 기본 테스트가 성공했습니다!")
        return 0
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
