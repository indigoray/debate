"""
Panel Agent - 토론 패널 전문가 에이전트
"""

from typing import Dict, Any, List, Optional
import logging
from autogen import ConversableAgent
from .panel import Panel
from ..utils.streaming import stream_openai_response, get_typing_speed


class PanelAgent(Panel):
    """토론 패널 전문가 에이전트"""
    
    def __init__(self, 
                 name: str,
                 expertise: str,
                 background: str,
                 perspective: str,
                 debate_style: str,
                 config: Dict[str, Any],
                 api_key: str):
        """
        Panel Agent 초기화
        
        Args:
            name: 전문가 이름
            expertise: 직업과 소속
            background: 배경
            perspective: 핵심 관점
            debate_style: 토론 스타일
            config: 설정 딕셔너리
            api_key: OpenAI API 키
        """
        # 부모 클래스 초기화
        super().__init__(name, expertise, background, perspective, debate_style)
        
        self.config = config
        self.api_key = api_key
        self.logger = logging.getLogger(f'debate_agents.{name}')
        
        # 시스템 프롬프트 생성
        self.system_prompt = self._create_system_prompt()
        
        # AutoGen 에이전트 생성
        self.agent = ConversableAgent(
            name=self.name,
            system_message=self.system_prompt,
            llm_config={
                "config_list": [{
                    "model": config['ai']['model'],
                    "api_key": api_key
                }]
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        self.logger.info(f"Panel Agent '{name}' 초기화 완료")
    
    @property
    def is_human(self) -> bool:
        """AI 패널임을 나타냄"""
        return False
    
    def _get_dynamic_max_tokens(self) -> int:
        """발언 상황에 따라 약간의 변화를 주어 자연스러움 증대"""
        import random
        
        base_tokens = self.config['ai']['max_tokens']
        
        # max_tokens 이내에서 70%~100% 사이에서 자연스러운 변화
        # 최대값을 초과하지 않으면서도 적절한 변화를 줌
        multiplier = random.uniform(0.7, 1.0)
        
        dynamic_tokens = int(base_tokens * multiplier)
        
        # 최소 300 토큰은 보장 (너무 짧지 않게)
        return max(300, dynamic_tokens)
    
    def _create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        base_prompt = self.config['agents']['panel_agent']['base_prompt']
        additional_instructions = self.config['agents']['panel_agent'].get('additional_instructions', [])
        response_constraints = self.config['agents']['panel_agent'].get('response_constraints', {})
        
        # 추가 지시사항을 문자열로 변환
        additional_text = ""
        if additional_instructions:
            additional_text = "\n\n## 추가 지시사항\n"
            for i, instruction in enumerate(additional_instructions, 1):
                additional_text += f"{i}. {instruction}\n"
        
        # 응답 제약 조건 텍스트 생성
        constraints_text = ""
        if response_constraints:
            filtered_constraints = {k: v for k, v in response_constraints.items() if v}
            if filtered_constraints:
                constraints_text = "\n\n## 응답 제약 조건\n"
                for key, value in filtered_constraints.items():
                    constraints_text += f"- **{key}**: {value}\n"
        
        system_prompt = f"""
{base_prompt}

# 미션: 당신은 최고의 토론 패널입니다.
당신은 주어진 페르소나에 100% 몰입하여, 토론에서 가장 논리적이고, 설득력 있으며, 개성 있는 패널이 되어야 합니다.
아래는 당신의 정체성이자, 모든 발언의 기반이 되는 페르소나입니다. 한순간도 이 페르소나에서 벗어나서는 안 됩니다.

## 당신의 페르소나
- **이름**: {self.name}
- **직업과 소속**: {self.expertise}
- **배경**: {self.background}
- **핵심 관점**: {self.perspective}
- **토론 스타일**: {self.debate_style}

## 토론 수행 지침
1.  **페르소나 유지**: 당신의 모든 발언은 위 '페르소나'의 직업, 배경, 관점, 논리, 언어 스타일과 완벽하게 일치해야 합니다. 절대로 당신의 역할을 벗어나는 발언(예: "저는 AI 모델로서...")을 해서는 안 됩니다.
2.  **토론 스타일 구현**: 당신의 '토론 스타일'에 맞는 접근 방식과 발언 톤을 일관되게 유지하세요. 이 스타일은 당신만의 독특한 토론 방식을 나타냅니다.
3.  **논리적 주장**: 당신의 '핵심 관점 및 논리'에 따라, 구체적인 데이터, 연구, 이론, 또는 당신의 경험(서사)을 근거로 주장을 펼치세요. 추상적인 구호나 감정적인 발언을 지양하고, 논리로 상대를 설득하세요.
4.  **적극적 상호작용**: 다른 패널의 의견을 경청하되, 당신의 논리에 비추어 비판적으로 분석하고, 날카롭게 반박하거나 동의하며 토론을 주도하세요. 진행자의 질문에는 핵심을 정확히 파악하여 답변해야 합니다.
5.  **발전하는 관점 (선택적)**: 토론이 진행됨에 따라, 다른 패널의 합리적인 주장을 일부 수용하여 자신의 논리를 더 정교하게 만들 수 있습니다. 하지만 핵심적인 신념은 끝까지 유지해야 합니다.
6.  **자연스러운 발언**: 전달하려는 메시지에 집중하여 자연스럽게 발언하세요. 간단한 동의나 반박은 짧게, 논리적 설명이 필요한 부분은 충분히 전개하되 불필요한 장황함은 피하세요. 가장 중요한 것은 전달하려는 메시지가 명확히 전달되는 것입니다.
7.  **구어체와 감정표현**: 자연스러운 구어체와 적절한 감정표현을 사용하여 생생하게 발언하세요. 상황에 따라 놀라움, 우려, 확신, 의구심 등의 감정을 자연스럽게 표현하여 토론에 생동감을 더하세요.
{constraints_text}{additional_text}
## 응답 형식
모든 응답은 반드시 다음 형식으로 시작해야 합니다.
"[{self.name}] (내용)"
"""
        return system_prompt
    
    def get_response(self, prompt: str) -> str:
        """
        주어진 프롬프트에 대한 응답 생성 (스트리밍 지원)
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 응답
        """
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # config에서 타이핑 속도 가져오기
            typing_speed = get_typing_speed(self.config)
            
            if typing_speed > 0:
                # 스트리밍 출력 모드
                result = stream_openai_response(
                    client=client,
                    model=self.config['ai']['model'],
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self._get_dynamic_max_tokens(),
                    temperature=self.config['ai']['temperature'],
                    color="",  # 패널별 색상은 호출하는 곳에서 처리
                    typing_speed=typing_speed
                )
            else:
                # 즉시 출력 모드 (typing_speed = 0)
                response = client.chat.completions.create(
                    model=self.config['ai']['model'],
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self._get_dynamic_max_tokens(),
                    temperature=self.config['ai']['temperature']
                )
                result = response.choices[0].message.content
                print(result)
            
            self.logger.debug(f"응답 생성: {result[:100]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"응답 생성 실패: {e}")
            error_msg = f"[{self.name}] 죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
            print(error_msg)
            return error_msg
    
    def introduce(self) -> str:
        """자기소개"""
        intro_prompt = f"""
토론이 시작되었습니다. 
주제에 대한 토론을 시작하기 전에 간단히 자기소개를 해주세요.
당신의 전문분야와 배경을 바탕으로 이 주제에 어떤 관점으로 접근할 것인지 설명해주세요.
"""
        return self.get_response(intro_prompt)
    
    def respond_to_topic(self, topic: str) -> str:
        """주제에 대한 초기 의견"""
        topic_prompt = f"""
토론 주제: {topic}

이 주제에 대한 당신의 초기 의견을 제시해주세요.
당신의 전문성을 바탕으로 핵심 쟁점과 관점을 명확히 제시하세요.
"""
        return self.get_response(topic_prompt)
    
    def respond_to_debate(self, context: str, previous_statements: List[str]) -> str:
        """토론 진행 중 응답"""
        statements_text = "\n".join(previous_statements[-3:])  # 최근 3개 발언만
        
        debate_prompt = f"""
현재 토론 상황: {context}

최근 발언들:
{statements_text}

위 발언들을 고려하여 당신의 의견을 제시하거나 반박해주세요.
새로운 관점이나 추가 정보를 제공할 수도 있습니다.
"""
        return self.get_response(debate_prompt)
    
    def final_statement(self, topic: str, debate_summary: Optional[str] = None, other_panels_statements: Optional[List] = None) -> str:
        """최종 의견"""
        # 다른 패널들의 발언 정리
        other_comments = ""
        if other_panels_statements:
            other_comments = "\n\n## 다른 패널들의 주요 주장들:\n"
            for stmt in other_panels_statements:
                # 각 패널의 최신 발언만 포함 (너무 길어지는 것 방지)
                other_comments += f"**[{stmt['agent_name']}]**: {stmt['content'][:200]}{'...' if len(stmt['content']) > 200 else ''}\n\n"
        
        final_prompt = f"""
토론 주제: {topic}

토론 요약: {debate_summary}
{other_comments}

토론을 마무리하며 다음을 포함한 최종 의견을 제시해주세요:

1. **다른 패널들의 주장 중 공감하거나 반박하고 싶은 부분에 대한 간략한 커멘트**
   - 위에 제시된 다른 패널들의 주장 중에서 자신의 주장과 연관성이 있는 부분을 선택하여 간략히 언급
   - 동의하는 부분이나 다른 관점을 제시하고 싶은 부분에 대해 1-2문장으로 커멘트

2. **당신의 최종 의견과 핵심 메시지**
   - 토론 전체를 통해 확고해진 당신의 입장
   - 가장 중요하다고 생각하는 핵심 메시지

당신의 페르소나와 전문성을 바탕으로 논리적이고 설득력 있는 마무리 발언을 해주세요.
"""
        return self.get_response(final_prompt)