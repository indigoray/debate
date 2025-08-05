"""
ResponseGenerator - AI 응답 생성 클래스
"""

import logging
from typing import Dict, Any, List
from colorama import Fore, Style

from ..utils.streaming import stream_openai_response, get_typing_speed


class ResponseGenerator:
    """AI 응답 생성을 담당하는 클래스 (브리핑, 요약, 결론, 진행 메시지)"""
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        ResponseGenerator 초기화
        
        Args:
            config: 설정 딕셔너리
            api_key: OpenAI API 키
        """
        self.config = config
        self.api_key = api_key
        self.logger = logging.getLogger('debate_agents.response_generator')
    
    def generate_topic_briefing(self, topic: str, system_prompt: str) -> str:
        """토론 주제에 대한 배경 브리핑 생성"""
        briefing_prompt = f"""
토론 주제: {topic}

당신은 전문적인 토론 진행자입니다. 위 토론 주제에 대해 시청자들이 쉽게 이해할 수 있도록 2-3분 분량의 간결한 브리핑을 작성해주세요.

다음 내용을 포함해주세요:
1. 이 주제가 왜 중요하고 논란이 되는지
2. 현재 사회적 배경과 맥락
3. 주요 쟁점들과 대립되는 관점들
4. 이 토론이 우리에게 왜 의미가 있는지

브리핑은 "[토론 진행자]"로 시작하여 친근하면서도 전문적인 톤으로 작성해주세요.
"""
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # 타이핑 속도 가져오기
            typing_speed = get_typing_speed(self.config)
            
            if typing_speed > 0:
                # 스트리밍으로 브리핑 생성
                result = stream_openai_response(
                    client=client,
                    model=self.config['ai']['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": briefing_prompt}
                    ],
                    max_tokens=self.config['ai']['max_tokens'],
                    temperature=self.config['ai']['temperature'],
                    color=Fore.MAGENTA,
                    typing_speed=typing_speed
                )
            else:
                # 즉시 출력 모드
                response = client.chat.completions.create(
                    model=self.config['ai']['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": briefing_prompt}
                    ],
                    max_tokens=self.config['ai']['max_tokens'],
                    temperature=self.config['ai']['temperature']
                )
                result = response.choices[0].message.content
                print(f"{Fore.MAGENTA}{result}{Style.RESET_ALL}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"주제 브리핑 생성 실패: {e}")
            return f"[토론 진행자] 오늘 우리가 다룰 주제는 '{topic}'입니다. 이는 현대 사회에서 중요한 논의가 필요한 주제로, 다양한 관점에서 심도 있게 살펴볼 필요가 있습니다."
    
    def generate_debate_summary(self, topic: str, system_prompt: str) -> str:
        """토론 요약 생성"""
        summary_prompt = f"""
토론 주제: {topic}

지금까지 진행된 토론의 주요 쟁점과 각 패널의 핵심 의견을 요약해주세요.
"""
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # 스트리밍으로 요약 생성 (출력 없이 생성만)
            response = client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=self.config['ai']['max_tokens'],
                temperature=self.config['ai']['temperature']
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"토론 요약 생성 실패: {e}")
            return "토론 요약을 생성할 수 없습니다."
    
    def generate_conclusion(self, topic: str, panel_agents: List, summary: str, system_prompt: str) -> str:
        """최종 결론 생성"""
        # 실제 참여한 패널 정보 구성
        panel_info = ""
        for i, agent in enumerate(panel_agents, 1):
            panel_info += f"- **{agent.name}** ({agent.expertise}): {agent.perspective}\n"
        
        conclusion_prompt = f"""
토론 주제: {topic}

참여 패널:
{panel_info}

토론 요약: {summary}

위 {len(panel_agents)}명의 패널이 참여한 토론을 마무리하며 다음을 포함한 종합적인 결론을 제시해주세요:

1. **주요 합의점**: 패널들이 공통으로 동의한 부분들
2. **주요 차이점과 핵심 쟁점**: 각 패널의 서로 다른 관점과 핵심 대립점 (각 패널의 이름과 전문분야를 명시하여 구체적으로 기술)
3. **향후 고려사항**: 토론에서 제기된 과제와 남은 질문들
4. **균형잡힌 시각에서의 종합 의견**: 전체적인 결론과 시사점

반드시 실제 참여한 모든 패널의 관점을 구체적으로 반영하여 작성해주세요.
"""
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # 타이핑 속도 가져오기
            typing_speed = get_typing_speed(self.config)
            
            if typing_speed > 0:
                # 스트리밍으로 결론 생성
                result = stream_openai_response(
                    client=client,
                    model=self.config['ai']['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": conclusion_prompt}
                    ],
                    max_tokens=self._get_max_tokens('conclusion'),
                    temperature=self.config['ai']['temperature'],
                    color=Fore.CYAN,
                    typing_speed=typing_speed
                )
            else:
                # 즉시 출력 모드
                response = client.chat.completions.create(
                    model=self.config['ai']['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": conclusion_prompt}
                    ],
                    max_tokens=self._get_max_tokens('conclusion'),
                    temperature=self.config['ai']['temperature']
                )
                result = response.choices[0].message.content
                print(f"{Fore.CYAN}{result}{Style.RESET_ALL}")
            
            return result
        except Exception as e:
            self.logger.error(f"결론 생성 실패: {e}")
            return "[토론 진행자] 토론을 마무리합니다. 감사합니다."
    
    def generate_manager_message(self, message_type: str, context: str) -> str:
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
    
    def _get_max_tokens(self, task_type: str = "default") -> int:
        """작업 유형에 따른 max_tokens 계산"""
        base_tokens = self.config['ai']['max_tokens']
        multipliers = self.config['ai'].get('token_multipliers', {})
        multiplier = multipliers.get(task_type, 1.0)
        return int(base_tokens * multiplier)