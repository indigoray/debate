# Debate Agents - AI 패널 토론 시뮬레이션

AI 기반의 콘솔 애플리케이션으로, 사용자가 입력한 토론 주제를 바탕으로 가상의 전문가 패널들이 진행하는 토론을 시뮬레이션합니다.

## 🎯 주요 기능

- **동적 전문가 생성**: 토론 주제에 맞는 4명의 전문가 AI 에이전트 자동 생성
- **다양한 관점**: 각 전문가는 서로 다른 배경과 전문성을 보유
- **실시간 토론**: 패널토론 방식으로 진행되는 상호 토론
- **균형잡힌 결론**: 토론 종료 시 종합적인 분석과 결론 제시

## 🏗️ 시스템 아키텍처

### 에이전트 구성
- **Debate Manager Agent (1명)**: 토론 진행 및 주재, 전문가 페르소나 생성
- **Panel Agents (4명)**: 각각 다른 전문 분야의 전문가

### 토론 진행 방식
1. **초기화**: 주제 분석 → 전문가 생성 → 규칙 안내
2. **토론 진행**: 패널 소개 → 초기 의견 → 상호 토론 → 반박
3. **결론**: 최종 의견 → 종합 분석 → 결론 제시

## 🛠️ 기술 스택

- **언어**: Python 3.11+
- **AI Framework**: AutoGen (Multi-Agent Framework)
- **AI 모델**: OpenAI GPT-4 Turbo
- **의존성 관리**: pip + requirements.txt

## 📦 설치 및 실행

### 1. 저장소 클론 및 이동
```bash
git clone <repository-url>
cd debate
```

### 2. 가상환경 설정
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# env_example.txt를 .env로 복사
cp env_example.txt .env

# .env 파일을 편집하여 OpenAI API 키 설정
# OPENAI_API_KEY=your_actual_api_key_here
```

### 5. 애플리케이션 실행
```bash
python main.py
```

## ⚙️ 설정

`config.yaml` 파일에서 다음 설정을 변경할 수 있습니다:

```yaml
debate:
  duration_minutes: 10        # 토론 진행 시간
  max_turns_per_agent: 3      # 에이전트당 최대 발언 횟수
  panel_size: 4               # 패널 수

ai:
  model: "gpt-4-turbo-preview"  # 사용할 AI 모델
  temperature: 0.7              # 창의성 수준
  max_tokens: 1500              # 최대 토큰 수
```

## 📁 프로젝트 구조

```
debate/
├── main.py                 # 애플리케이션 진입점
├── config.yaml             # 설정 파일
├── requirements.txt        # Python 의존성
├── .env                    # 환경변수 (생성 필요)
├── src/
│   ├── agents/
│   │   ├── debate_manager.py    # 토론 관리자
│   │   └── panel_agent.py       # 패널 전문가
│   └── utils/
│       └── logger.py            # 로깅 유틸리티
├── tests/                  # 테스트 코드 (예정)
└── venv/                   # 가상환경
```

## 🎮 사용 방법

1. 애플리케이션을 실행하면 토론 주제 입력을 요청합니다.
2. 주제를 입력하면 AI가 해당 주제에 적합한 4명의 전문가를 생성합니다.
3. 각 전문가가 자기소개를 하고 토론이 시작됩니다.
4. 패널토론 방식으로 토론이 진행됩니다.
5. 토론 종료 시 종합 분석과 결론이 제시됩니다.

## 🔧 요구사항

- Python 3.11+
- OpenAI API 키
- 인터넷 연결

## 📄 라이선스

MIT License

## 👥 기여

이슈 및 풀 리퀘스트를 환영합니다!