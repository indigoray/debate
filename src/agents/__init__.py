"""
Agents 모듈 - AI 에이전트 클래스들
"""

# 테스트에서 autogen 등 외부 의존성으로 인한 임포트 실패를 피하기 위해
# 지연 임포트를 사용합니다.

def __getattr__(name):  # type: ignore
    if name == 'DebateManager':
        from .debate_manager import DebateManager
        return DebateManager
    if name == 'PanelAgent':
        from .panel_agent import PanelAgent
        return PanelAgent
    raise AttributeError(name)

__all__ = ['DebateManager', 'PanelAgent']