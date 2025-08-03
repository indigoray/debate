#!/usr/bin/env python3
"""
PyPI 빌드 및 업로드 스크립트
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """명령어 실행"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 완료")
        if result.stdout:
            print(f"출력: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패")
        print(f"오류: {e.stderr}")
        return False

def clean_build():
    """빌드 폴더 정리"""
    folders_to_clean = ['build', 'dist', '*.egg-info']
    for folder in folders_to_clean:
        if '*' in folder:
            # glob 패턴인 경우
            import glob
            for path in glob.glob(folder):
                if os.path.exists(path):
                    shutil.rmtree(path)
                    print(f"🗑️ {path} 폴더 삭제")
        else:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"🗑️ {folder} 폴더 삭제")

def check_requirements():
    """필수 도구 확인"""
    required_tools = ['build', 'twine']
    for tool in required_tools:
        try:
            subprocess.run([sys.executable, '-m', tool, '--help'], 
                         capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print(f"❌ {tool}이 설치되지 않았습니다.")
            print(f"설치 명령: pip install {tool}")
            return False
    return True

def main():
    """메인 함수"""
    print("🚀 PyPI 패키지 빌드 및 업로드 스크립트")
    print("=" * 50)
    
    # 가상환경 확인
    if not hasattr(sys, 'real_prefix') and not (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        print("⚠️ 가상환경이 활성화되지 않은 것 같습니다.")
        response = input("계속하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            return
    
    # 필수 도구 확인
    if not check_requirements():
        print("\n필수 도구를 먼저 설치하세요:")
        print("pip install build twine")
        return
    
    # 빌드 폴더 정리
    print("\n🧹 이전 빌드 파일 정리...")
    clean_build()
    
    # 패키지 빌드
    if not run_command(f"{sys.executable} -m build", "패키지 빌드"):
        return
    
    # 빌드 결과 확인
    dist_files = list(Path("dist").glob("*"))
    if not dist_files:
        print("❌ 빌드된 파일이 없습니다.")
        return
    
    print(f"\n📦 빌드된 파일들:")
    for file in dist_files:
        print(f"  - {file}")
    
    # 업로드 선택
    print("\n📤 업로드 옵션:")
    print("1. TestPyPI (테스트용)")
    print("2. PyPI (실제 배포)")
    print("3. 로컬 설치 테스트만")
    
    choice = input("선택하세요 (1/2/3): ").strip()
    
    if choice == "1":
        # TestPyPI 업로드
        if run_command(f"{sys.executable} -m twine upload --repository testpypi dist/*", 
                      "TestPyPI 업로드"):
            print("\n✅ TestPyPI 업로드 완료!")
            print("테스트 설치: pip install --index-url https://test.pypi.org/simple/ debate-agents")
    
    elif choice == "2":
        # PyPI 업로드
        confirm = input("실제 PyPI에 업로드하시겠습니까? (y/N): ")
        if confirm.lower() == 'y':
            if run_command(f"{sys.executable} -m twine upload dist/*", "PyPI 업로드"):
                print("\n🎉 PyPI 업로드 완료!")
                print("설치 명령: pip install debate-agents")
    
    elif choice == "3":
        # 로컬 설치 테스트
        whl_files = list(Path("dist").glob("*.whl"))
        if whl_files:
            whl_file = whl_files[0]
            if run_command(f"pip install {whl_file}", "로컬 설치 테스트"):
                print("\n✅ 로컬 설치 테스트 완료!")
                print("테스트 명령: debate-agents")
    
    else:
        print("빌드만 완료되었습니다.")

if __name__ == "__main__":
    main()