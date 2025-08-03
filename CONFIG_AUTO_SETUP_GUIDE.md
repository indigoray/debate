# 🔧 설정 파일 자동 관리 시스템

## 📋 개요

Debate Agents는 이제 더욱 사용자 친화적인 설정 파일 관리 시스템을 제공합니다!

## ✨ 새로운 기능

### 🔄 자동 설정 파일 생성

**이전 방식:**
```bash
cp env_example.txt .env
# 수동으로 파일을 복사해야 했음
```

**새로운 방식:**
```bash
debate-agents
# 첫 실행 시 config.yaml이 자동으로 생성됨!
```

### 📁 파일 구조 변경

- ✅ `env_example.txt` → `config.yaml.example`
- ✅ 더 직관적인 파일명
- ✅ YAML 형식으로 통일

## 🚀 작동 방식

### 1️⃣ 개발 환경에서
```bash
# config.yaml이 있으면 바로 사용
python main.py
```

### 2️⃣ 설정 파일이 없을 때
```bash
# config.yaml.example을 config.yaml로 자동 복사
debate-agents
```

**실행 화면:**
```
config.yaml 파일이 없습니다. config.yaml.example을 복사합니다...
config.yaml 파일이 생성되었습니다. 필요에 따라 설정을 수정하세요.
```

### 3️⃣ 패키지 설치 환경에서
- 패키지에 포함된 `config.yaml.example`을 자동으로 찾아 복사
- 찾을 수 없으면 내장된 기본 설정 사용

## 🛠️ 구현 상세

### load_config() 함수 로직

1. **현재 디렉토리에 config.yaml 존재** → 바로 로드
2. **config.yaml.example 존재** → 복사 후 로드  
3. **패키지 설치 환경** → 패키지 내 example 파일 찾아 복사
4. **마지막 대안** → 내장 기본 설정 사용

### 자동 복사 경로 우선순위

```python
possible_paths = [
    'config.yaml.example',          # 현재 디렉토리
    '../config.yaml.example',       # 상위 디렉토리  
    '../../config.yaml.example'     # 2단계 상위
]
```

## 🎯 사용자 경험 개선

### Before ❌
1. 복잡한 설치 과정
2. 수동 파일 복사 필요
3. 실수로 설정 파일 누락 가능
4. env와 yaml 혼재로 혼란

### After ✅
1. 간단한 설치 과정
2. 완전 자동화된 설정
3. 실행만 하면 모든 것이 준비됨
4. 일관된 YAML 설정 파일

## 📦 패키지 배포에 미치는 영향

### MANIFEST.in 업데이트
```ini
include config.yaml.example  # 새로운 example 파일 포함
include config.yaml          # 기본 설정 파일도 포함
```

### pyproject.toml 호환성
- 모든 패키징 도구와 호환
- 설치 시 추가 스크립트 불필요
- 순수 Python 로직으로 구현

## 🔧 개발자 가이드

### 설정 파일 수정 시
1. `config.yaml.example` 수정
2. 개발 환경의 `config.yaml`도 동기화
3. 패키지 재빌드

### 새로운 설정 항목 추가 시
```yaml
# config.yaml.example에 추가
new_feature:
  enabled: true
  option: "default_value"
```

### 기본값 업데이트
`main.py`의 `default_config`도 함께 업데이트:
```python
default_config = {
    'new_feature': {
        'enabled': True,
        'option': 'default_value'
    }
}
```

## ⚠️ 주의사항

### 보안
- API 키는 여전히 수동 설정 필요
- `config.yaml`에 민감한 정보 입력 후 사용
- `.gitignore`에 `config.yaml` 포함 권장

### 파일 권한
- 자동 생성된 파일은 현재 사용자 권한
- 필요시 `chmod 600 config.yaml` 실행

### 버전 호환성
- Python 3.11+ 지원
- 이전 버전과의 하위 호환성 유지

## 🎉 결과

이제 사용자들은 다음과 같이 간단하게 시작할 수 있습니다:

```bash
pip install debate-agents
debate-agents
# 첫 실행 시 자동으로 설정 파일 생성!
# OpenAI API 키만 설정하면 바로 사용 가능!
```

**전보다 3단계나 줄어든 설치 과정으로 더 나은 사용자 경험을 제공합니다! 🚀**