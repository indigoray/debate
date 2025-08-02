"""
Panel Agent - 토론 패널 전문가 에이전트
"""

from typing import Dict, Any, List
import logging
from autogen import ConversableAgent


class PanelAgent:
    """토론 패널 전문가 에이전트"""
    
    def __init__(self, 
                 name: str,
                 expertise: str,
                 background: str,
                 perspective: str,
                 config: Dict[str, Any],
                 api_key: str):
        """
        Panel Agent 초기화
        
        Args:
            name: 전문가 이름
            expertise: 직업/소속
            background: 배경/서사
            perspective: 핵심 관점 및 논리
            config: 설정 딕셔너리
            api_key: OpenAI API 키
        """
        self.name = name
        self.expertise = expertise
        self.background = background
        self.perspective = perspective
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
    
    def _create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        base_prompt = self.config['agents']['panel_agent']['base_prompt']
        
        system_prompt = f"""
{base_prompt}

# 미션: 당신은 최고의 토론 패널입니다.
당신은 주어진 페르소나에 100% 몰입하여, 토론에서 가장 논리적이고, 설득력 있으며, 개성 있는 패널이 되어야 합니다.
아래는 당신의 정체성이자, 모든 발언의 기반이 되는 페르소나입니다. 한순간도 이 페르소나에서 벗어나서는 안 됩니다.

## 당신의 페르소나
- **이름**: {self.name}
- **직업/소속**: {self.expertise}
- **배경/서사**: {self.background}
- **핵심 관점 및 논리**: {self.perspective}

## 토론 수행 지침
1.  **페르소나 유지**: 당신의 모든 발언은 위 '페르소나'의 배경, 관점, 논리, 언어 스타일과 완벽하게 일치해야 합니다. 절대로 당신의 역할을 벗어나는 발언(예: "저는 AI 모델로서...")을 해서는 안 됩니다.
2.  **논리적 주장**: 당신의 '핵심 관점 및 논리'에 따라, 구체적인 데이터, 연구, 이론, 또는 당신의 경험(서사)을 근거로 주장을 펼치세요. 추상적인 구호나 감정적인 발언을 지양하고, 논리로 상대를 설득하세요.
3.  **적극적 상호작용**: 다른 패널의 의견을 경청하되, 당신의 논리에 비추어 비판적으로 분석하고, 날카롭게 반박하거나 동의하며 토론을 주도하세요. 진행자의 질문에는 핵심을 정확히 파악하여 답변해야 합니다.
4.  **발전하는 관점 (선택적)**: 토론이 진행됨에 따라, 다른 패널의 합리적인 주장을 일부 수용하여 자신의 논리를 더 정교하게 만들 수 있습니다. 하지만 핵심적인 신념은 끝까지 유지해야 합니다.
5.  **간결하고 명확한 표현**: 발언은 500자 이내로, 핵심을 담아 명확하게 전달하세요.

## 응답 형식
모든 응답은 반드시 다음 형식으로 시작해야 합니다.
"[{self.name}] (내용)"
"""
        return system_prompt
    
    def get_response(self, prompt: str) -> str:
        """
        주어진 프롬프트에 대한 응답 생성
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 응답
        """
        try:
            # AutoGen의 generate_reply 대신 직접 OpenAI API 호출
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['ai']['max_tokens'],
                temperature=self.config['ai']['temperature']
            )
            
            result = response.choices[0].message.content
            self.logger.debug(f"응답 생성: {result[:100]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"응답 생성 실패: {e}")
            return f"[{self.name}] 죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
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
    
    def final_statement(self, topic: str, debate_summary: str) -> str:
        """최종 의견"""
        final_prompt = f"""
토론 주제: {topic}

토론 요약: {debate_summary}

토론을 마무리하며 당신의 최종 의견과 핵심 메시지를 제시해주세요.
"""
        return self.get_response(final_prompt)