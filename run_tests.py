#!/usr/bin/env python3
"""
DebateOrchestrator 테스트 실행 스크립트
모든 테스트를 실행하고 결과를 요약하는 메인 스크립트
"""

import sys
import os
import subprocess
import argparse
import time
from typing import List, Dict, Any

def run_command(command: List[str], description: str, stream: bool = False) -> bool:
    """명령어 실행 및 결과 반환

    Args:
        command: 실행할 커맨드 배열
        description: 설명 출력용 텍스트
        stream: True면 하위 프로세스 stdout/stderr를 실시간 스트리밍
    """
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"실행 명령어: {' '.join(command)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        if stream:
            # 실시간 스트리밍 모드: 출력 캡처하지 않고 바로 화면에 표시
            result = subprocess.run(
                command,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"실행 시간: {duration:.2f}초")
        print(f"반환 코드: {result.returncode}")
        
        if not stream:
            if result.stdout:
                print("\n📤 표준 출력:")
                print(result.stdout)
            if result.stderr:
                print("\n⚠️  표준 오류:")
                print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} 성공")
            return True
        else:
            print(f"❌ {description} 실패 (반환 코드: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} 실행 중 오류 발생: {e}")
        return False

def run_unit_tests() -> bool:
    """단위 테스트 실행"""
    # 단위 테스트는 케이스별 진행상황을 실시간으로 보기 위해 스트리밍 모드로 실행
    # 사용자 참여 시나리오 제외: add_user_as_panelist 관련 테스트 제외
    return run_command(
        [sys.executable, "-m", "unittest", "tests.test_debate_orchestrator", "-v"],
        "단위 테스트 실행",
        stream=True
    )

def run_round_specific_tests() -> bool:
    """라운드별 상세 테스트 실행"""
    return run_command(
        [sys.executable, "tests/test_round_specific.py"],
        "라운드별 상세 테스트 실행"
    )

def run_debug_tests(test_type: str = "all") -> bool:
    """디버깅 테스트 실행"""
    return run_command(
        [sys.executable, "tests/debug_orchestrator.py", "--test", test_type],
        f"디버깅 테스트 실행 ({test_type})"
    )

def run_specific_debug_test(test_name: str) -> bool:
    """특정 디버깅 테스트 실행"""
    return run_debug_tests(test_name)

def check_venv() -> bool:
    """가상환경 활성화 확인"""
    print("\n🔍 가상환경 상태 확인")
    
    # 가상환경 확인
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 가상환경이 활성화되어 있습니다.")
        print(f"   가상환경 경로: {sys.prefix}")
        return True
    else:
        print("⚠️  가상환경이 활성화되어 있지 않습니다.")
        print("   가상환경을 활성화하는 것을 권장합니다:")
        print("   source venv/bin/activate")
        return False

def check_dependencies() -> bool:
    """의존성 확인"""
    print("\n🔍 의존성 확인")
    
    required_packages = [
        'yaml', 'unittest', 'logging', 'typing'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  누락된 패키지: {', '.join(missing_packages)}")
        print("   다음 명령어로 설치하세요:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")
        return True

def run_all_tests() -> Dict[str, bool]:
    """모든 테스트 실행"""
    print("🎯 DebateOrchestrator 종합 테스트 시작")
    print(f"Python 버전: {sys.version}")
    print(f"작업 디렉토리: {os.getcwd()}")
    
    # 환경 확인
    venv_ok = check_venv()
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ 의존성 문제로 테스트를 중단합니다.")
        return {"환경 확인": False}
    
    # 테스트 실행
    results = {}
    
    # 단위 테스트
    results["단위 테스트"] = run_unit_tests()
    
    # 라운드별 상세 테스트
    results["라운드별 테스트"] = run_round_specific_tests()
    
    # 디버깅 테스트
    results["디버깅 테스트"] = run_debug_tests()
    
    return results

def print_summary(results: Dict[str, bool]):
    """테스트 결과 요약 출력"""
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print(f"{'='*60}")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
    
    print(f"\n전체 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 로그를 확인해주세요.")
    
    print(f"{'='*60}")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='DebateOrchestrator 테스트 실행기')
    parser.add_argument('--test', type=str, choices=[
        'unit', 'round', 'debug', 'all', 'specific'
    ], default='all', help='실행할 테스트 유형')
    parser.add_argument('--debug-test', type=str, choices=[
        'init', 'announce', 'introduce', 'static', 'dynamic', 
        'provoke', 'clash', 'angle', 'evidence', 'normal', 
        'conclude', 'full'
    ], help='실행할 특정 디버깅 테스트')
    
    args = parser.parse_args()
    
    if args.test == 'specific' and not args.debug_test:
        print("❌ --specific 옵션을 사용할 때는 --debug-test도 지정해야 합니다.")
        return 1
    
    try:
        if args.test == 'all':
            results = run_all_tests()
            print_summary(results)
            
        elif args.test == 'unit':
            success = run_unit_tests()
            print_summary({"단위 테스트": success})
            
        elif args.test == 'round':
            success = run_round_specific_tests()
            print_summary({"라운드별 테스트": success})
            
        elif args.test == 'debug':
            if args.debug_test:
                success = run_specific_debug_test(args.debug_test)
                print_summary({f"디버깅 테스트 ({args.debug_test})": success})
            else:
                success = run_debug_tests()
                print_summary({"디버깅 테스트": success})
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 테스트가 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
