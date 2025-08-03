# 🚀 Debate Agents - PyPI 배포 최종 가이드

## ✅ 완료된 작업들

### 📦 패키지 구성
- [x] `pyproject.toml` - 패키지 설정 및 메타데이터
- [x] `LICENSE` - MIT 라이선스
- [x] `MANIFEST.in` - 추가 파일 포함 설정
- [x] `main.py` 수정 - 패키지 설치 환경 대응
- [x] CLI 진입점 설정 (`debate-agents` 명령어)

### 🛠️ 빌드 도구
- [x] `build_and_upload.py` - 자동 빌드 및 업로드 스크립트
- [x] `build`, `twine` 패키지 설치 완료
- [x] 로컬 패키지 빌드 및 설치 테스트 성공

## 🎯 다음 단계: PyPI 업로드

### 1️⃣ 개인 정보 설정

먼저 `pyproject.toml` 파일에서 개인 정보를 수정하세요:

```toml
[project]
name = "debate-agents"  # ⚠️ 중복 확인 필요!
authors = [
    {name = "실제 이름", email = "실제@이메일.com"}
]
maintainers = [
    {name = "실제 이름", email = "실제@이메일.com"}
]

[project.urls]
Homepage = "https://github.com/실제사용자명/debate-agents"
Repository = "https://github.com/실제사용자명/debate-agents.git"
"Bug Reports" = "https://github.com/실제사용자명/debate-agents/issues"
```

### 2️⃣ PyPI 계정 생성

1. **PyPI**: https://pypi.org/account/register/
2. **TestPyPI**: https://test.pypi.org/account/register/

### 3️⃣ API 토큰 생성

#### PyPI 토큰
1. PyPI 로그인 → Account settings → API tokens
2. "Add API token" 클릭
3. Token name: `debate-agents`
4. Scope: "Entire account"

#### TestPyPI 토큰
1. TestPyPI에서 동일한 과정 반복

### 4️⃣ 인증 설정

`~/.pypirc` 파일 생성:

```bash
nano ~/.pypirc
```

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-여기에실제토큰입력

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-여기에TestPyPI토큰입력
```

보안 설정:
```bash
chmod 600 ~/.pypirc
```

### 5️⃣ 패키지명 중복 확인

```bash
# 패키지명이 이미 존재하는지 확인
curl -s https://pypi.org/pypi/debate-agents/json > /dev/null && echo "이미 존재함" || echo "사용 가능"
```

만약 이미 존재한다면 `pyproject.toml`에서 이름 변경:
```toml
name = "debate-agents-yourname"  # 고유한 이름으로 변경
```

### 6️⃣ 자동 배포

```bash
# 자동 빌드 및 업로드 스크립트 실행
python build_and_upload.py
```

스크립트 옵션:
1. **TestPyPI (추천)**: 먼저 테스트용으로 업로드
2. **PyPI**: 실제 배포
3. **로컬 테스트**: 설치 테스트만

### 7️⃣ 수동 배포 (선택사항)

```bash
# 1. 빌드 폴더 정리
rm -rf build/ dist/ *.egg-info/

# 2. 패키지 빌드
python -m build

# 3. TestPyPI 업로드 (테스트)
python -m twine upload --repository testpypi dist/*

# 4. 실제 PyPI 업로드
python -m twine upload dist/*
```

## 🧪 설치 테스트

### TestPyPI에서 설치
```bash
pip install --index-url https://test.pypi.org/simple/ debate-agents
```

### 실제 PyPI에서 설치
```bash
pip install debate-agents
```

### 사용법 테스트
```bash
# CLI 명령어로 실행 (첫 실행 시 config.yaml 자동 생성)
debate-agents

# config.yaml 파일에서 OpenAI API 키 설정 후 재실행
# ai:
#   api_key: your_actual_api_key_here

# 또는 Python 모듈로 실행
python -m src.main
```

## ⚠️ 주의사항

### 패키지명
- PyPI에서 패키지명은 전역적으로 고유해야 함
- 이미 존재하는 이름은 사용 불가
- 필요시 `debate-agents-yourname` 형태로 변경

### 버전 관리
- 업로드된 버전은 삭제/수정 불가
- 실수 시 버전 번호를 올려서 재업로드
- [Semantic Versioning](https://semver.org/) 권장

### API 키 보안
- API 키를 코드에 절대 포함하지 말 것
- `.pypirc` 파일 권한을 600으로 설정
- 키가 노출되면 즉시 재생성

## 🎉 배포 완료 후

1. **GitHub 릴리스**: 코드와 함께 릴리스 노트 작성
2. **README 업데이트**: PyPI 설치 방법 추가
3. **문서화**: 사용 예제 및 API 문서 작성
4. **커뮤니티 공유**: 개발자 커뮤니티에 프로젝트 소개

## 🔧 문제 해결

### "File already exists" 오류
```bash
# 해결: 버전 번호 증가
version = "1.0.1"
```

### "Invalid authentication" 오류
```bash
# 해결: API 토큰 재확인 및 .pypirc 권한 설정
chmod 600 ~/.pypirc
```

### "Package name taken" 오류
```bash
# 해결: 다른 이름 사용
name = "debate-agents-yourname"
```

## 📞 지원

- **PyPI 도움말**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **이슈 트래킹**: GitHub Issues 사용

---

**축하합니다! 🎊 이제 전세계 Python 개발자들이 `pip install debate-agents`로 여러분의 앱을 설치할 수 있습니다!**