"""
Panel - 토론 패널 추상 베이스 클래스
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class Panel(ABC):
    """토론 패널 추상 베이스 클래스"""
    
    def __init__(self, name: str, expertise: str, background: str, 
                 perspective: str, debate_style: str):
        """
        Panel 초기화
        
        Args:
            name: 패널 이름
            expertise: 직업과 소속
            background: 배경
            perspective: 핵심 관점
            debate_style: 토론 스타일
        """
        self.name = name
        self.expertise = expertise
        self.background = background
        self.perspective = perspective
        self.debate_style = debate_style
    
    @property
    @abstractmethod
    def is_human(self) -> bool:
        """패널이 인간인지 AI인지 구분"""
        pass
    
    @abstractmethod
    def introduce(self) -> str:
        """자기소개"""
        pass
    
    @abstractmethod
    def respond_to_topic(self, topic: str) -> str:
        """주제에 대한 초기 의견 제시"""
        pass
    
    @abstractmethod
    def respond_to_debate(self, context: str, previous_statements: List[str]) -> str:
        """토론 중 의견 제시"""
        pass
    
    @abstractmethod
    def final_statement(self, topic: str, debate_summary: Optional[str] = None) -> str:
        """최종 의견 제시"""
        pass
    
    def get_panel_info(self) -> dict:
        """패널 정보 반환"""
        return {
            'name': self.name,
            'expertise': self.expertise,
            'background': self.background,
            'perspective': self.perspective,
            'debate_style': self.debate_style,
            'is_human': self.is_human
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.name} ({self.expertise})"
    
    def __repr__(self) -> str:
        """객체 표현"""
        human_type = "Human" if self.is_human else "AI"
        return f"<{human_type}Panel: {self.name}>"