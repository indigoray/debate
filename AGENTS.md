# Repository Guidelines

## Project Language
- Code (identifiers, commit messages): English.
- Comments, docs, issues/PRs: Korean.
- Agent outputs: 모든 에이전트의 답변과 보고서는 한국어로 작성합니다.
## Project Structure & Module Organization
- `main.py`: CLI entry for running the debate simulation.
- `src/agents/`: Core orchestration and agent logic (`debate_manager.py`, `debate_orchestrator.py`, `panel_*.py`, `response_generator.py`).
- `src/utils/`: Helpers for logging, streaming, and output capture.
- `tests/`: Unit/integration tests and debug runners (`test_*.py`, `debug_orchestrator.py`).
- `config.yaml.example`: Template; copy to `config.yaml` (gitignored) and set `ai.api_key`.
- `run_tests.py`: Unified test runner; `build_and_upload.py`: packaging helper.

## Build, Test, and Development Commands
- Setup: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Optional dev tools: `pip install -e .[dev]`
- Run app: `python main.py`
- Run all tests: `python run_tests.py --test all`
- Unit tests only: `python -m unittest tests.test_debate_orchestrator -v`
- Debug a phase: `python run_tests.py --test debug --debug-test full`
- Build package: `python build_and_upload.py` (guided) or `python -m build`

## Coding Style & Naming Conventions
- Python 3.11+, 4-space indent, type hints encouraged.
- Formatter: Black (line length 88). Lint: Flake8. Types: mypy (target py311).
- Run locally: `black . && flake8 . && mypy src`
- Naming: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants. Tests in `tests/test_*.py`.

## Testing Guidelines
- Framework: `unittest`. Place new tests under `tests/` named `test_*.py`.
- Run one file: `python -m unittest tests.basic_unit_test`
- Prefer deterministic tests with clear arrange/act/assert blocks. Include edge cases and failure paths.
- Use `run_tests.py` locally before PRs to exercise unit, round-specific, and debug flows.

## Commit & Pull Request Guidelines
- Commits: short, imperative summaries (Korean/English). Example: `토론 라운드 진행 수정`, `refactor: split debate orchestrator`.
- Reference issues with `#123` when relevant. Keep commits scoped and atomic.
- PRs: clear description, rationale, test plan/outputs (logs or screenshots), and linked issues. Keep changes focused; include config or data updates if required.

## Security & Configuration Tips
- Never commit secrets. `config.yaml` is gitignored; copy from `config.yaml.example` and set `ai.api_key`.
- Keep logs free of sensitive data. Use `.env` or local config for machine-specific settings.

## Cursor Rules (MDC 참고)
- Cursor 기반 워크플로우를 따릅니다. 필요 시 `.cursor/rules/*.mdc`를 우선 참고하세요.
- 주요 규칙 파일: `app.mdc`, `todo.mdc`, `debate_orchestrator_todo.mdc`, `debate_test_environment.mdc`, `dynamic_debate.mdc`.
- 에이전트/오케스트레이터/테스트 변경 시 관련 MDC를 먼저 읽고, 규칙과 충돌할 경우 MDC 내용을 우선합니다.
 - `app.mdc`: 앱 개요·아키텍처·에이전트 역할 정의, 실행/원칙 정리.
 - `todo.mdc`: project todo list Streamlit UI, 다국어 지원, AutoGen 활용/제거 로드맵.
 - `debate_test_environment.mdc`: 테스트 구조/종류/실행법과 커버리지 가이드.
 - `dynamic_debate.mdc`: dynamic debate를 위한 동적 라운드 5종, 상태분석, 쿨다운·조기종료·연장 규칙.
 - `debate_orchestrator_todo.mdc`: debate_orchestrator의 Todo list, 버그 우선순위, 전략/상태 분리, 검증/폴백, 리팩토링 체크리스트.
