# PyPI 배포 가이드

## 🎯 개요

이 가이드는 Debate Agents 앱을 PyPI에 배포하는 전체 과정을 설명합니다.

## 📋 사전 준비

### 1. PyPI 계정 생성

1. **PyPI 계정 생성**: https://pypi.org/account/register/
2. **TestPyPI 계정 생성**: https://test.pypi.org/account/register/
   - 실제 배포 전 테스트용

### 2. API 토큰 생성

#### PyPI API 토큰
1. PyPI 로그인 → Account settings → API tokens
2. "Add API token" 클릭
3. Token name: `debate-agents` (또는 원하는 이름)
4. Scope: "Entire account" 또는 특정 프로젝트
5. 생성된 토큰 복사 (한 번만 표시됨!)

#### TestPyPI API 토큰
1. TestPyPI에서도 동일한 과정 반복

### 3. 필수 도구 설치

```bash
# 가상환경 활성화
source venv/bin/activate

# 빌드 및 업로드 도구 설치
pip install build twine
```

### 4. 인증 설정

#### 방법 1: .pypirc 파일 (추천)
```bash
# 홈 디렉토리에 .pypirc 파일 생성
nano ~/.pypirc
```

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-actual-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-actual-testpypi-token-here
```

#### 방법 2: 환경변수
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
```

## 🚀 배포 과정

### 1. 프로젝트 정보 업데이트

`pyproject.toml` 파일에서 다음 정보를 수정하세요:

```toml
[project]
name = "debate-agents"  # 고유한 이름 확인 필요
version = "1.0.0"       # 버전 업데이트
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

[project.urls]
Homepage = "https://github.com/your-username/debate-agents"
Repository = "https://github.com/your-username/debate-agents.git"
```

### 2. 자동 빌드 및 업로드

```bash
# 빌드 및 업로드 스크립트 실행
python build_and_upload.py
```

스크립트가 다음을 수행합니다:
1. 이전 빌드 파일 정리
2. 패키지 빌드
3. 업로드 옵션 선택

### 3. 수동 빌드 및 업로드

#### 빌드
```bash
# 이전 빌드 정리
rm -rf build/ dist/ *.egg-info/

# 패키지 빌드
python -m build
```

#### TestPyPI 업로드 (테스트)
```bash
python -m twine upload --repository testpypi dist/*
```

#### 실제 PyPI 업로드
```bash
python -m twine upload dist/*
```

## 🧪 테스트

### TestPyPI에서 설치 테스트
```bash
pip install --index-url https://test.pypi.org/simple/ debate-agents
```

### 실제 PyPI에서 설치
```bash
pip install debate-agents
```

### 설치 후 테스트
```bash
# CLI 명령어 테스트
debate-agents

# 또는 Python 모듈로 실행
python -m src.main
```

## 🔄 버전 업데이트

새 버전 배포 시:

1. `pyproject.toml`에서 버전 번호 업데이트
2. 변경사항을 README.md에 추가
3. 빌드 및 업로드 재실행

```bash
# 버전 예시
version = "1.0.1"  # 버그 수정
version = "1.1.0"  # 새 기능 추가
version = "2.0.0"  # 호환성 깨지는 변경
```

## ⚠️ 주의사항

### 패키지 이름
- PyPI에서 패키지 이름은 고유해야 함
- 이미 존재하는 이름인지 확인: https://pypi.org/project/YOUR-PACKAGE-NAME/
- 필요시 `debate-agents-yourname` 같은 형태로 변경

### 버전 관리
- 한 번 업로드된 버전은 다시 업로드할 수 없음
- 실수 시 버전 번호를 올려서 재업로드

### API 키 보안
- API 키를 코드에 포함하지 말 것
- `.pypirc` 파일 권한 설정: `chmod 600 ~/.pypirc`

## 🔧 문제 해결

### 일반적인 오류

#### "File already exists"
```bash
# 해결: 버전 번호 증가
version = "1.0.1"
```

#### "Invalid or non-existent authentication"
```bash
# 해결: API 토큰 재확인
python -m twine check dist/*
```

#### "Package name already taken"
```bash
# 해결: 다른 이름 사용
name = "debate-agents-yourname"
```

### 빌드 오류
```bash
# 의존성 확인
pip install --upgrade build twine setuptools wheel

# 구문 오류 확인
python -m py_compile src/main.py
```

## 🎉 성공적인 배포 후

1. **GitHub 릴리스 생성**: 코드와 함께 릴리스 노트 작성
2. **문서 업데이트**: README.md에 설치 방법 추가
3. **소셜 공유**: 개발 커뮤니티에 프로젝트 소개

## 📚 추가 자료

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)