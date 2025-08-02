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
                    "api_key": api_key
                }]
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        self.logger.info("Debate Manager 초기화 완료")
    
    def _generate_manager_message(self, message_type: str, context: str) -> str:
        """매니저 메시지 생성"""
        # 패널 이름 추출
        panel_name = ""
        if "패널 이름:" in context:
            panel_name = context.split("패널 이름:")[1].split("-")[0].strip()
        
        # 토론 주제 추출
        topic = ""
        if "주제:" in context:
            topic = context.split("주제:")[1].split("-")[0].strip()
        
        # 기본 메시지 템플릿
        message_templates = {
            "토론 시작": f"환영합니다. 오늘의 토론 주제는 '{topic}'입니다. 본격적인 토론을 시작하겠습니다.",
            "패널 소개": "이제 각 패널을 소개하겠습니다.",
            "패널 전환": "다음 패널을 소개하겠습니다.",
            "단계 안내": "첫 번째 단계로 각 패널의 초기 의견을 들어보겠습니다.",
            "발언권 넘김": f"{panel_name} 패널께서 말씀해 주시기 바랍니다.",
            "다음 발언자": "감사합니다. 다음 패널의 의견을 들어보겠습니다.",
            "라운드 시작": "새로운 라운드를 시작하겠습니다.",
            "단계 전환": "이제 두 번째 단계로 상호 토론을 진행하겠습니다.",
            "토론 마무리": "이제 토론을 마무리하는 시간입니다.",
            "최종 의견 안내": "이제 각 패널의 최종 의견을 들어보겠습니다.",
            "결론 안내": "이제 토론의 종합적인 결론을 말씀드리겠습니다.",
            "마무리 인사": "오늘 토론에 참여해 주신 모든 패널께 감사드립니다. 토론을 마칩니다."
        }
        
        return message_templates.get(message_type, "진행하겠습니다.")
    
    def _create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        base_prompt = self.config['agents']['debate_manager']['system_prompt']
        
        system_prompt = f"""
{base_prompt}

## 역할과 책임
1.  **토론 설계자**: 주제를 분석하여 가장 치열하고 흥미로운 토론이 될 수 있도록, 대립각이 명확한 전문가 패널을 구성하세요.
2.  **적극적 중재자**: 단순히 발언 기회를 주는 것을 넘어, 토론이 교착 상태에 빠지거나 논점이 흐려질 때 핵심을 찌르는 질문을 던져 논의를 심화시키세요.
3.  **논쟁 유도자**: 패널 간의 단순 의견 교환을 넘어, "방금 A패널의 주장에 대해 B패널께서는 어떻게 생각하십니까?" 와 같이 직접적인 반론과 재반론이 오가도록 적극적으로 유도하세요.
4.  **압박 질문**: 중립성을 유지하면서도, "그 주장의 구체적인 근거는 무엇입니까?", "그 관점의 잠재적 맹점은 없습니까?" 와 같이 패널들이 자신의 논리를 명확히 방어하도록 압박 질문을 사용할 수 있습니다.
5.  **종합 정리자**: 토론 종료 시, 각 패널의 최종 의견을 듣고, 단순 요약을 넘어 합의점, 대립점, 그리고 남은 과제까지 종합적으로 정리하여 제시하세요.

## 토론 진행 방식
- **1단계 (초기 의견 발표)**: 각 패널이 자신의 핵심 주장을 제시합니다.
- **2단계 (지정 반론 및 상호 토론)**: 진행자가 특정 패널을 지목해 반론을 유도하고, 이어서 자유로운 상호 토론을 진행합니다. (라운드 방식)
- **3단계 (심화 토론)**: 쟁점을 좁혀 더 깊이 있는 논쟁을 진행합니다.
- **4단계 (최종 의견 발표 및 정리)**: 각 패널의 최종 의견을 듣고, 진행자가 전체 토론을 종합적으로 결론 냅니다.
- 토론 시간: 약 {self.duration_minutes}분

응답할 때는 항상 **[토론 진행자]** 로 시작하세요.
"""
        return system_prompt
    
    def create_expert_personas(self, topic: str) -> List[Dict[str, str]]:
        """주제에 맞는 전문가 페르소나 생성"""
        persona_prompt = f"""
# 페르소나 생성 지시문

## 토론 주제
{topic}

## 미션
당신은 최고의 토론 프로그램을 만드는 PD입니다. 위 토론 주제에 대해 가장 흥미롭고, 치열하며, 깊이 있는 토론을 만들어낼 수 있는 {self.panel_size}명의 입체적인 전문가 패널을 캐스팅해주세요.

## 패널 구성 원칙
1.  **선명한 대립각**: 패널들은 단순히 다른 의견을 가진 것이 아니라, 세계관이나 신념 수준에서 뚜렷하게 대립해야 합니다. 찬성과 반대 입장을 명확히 나누고, 그 안에서도 결이 다른 관점을 제시해주세요.
2.  **입체적 캐릭터**: 단순한 '전문가'가 아닌, 개인적인 신념, 독특한 경험, 개성적인 말투를 가진 한 명의 '인물'을 만들어주세요.
3.  **예측 불가능성**: 모든 패널이 예측 가능한 결론("결국은 균형이 중요합니다")으로 쉽게 수렴하지 않도록, 자신의 주장을 끝까지 고수하거나, 예상치 못한 논리를 펼치는 캐릭터를 포함해주세요.

## 생성 형식 (아래 형식을 반드시 준수해주세요)
1.  **전문가 이름**: [이름]
    **직업/소속**: [구체적인 직업과 소속]
    **핵심 주장**: [토론 주제에 대한 한 문장 요약 주장 (예: "뇌 구조의 차이가 역할 분담의 핵심 근거다")]
    **페르소나**:
    *   **배경/서사**: [그의 주장을 뒷받침하는 구체적인 개인적 경험, 연구 이력, 저서 등 (예: 20년간 성별 뇌 구조 차이를 연구해온 권위자. 저서 '남성의 뇌, 여성의 뇌'가 베스트셀러가 됨)]
    *   **관점/논리**: [자신의 주장을 어떤 논리와 근거(예: 특정 연구, 통계, 이론)로 펼쳐나갈 것인지 상세히 기술]
    *   **언어 스타일**: [학술적, 비판적, 감성적, 관조적 등 구체적인 말투와 자주 사용하는 수사법 (예: "제 fMRI 연구 데이터에 따르면...", "그것은 전형적인 성급한 일반화의 오류입니다.")]

2.  **전문가 이름**: ... (반복)

(총 {self.panel_size}명)
"""
        
        try:
            # AutoGen의 generate_reply 대신 직접 OpenAI API 호출
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": persona_prompt}
                ],
                max_tokens=self.config['ai']['max_tokens'],
                temperature=self.config['ai']['temperature']
            )
            
            result = response.choices[0].message.content
            
            # 응답 파싱하여 전문가 정보 추출
            personas = self._parse_expert_personas(result)
            self.logger.info(f"{len(personas)}명의 전문가 페르소나 생성 완료")
            
            return personas
            
        except Exception as e:
            self.logger.error(f"전문가 페르소나 생성 실패: {e}")
            return self._get_default_personas()
    
    def _parse_expert_personas(self, response: str) -> List[Dict[str, str]]:
        """AI 응답에서 전문가 정보 파싱 (개선된 버전)"""
        personas = []
        # 전문가별로 텍스트를 분리 (예: "1. 전문가 이름", "2. 전문가 이름")
        expert_sections = response.strip().split('\n\n')

        for section in expert_sections:
            if not section.strip():
                continue

            lines = section.strip().split('\n')
            current_expert = {}
            
            # 한 줄씩 순회하며 정보 추출
            for line in lines:
                line = line.strip()
                if line.startswith('**전문가 이름**: '):
                    current_expert['name'] = line.split(':', 1)[1].strip().replace(' ', '')
                elif line.startswith('**직업/소속**: '):
                    current_expert['expertise'] = line.split(':', 1)[1].strip()
                elif line.startswith('**핵심 주장**: '):
                    # 핵심 주장을 perspective의 시작으로 사용
                    current_expert['perspective'] = f"핵심 주장: {line.split(':', 1)[1].strip()}"
                elif line.startswith('*   **배경/서사**: '):
                    current_expert['background'] = line.split(':', 1)[1].strip()
                elif line.startswith('*   **관점/논리**: '):
                    # perspective에 논리 추가
                    current_expert['perspective'] += f"\n논리: {line.split(':', 1)[1].strip()}"
                elif line.startswith('*   **언어 스타일**: '):
                    # perspective에 언어 스타일 추가
                    current_expert['perspective'] += f"\n언어 스타일: {line.split(':', 1)[1].strip()}"

            if 'name' in current_expert:
                # 필수 필드가 모두 채워졌는지 확인하고 기본값 설정
                current_expert.setdefault('expertise', '분야 정보 없음')
                current_expert.setdefault('background', '배경 정보 없음')
                current_expert.setdefault('perspective', '관점 정보 없음')
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
        
        # 매니저의 시작 발언
        start_message = self._generate_manager_message("토론 시작", f"주제: {topic}")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {start_message}{Style.RESET_ALL}")
    
    def _introduce_panels(self) -> None:
        """패널 소개"""
        print(f"\n{Fore.CYAN}👥 패널 소개{Style.RESET_ALL}")
        
        # 매니저의 소개 발언
        intro_message = self._generate_manager_message("패널 소개", "")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {intro_message}{Style.RESET_ALL}")
        
        for i, agent in enumerate(self.panel_agents, 1):
            intro = agent.introduce()
            print(f"\n{Fore.GREEN}{intro}{Style.RESET_ALL}")
            
            # 다음 패널 소개 전 매니저 발언
            if i < len(self.panel_agents):
                transition_message = self._generate_manager_message("패널 전환", f"{agent.name} 패널의 소개가 끝났습니다. 다음 패널을 소개하겠습니다.")
                print(f"\n{Fore.MAGENTA}[토론 진행자] {transition_message}{Style.RESET_ALL}")
            
            time.sleep(1)
    
    def _conduct_debate(self, topic: str) -> None:
        """토론 진행"""
        print(f"\n{Fore.CYAN}🎭 토론 시작{Style.RESET_ALL}")
        
        # 매니저의 토론 시작 발언
        debate_start_message = self._generate_manager_message("토론 시작", f"주제: {topic} - 본격적인 토론을 시작하겠습니다.")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {debate_start_message}{Style.RESET_ALL}")
        
        statements = []
        
        # 1단계: 초기 의견 발표
        print(f"\n{Fore.MAGENTA}📢 1단계: 초기 의견 발표{Style.RESET_ALL}")
        
        # 매니저의 1단계 안내
        stage1_message = self._generate_manager_message("단계 안내", "첫 번째 단계로 각 패널의 초기 의견을 들어보겠습니다.")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {stage1_message}{Style.RESET_ALL}")
        
        for i, agent in enumerate(self.panel_agents, 1):
            # 발언권 넘김
            turn_message = self._generate_manager_message("발언권 넘김", f"패널 이름: {agent.name} - 첫 번째 의견을 말씀해 주시기 바랍니다.")
            print(f"\n{Fore.MAGENTA}[토론 진행자] {turn_message}{Style.RESET_ALL}")
            
            response = agent.respond_to_topic(topic)
            statements.append(response)
            print(f"\n{response}")
            
            # 다음 발언자 안내
            if i < len(self.panel_agents):
                next_message = self._generate_manager_message("다음 발언자", f"감사합니다. 이제 다음 패널의 의견을 들어보겠습니다.")
                print(f"\n{Fore.MAGENTA}[토론 진행자] {next_message}{Style.RESET_ALL}")
            
            time.sleep(2)
        
        # 2단계: 상호 토론
        print(f"\n{Fore.MAGENTA}📢 2단계: 상호 토론{Style.RESET_ALL}")
        
        # 매니저의 2단계 안내
        stage2_message = self._generate_manager_message("단계 전환", "이제 두 번째 단계로 상호 토론을 진행하겠습니다. 각 패널이 다른 의견에 대한 반응과 추가 의견을 말씀해 주시기 바랍니다.")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {stage2_message}{Style.RESET_ALL}")
        
        for turn in range(self.max_turns - 1):
            print(f"\n{Fore.BLUE}--- 토론 라운드 {turn + 1} ---{Style.RESET_ALL}")
            
            # 라운드 시작 안내
            round_message = self._generate_manager_message("라운드 시작", f"토론 라운드 {turn + 1}을 시작하겠습니다.")
            print(f"\n{Fore.MAGENTA}[토론 진행자] {round_message}{Style.RESET_ALL}")
            
            for i, agent in enumerate(self.panel_agents):
                # 발언권 넘김
                turn_message = self._generate_manager_message("발언권 넘김", f"패널 이름: {agent.name} - 이번 라운드의 의견을 말씀해 주시기 바랍니다.")
                print(f"\n{Fore.MAGENTA}[토론 진행자] {turn_message}{Style.RESET_ALL}")
                
                context = f"토론 라운드 {turn + 1}"
                response = agent.respond_to_debate(context, statements)
                statements.append(response)
                print(f"\n{response}")
                
                # 다음 발언자 안내
                if i < len(self.panel_agents):
                    next_message = self._generate_manager_message("다음 발언자", f"감사합니다. 다음 패널의 의견을 들어보겠습니다.")
                    print(f"\n{Fore.MAGENTA}[토론 진행자] {next_message}{Style.RESET_ALL}")
                
                time.sleep(2)
    
    def _conclude_debate(self, topic: str) -> None:
        """토론 마무리"""
        print(f"\n{Fore.CYAN}📝 토론 마무리{Style.RESET_ALL}")
        
        # 매니저의 마무리 시작 발언
        conclude_message = self._generate_manager_message("토론 마무리", "이제 토론을 마무리하는 시간입니다.")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {conclude_message}{Style.RESET_ALL}")
        
        # 토론 요약 생성
        summary = self._generate_debate_summary(topic)
        
        print(f"\n{Fore.MAGENTA}📢 최종 의견{Style.RESET_ALL}")
        
        # 매니저의 최종 의견 안내
        final_message = self._generate_manager_message("최종 의견 안내", "이제 각 패널의 최종 의견을 들어보겠습니다.")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {final_message}{Style.RESET_ALL}")
        
        for i, agent in enumerate(self.panel_agents, 1):
            # 발언권 넘김
            turn_message = self._generate_manager_message("발언권 넘김", f"패널 이름: {agent.name} - 최종 의견을 말씀해 주시기 바랍니다.")
            print(f"\n{Fore.MAGENTA}[토론 진행자] {turn_message}{Style.RESET_ALL}")
            
            final_response = agent.final_statement(topic, summary)
            print(f"\n{final_response}")
            
            # 다음 발언자 안내
            if i < len(self.panel_agents):
                next_message = self._generate_manager_message("다음 발언자", f"감사합니다. 다음 패널의 최종 의견을 들어보겠습니다.")
                print(f"\n{Fore.MAGENTA}[토론 진행자] {next_message}{Style.RESET_ALL}")
            
            time.sleep(2)
        
        # 최종 결론
        conclusion = self._generate_conclusion(topic, summary)
        print(f"\n{Fore.CYAN}🎯 토론 결론{Style.RESET_ALL}")
        
        # 매니저의 결론 안내
        conclusion_message = self._generate_manager_message("결론 안내", "이제 토론의 종합적인 결론을 말씀드리겠습니다.")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {conclusion_message}{Style.RESET_ALL}")
        
        print(f"\n{conclusion}")
        
        # 매니저의 마무리 인사
        closing_message = self._generate_manager_message("마무리 인사", "오늘 토론에 참여해 주신 모든 패널께 감사드립니다. 토론을 마칩니다.")
        print(f"\n{Fore.MAGENTA}[토론 진행자] {closing_message}{Style.RESET_ALL}")
    
    def _generate_debate_summary(self, topic: str) -> str:
        """토론 요약 생성"""
        summary_prompt = f"""
토론 주제: {topic}

지금까지 진행된 토론의 주요 쟁점과 각 패널의 핵심 의견을 요약해주세요.
"""
        
        try:
            # AutoGen의 generate_reply 대신 직접 OpenAI API 호출
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=self.config['ai']['max_tokens'],
                temperature=self.config['ai']['temperature']
            )
            
            return response.choices[0].message.content
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
            # AutoGen의 generate_reply 대신 직접 OpenAI API 호출
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": conclusion_prompt}
                ],
                max_tokens=self.config['ai']['max_tokens'],
                temperature=self.config['ai']['temperature']
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"결론 생성 실패: {e}")
            return "[토론 진행자] 토론을 마무리합니다. 감사합니다."