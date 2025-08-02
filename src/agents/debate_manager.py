"""
Debate Manager - 토론 진행 및 관리 에이전트
"""

import time
import logging
from typing import Dict, Any, List
from colorama import Fore, Style
from autogen import ConversableAgent

from .panel_agent import PanelAgent


class DebateManager:
    """토론 진행 및 관리 에이전트"""
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        Debate Manager 초기화
        
        Args:
            config: 설정 딕셔너리
            api_key: OpenAI API 키
        """
        self.config = config
        self.api_key = api_key
        self.logger = logging.getLogger('debate_agents.manager')
        
        # 토론 설정
        self.duration_minutes = config['debate']['duration_minutes']
        self.max_turns = config['debate']['max_turns_per_agent']
        self.panel_size = config['debate']['panel_size']
        
        # 패널 에이전트들
        self.panel_agents: List[PanelAgent] = []
        
        # AutoGen 에이전트 생성
        self.agent = ConversableAgent(
            name="DebateManager",
            system_message=self._create_system_prompt(),
            llm_config={
                "config_list": [{
                    "model": config['ai']['model'],
                    "api_key": api_key,
                    "temperature": config['ai']['temperature'],
                    "max_tokens": config['ai']['max_tokens']
                }]
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        self.logger.info("Debate Manager 초기화 완료")
    
    def _create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        base_prompt = self.config['agents']['debate_manager']['system_prompt']
        
        system_prompt = f"""
{base_prompt}

## 역할과 책임
1. 토론 주제를 분석하고 적절한 전문가 패널을 구성하세요.
2. 토론 방식과 규칙을 명확히 안내하세요.
3. 각 패널에게 공평한 발언 기회를 제공하세요.
4. 토론이 건설적으로 진행되도록 조율하세요.
5. 토론 종료 시 각 패널의 의견을 요약하고 결론을 제시하세요.

## 토론 진행 방식
- 패널토론 방식으로 진행
- 각 패널은 순차적으로 발언
- 상호 토론과 반박 허용
- 약 {self.duration_minutes}분간 진행

응답할 때는 "[토론 진행자]"로 시작하세요.
"""
        return system_prompt
    
    def create_expert_personas(self, topic: str) -> List[Dict[str, str]]:
        """주제에 맞는 전문가 페르소나 생성"""
        persona_prompt = f"""
토론 주제: {topic}

이 주제에 대해 토론할 {self.panel_size}명의 전문가를 설계해주세요.
각 전문가는 서로 다른 배경과 관점을 가져야 합니다.

다음 형식으로 응답해주세요:
1. 전문가 이름: [이름]
   전문분야: [분야]
   배경: [경력 및 배경]
   관점: [주제에 대한 기본 관점]

2. 전문가 이름: [이름]
   전문분야: [분야]
   배경: [경력 및 배경]
   관점: [주제에 대한 기본 관점]

(4명까지)
"""
        
        try:
            response = self.agent.generate_reply(
                messages=[{"content": persona_prompt, "role": "user"}]
            )
            
            # 응답 파싱하여 전문가 정보 추출
            personas = self._parse_expert_personas(response)
            self.logger.info(f"{len(personas)}명의 전문가 페르소나 생성 완료")
            
            return personas
            
        except Exception as e:
            self.logger.error(f"전문가 페르소나 생성 실패: {e}")
            return self._get_default_personas()
    
    def _parse_expert_personas(self, response: str) -> List[Dict[str, str]]:
        """AI 응답에서 전문가 정보 파싱"""
        personas = []
        lines = response.split('\n')
        
        current_expert = {}
        for line in lines:
            line = line.strip()
            if '전문가 이름:' in line:
                if current_expert:
                    personas.append(current_expert)
                current_expert = {'name': line.split(':', 1)[1].strip()}
            elif '전문분야:' in line:
                current_expert['expertise'] = line.split(':', 1)[1].strip()
            elif '배경:' in line:
                current_expert['background'] = line.split(':', 1)[1].strip()
            elif '관점:' in line:
                current_expert['perspective'] = line.split(':', 1)[1].strip()
        
        if current_expert:
            personas.append(current_expert)
        
        return personas[:self.panel_size]
    
    def _get_default_personas(self) -> List[Dict[str, str]]:
        """기본 전문가 페르소나"""
        return [
            {
                "name": "김학술",
                "expertise": "사회과학",
                "background": "서울대학교 사회학과 교수, 20년 경력",
                "perspective": "사회구조적 관점에서 접근"
            },
            {
                "name": "이실무",
                "expertise": "경영학",
                "background": "대기업 CEO 출신, 현재 경영컨설턴트",
                "perspective": "실무적, 경제적 관점에서 접근"
            },
            {
                "name": "박연구",
                "expertise": "기술공학",
                "background": "KAIST 교수, IT 기업 CTO 경력",
                "perspective": "기술적, 혁신적 관점에서 접근"
            },
            {
                "name": "최시민",
                "expertise": "시민사회학",
                "background": "NGO 활동가, 시민단체 대표",
                "perspective": "시민사회, 인권적 관점에서 접근"
            }
        ]
    
    def create_panel_agents(self, personas: List[Dict[str, str]]) -> None:
        """패널 에이전트들 생성"""
        self.panel_agents = []
        
        for persona in personas:
            agent = PanelAgent(
                name=persona['name'],
                expertise=persona['expertise'],
                background=persona['background'],
                perspective=persona['perspective'],
                config=self.config,
                api_key=self.api_key
            )
            self.panel_agents.append(agent)
        
        self.logger.info(f"{len(self.panel_agents)}명의 패널 에이전트 생성 완료")
    
    def start_debate(self, topic: str) -> None:
        """토론 시작"""
        print(f"\n{Fore.BLUE}🔍 주제 분석 및 전문가 패널 구성 중...{Style.RESET_ALL}")
        
        # 1. 전문가 페르소나 생성
        personas = self.create_expert_personas(topic)
        
        # 2. 패널 에이전트 생성
        self.create_panel_agents(personas)
        
        # 3. 토론 방식 안내
        self._announce_debate_format(topic)
        
        # 4. 패널 소개
        self._introduce_panels()
        
        # 5. 토론 진행
        self._conduct_debate(topic)
        
        # 6. 토론 마무리
        self._conclude_debate(topic)
    
    def _announce_debate_format(self, topic: str) -> None:
        """토론 방식 안내"""
        print(f"\n{Fore.CYAN}📋 토론 진행 방식{Style.RESET_ALL}")
        print(f"주제: {Fore.YELLOW}{topic}{Style.RESET_ALL}")
        print(f"방식: 패널토론")
        print(f"시간: 약 {self.duration_minutes}분")
        print(f"참여자: {len(self.panel_agents)}명의 전문가 패널")
        print(f"진행: 순차 발언 → 상호 토론 → 최종 의견")
    
    def _introduce_panels(self) -> None:
        """패널 소개"""
        print(f"\n{Fore.CYAN}👥 패널 소개{Style.RESET_ALL}")
        
        for agent in self.panel_agents:
            intro = agent.introduce()
            print(f"\n{Fore.GREEN}{intro}{Style.RESET_ALL}")
            time.sleep(1)
    
    def _conduct_debate(self, topic: str) -> None:
        """토론 진행"""
        print(f"\n{Fore.CYAN}🎭 토론 시작{Style.RESET_ALL}")
        
        statements = []
        
        # 1단계: 초기 의견 발표
        print(f"\n{Fore.MAGENTA}📢 1단계: 초기 의견 발표{Style.RESET_ALL}")
        for agent in self.panel_agents:
            response = agent.respond_to_topic(topic)
            statements.append(response)
            print(f"\n{response}")
            time.sleep(2)
        
        # 2단계: 상호 토론
        print(f"\n{Fore.MAGENTA}📢 2단계: 상호 토론{Style.RESET_ALL}")
        for turn in range(self.max_turns - 1):
            print(f"\n{Fore.BLUE}--- 토론 라운드 {turn + 1} ---{Style.RESET_ALL}")
            
            for agent in self.panel_agents:
                context = f"토론 라운드 {turn + 1}"
                response = agent.respond_to_debate(context, statements)
                statements.append(response)
                print(f"\n{response}")
                time.sleep(2)
    
    def _conclude_debate(self, topic: str) -> None:
        """토론 마무리"""
        print(f"\n{Fore.CYAN}📝 토론 마무리{Style.RESET_ALL}")
        
        # 토론 요약 생성
        summary = self._generate_debate_summary(topic)
        
        print(f"\n{Fore.MAGENTA}📢 최종 의견{Style.RESET_ALL}")
        for agent in self.panel_agents:
            final_response = agent.final_statement(topic, summary)
            print(f"\n{final_response}")
            time.sleep(2)
        
        # 최종 결론
        conclusion = self._generate_conclusion(topic, summary)
        print(f"\n{Fore.CYAN}🎯 토론 결론{Style.RESET_ALL}")
        print(f"\n{conclusion}")
    
    def _generate_debate_summary(self, topic: str) -> str:
        """토론 요약 생성"""
        summary_prompt = f"""
토론 주제: {topic}

지금까지 진행된 토론의 주요 쟁점과 각 패널의 핵심 의견을 요약해주세요.
"""
        
        try:
            return self.agent.generate_reply(
                messages=[{"content": summary_prompt, "role": "user"}]
            )
        except Exception as e:
            self.logger.error(f"토론 요약 생성 실패: {e}")
            return "토론 요약을 생성할 수 없습니다."
    
    def _generate_conclusion(self, topic: str, summary: str) -> str:
        """최종 결론 생성"""
        conclusion_prompt = f"""
토론 주제: {topic}
토론 요약: {summary}

토론을 마무리하며 다음을 포함한 종합적인 결론을 제시해주세요:
1. 주요 합의점과 차이점
2. 제기된 핵심 쟁점들
3. 향후 고려사항
4. 균형잡힌 시각에서의 종합 의견
"""
        
        try:
            return self.agent.generate_reply(
                messages=[{"content": conclusion_prompt, "role": "user"}]
            )
        except Exception as e:
            self.logger.error(f"결론 생성 실패: {e}")
            return "[토론 진행자] 토론을 마무리합니다. 감사합니다."