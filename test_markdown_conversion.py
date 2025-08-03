#!/usr/bin/env python3
"""마크다운 변환 테스트"""

from src.utils.output_capture import ConsoleCapture

# 테스트용 콘텐츠 (문제가 되는 부분 포함)
test_content = """🎭 **[토론 진행자] 이제 토론의 종합적인 결론을 말씀드리겠습니다.**

🎭 **[토론 진행자]**

지금까지 토론을 진행했습니다. 논의를 종합해 다음과 같이 결론을 내리겠습니다.
---
### 1. 주요 합의점
- **모두가 부동산 쏠림의 현상 자체와 그 파급효과에 대해 문제의식**을 공유했습니다.
- **부동산 시장의 구조적 문제와 제도적 환경이 개인 선택에 큰 영향을 미친다**는 점에 동의했습니다.
---
### 2. 주요 차이점과 핵심 쟁점
- **김서진 교수(경제학, 부동산경제연구소)**
- 부동산 쏠림이 국가적 성장잠재력 저하를 강조.
"""

# ConsoleCapture 인스턴스 생성
capture = ConsoleCapture()

# 변환 테스트
converted = capture._add_blank_lines_after_speeches(test_content)

print("=== 원본 ===")
print(test_content)
print("\n=== 변환 후 ===")
print(converted)
print("\n=== 변환 결과 확인 ===")
print("✅ '### 1. 주요 합의점'이 '**1. 주요 합의점**'으로 변환되었나?")
print("✅ '---'이 '・・・・・・'으로 변환되었나?")