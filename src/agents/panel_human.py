"""
Panel Human - 인간 참여자 패널 클래스
"""

from typing import Optional, List
from colorama import Fore, Style

from .panel import Panel


class PanelHuman(Panel):
    """인간 참여자를 나타내는 패널 클래스"""
    
    def __init__(self, name: str, expertise: str = "시민 참여자"):
        # 부모 클래스 초기화
        super().__init__(
            name=name,
            expertise=expertise,
            background=f"{expertise}로서 실제 경험과 현실적 관점을 보유",
            perspective=f"{expertise}의 관점에서 실용적이고 균형잡힌 시각을 제시",
            debate_style="진솔하고 솔직한 표현으로 실제 경험을 바탕으로 한 의견 제시"
        )
    
    @property
    def is_human(self) -> bool:
        """인간 패널임을 나타냄"""
        return True
    
    def respond_to_topic(self, topic: str) -> str:
        """주제에 대한 초기 의견 제시"""
        print(f"\n{Fore.CYAN}💭 {self.name}님, 이 주제에 대한 당신의 의견을 들려주세요:{Style.RESET_ALL}")
        print(f"주제: {topic}")
        response = input(f"\n{Fore.GREEN}의견 입력: {Style.RESET_ALL}")
        return f"[{self.name}] {response}"
    
    def respond_to_debate(self, context: str, statements: list) -> str:
        """토론 중 의견 제시"""
        print(f"\n{Fore.CYAN}💭 {self.name}님, 다른 패널들의 의견을 듣고 당신의 추가 의견이나 반박을 말씀해주세요:{Style.RESET_ALL}")
        print(f"현재 상황: {context}")
        response = input(f"\n{Fore.GREEN}의견 입력: {Style.RESET_ALL}")
        return f"[{self.name}] {response}"
    
    def final_statement(self, topic: str, debate_summary: Optional[str] = None, other_panels_statements: Optional[List] = None) -> str:
        """최종 의견 제시"""
        print(f"\n{Fore.CYAN}💭 {self.name}님, 토론을 마무리하며 최종 의견을 말씀해주세요:{Style.RESET_ALL}")
        
        if debate_summary:
            print(f"토론 요약: {debate_summary[:200]}...")  # 요약의 일부만 표시
            
        # 다른 패널들의 주요 주장 표시
        if other_panels_statements:
            print(f"\n{Fore.YELLOW}📋 다른 패널들의 주요 주장들:{Style.RESET_ALL}")
            for stmt in other_panels_statements:
                print(f"• [{stmt['agent_name']}]: {stmt['content'][:150]}{'...' if len(stmt['content']) > 150 else ''}")
            
            print(f"\n{Fore.CYAN}위 주장들 중에서 공감하거나 반박하고 싶은 부분이 있다면 언급해주시고, 최종 의견을 말씀해주세요.{Style.RESET_ALL}")
        
        response = input(f"\n{Fore.GREEN}최종 의견 입력: {Style.RESET_ALL}")
        return f"[{self.name}] {response}"
    
    def introduce(self) -> str:
        """자기소개"""
        print(f"\n{Fore.CYAN}💭 {self.name}님, 다른 패널들과 청중에게 간단히 자기소개를 해주세요:{Style.RESET_ALL}")
        response = input(f"\n{Fore.GREEN}자기소개: {Style.RESET_ALL}")
        return f"[{self.name}] {response}"