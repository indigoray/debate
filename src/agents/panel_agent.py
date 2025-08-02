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
            expertise: 전문 분야
            background: 배경 및 경력
            perspective: 주제에 대한 관점
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

## 당신의 정보
- 이름: {self.name}
- 전문분야: {self.expertise}
- 배경: {self.background}
- 관점: {self.perspective}

## 토론 규칙
1. 자신의 전문성을 바탕으로 논리적이고 설득력 있는 의견을 제시하세요.
2. 다른 패널의 의견을 존중하되, 건설적인 반박도 환영합니다.
3. 구체적인 예시나 데이터를 활용하여 주장을 뒷받침하세요.
4. 간결하고 명확하게 의견을 표현하세요 (500자 이내).
5. 토론 주제에서 벗어나지 마세요.

## 응답 형식
응답할 때는 다음 형식을 사용하세요:
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