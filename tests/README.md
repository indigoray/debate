# DebateOrchestrator 테스트 환경

이 디렉토리는 `debate_orchestrator`의 각 라운드별로 토론 진행이 원활한지 테스트하기 위한 종합적인 테스트 환경을 제공합니다.

## 📁 파일 구조

```
tests/
├── __init__.py                    # 테스트 패키지 초기화
├── test_debate_orchestrator.py    # 단위 테스트 스위트
├── test_round_specific.py         # 라운드별 상세 테스트
├── debug_orchestrator.py          # 디버깅 도구
└── README.md                      # 이 파일
```

## 🚀 빠른 시작

### 1. 가상환경 활성화
```bash
source venv/bin/activate
```

### 2. 모든 테스트 실행
```bash
python run_tests.py
```

### 3. 특정 테스트만 실행
```bash
# 단위 테스트만
python run_tests.py --test unit

# 라운드별 테스트만
python run_tests.py --test round

# 디버깅 테스트만
python run_tests.py --test debug

# 특정 디버깅 테스트
python run_tests.py --test specific --debug-test dynamic
```

## 📋 테스트 종류

### 1. 단위 테스트 (`test_debate_orchestrator.py`)
- **목적**: 각 메서드의 기본 동작 검증
- **내용**: 
  - 오케스트레이터 초기화
  - 토론 방식 안내
  - 패널 소개
  - 정적/동적 토론 진행
  - 각 라운드별 메서드
  - 토론 마무리
  - 오류 처리

### 2. 라운드별 상세 테스트 (`test_round_specific.py`)
- **목적**: 각 라운드의 구체적인 시나리오 테스트
- **내용**:
  - 논쟁 유도 라운드 시나리오
  - 직접 대결 라운드 시나리오
  - 새로운 관점 라운드 시나리오
  - 근거 제시 라운드 시나리오
  - 일반 라운드 시나리오
  - 동적 토론 흐름

### 3. 디버깅 도구 (`debug_orchestrator.py`)
- **목적**: 실제 오류 진단 및 수정
- **내용**:
  - 각 단계별 실제 실행 테스트
  - 상세한 오류 로깅
  - 설정 파일 검증
  - API 연결 테스트

## 🔧 사용법

### 단위 테스트 실행
```bash
# 모든 단위 테스트
python -m unittest tests.test_debate_orchestrator -v

# 특정 테스트 클래스
python -m unittest tests.test_debate_orchestrator.TestDebateOrchestrator -v

# 특정 테스트 메서드
python -m unittest tests.test_debate_orchestrator.TestDebateOrchestrator.test_provoke_round -v
```

### 라운드별 테스트 실행
```bash
python tests/test_round_specific.py
```

### 디버깅 도구 사용
```bash
# 모든 디버깅 테스트
python tests/debug_orchestrator.py

# 특정 디버깅 테스트
python tests/debug_orchestrator.py --test dynamic
python tests/debug_orchestrator.py --test provoke
python tests/debug_orchestrator.py --test clash

# 설정 파일 지정
python tests/debug_orchestrator.py --config config.yaml

# API 키 지정
python tests/debug_orchestrator.py --api-key your_api_key
```

## 📊 테스트 결과 확인

### 로그 파일
- `test_debate_orchestrator.log`: 단위 테스트 로그
- `round_specific_test.log`: 라운드별 테스트 로그
- `debug_orchestrator.log`: 디버깅 테스트 로그

### 콘솔 출력
테스트 실행 시 실시간으로 진행 상황과 결과가 콘솔에 출력됩니다.

## 🐛 오류 진단

### 1. 일반적인 오류
- **ImportError**: 의존성 패키지 누락
- **AttributeError**: 메서드나 속성 접근 오류
- **TypeError**: 타입 불일치
- **KeyError**: 딕셔너리 키 오류

### 2. 오류 해결 방법
1. **가상환경 확인**: `source venv/bin/activate`
2. **의존성 설치**: `pip install -r requirements.txt`
3. **설정 파일 확인**: `config.yaml` 파일 존재 및 형식 확인
4. **API 키 설정**: OpenAI API 키가 올바르게 설정되었는지 확인
5. **로그 확인**: 해당 로그 파일에서 상세한 오류 정보 확인

### 3. 디버깅 팁
- `--show_debug_info: true` 설정으로 상세한 디버그 정보 출력
- 특정 라운드에서 오류가 발생하면 해당 라운드만 테스트
- Mock 객체를 사용하여 외부 의존성 격리

## 🔄 테스트 시나리오

### 논쟁 유도 라운드 테스트
1. **2명 패널 간 논쟁**: 특정 패널 2명이 서로 논쟁
2. **개별 패널 지목**: 한 명의 패널만 지목하여 응답
3. **잘못된 분석 결과**: 오류 처리 검증

### 직접 대결 라운드 테스트
1. **정상적인 1:1 대결**: 2명의 패널이 직접 대결
2. **패널 부족**: 2명 미만일 때의 처리

### 새로운 관점 라운드 테스트
1. **국제적 관점**: 새로운 관점 제시
2. **미래 세대 관점**: 다른 새로운 관점

### 근거 제시 라운드 테스트
1. **개별 근거 제시**: 한 명의 패널이 근거 제시
2. **순차 근거 제시**: 여러 패널이 순서대로 근거 제시
3. **근거 논쟁**: 패널 간 근거 논쟁

## 📝 테스트 추가 방법

### 새로운 단위 테스트 추가
```python
def test_new_feature(self):
    """새로운 기능 테스트"""
    # 테스트 코드 작성
    self.assertTrue(result)
```

### 새로운 라운드 테스트 추가
```python
def test_new_round_scenario(self):
    """새로운 라운드 시나리오 테스트"""
    # 시나리오 설정
    # 테스트 실행
    # 결과 검증
```

### 새로운 디버깅 테스트 추가
```python
def debug_new_feature(self) -> bool:
    """새로운 기능 디버깅"""
    try:
        # 디버깅 코드
        return True
    except Exception as e:
        self.logger.error(f"오류: {e}")
        return False
```

## 🎯 테스트 목표

1. **기능 검증**: 각 라운드가 의도한 대로 동작하는지 확인
2. **오류 처리**: 예외 상황에서 적절히 처리되는지 확인
3. **성능 검증**: 토론 진행이 원활한지 확인
4. **통합 검증**: 전체 토론 흐름이 정상적으로 작동하는지 확인

## 📞 지원

테스트 실행 중 문제가 발생하면:
1. 로그 파일 확인
2. 가상환경 및 의존성 상태 확인
3. 설정 파일 검증
4. 필요시 추가 디버깅 정보 수집
