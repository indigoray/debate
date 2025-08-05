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
    
    def analyze_debate_state(self, topic: str, recent_statements: List[str], last_round_type: str = None, change_angle_cooldown: bool = False) -> Dict[str, Any]:
        """현재 토론 상태를 분석하여 다음 액션 결정 (Dynamic 모드용)"""
        analysis_prompt = f"""
토론 주제: {topic}

최근 발언들:
{chr(10).join(recent_statements[-6:]) if recent_statements else "아직 발언이 없습니다."}

현재 토론 상태를 분석하고 다음을 결정해주세요. **더 역동적이고 흥미진진한 토론을 위해 적극적인 개입을 선호합니다.**

1. **토론 온도**: heated(열띤), balanced(균형잡힌), cold(식어가는), stuck(교착)
2. **주요 쟁점**: 현재 가장 핵심적인 논쟁거리
3. **놓친 관점**: 아직 다뤄지지 않은 중요한 관점
4. **다음 액션**: 
   - continue_normal: 정상 진행 (지루할 때만 선택)
   - provoke_debate: 논쟁 유도 필요 (추천! 대립각 형성)
   - change_angle: 새로운 관점 제시 (새로운 시각 도입) {"❌ 쿨다운 중 - 선택 불가" if change_angle_cooldown else "✅ 선택 가능"}
   - pressure_evidence: 근거 요구 (구체적 데이터 압박)
   - focus_clash: 특정 패널 간 직접 대결 (추천! 1:1 논쟁)

5. **구체적 개입방안**: 위 액션을 위한 구체적인 질문이나 개입 방법

**지침**: 
- **다양성 우선**: 이전 라운드({last_round_type or "없음"})와 같은 타입은 피하고 다른 타입을 선택하세요
- 연속으로 focus_clash(직접 대결)는 금지! 다른 타입으로 변화를 주세요
- **쿨다운 제한**: {"change_angle은 쿨다운 중이므로 선택 불가" if change_angle_cooldown else "모든 타입 선택 가능"}
- 토론이 평범하면 provoke_debate, {"pressure_evidence 중 선택 (change_angle 제외)" if change_angle_cooldown else "change_angle, pressure_evidence 중 선택"}
- 패널들이 너무 온화하게 동의하면 대립을 유도하세요
- 구체적인 패널 이름을 활용한 직접적인 질문을 제안하세요

JSON 형태로 답변:
{{"temperature": "...", "main_issue": "...", "missing_perspective": "...", "next_action": "...", "intervention": "..."}}
"""
        
        try:
            import openai
            import json
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": "토론 분석 전문가로서 객관적으로 분석하세요."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # JSON 파싱 시도
            content = response.choices[0].message.content.strip()
            
            # JSON 부분만 추출 (때로는 추가 설명이 있을 수 있음)
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_content = content[json_start:json_end]
                result = json.loads(json_content)
            else:
                raise ValueError("JSON 형식이 아님")
            
            return result
            
        except Exception as e:
            self.logger.error(f"토론 상태 분석 실패: {e}")
            return {
                "temperature": "balanced",
                "main_issue": "일반적인 토론 진행",
                "missing_perspective": "새로운 관점 필요",
                "next_action": "continue_normal",
                "intervention": "계속 진행하겠습니다."
            }
    
    def generate_dynamic_manager_response(self, context: str, analysis: Dict[str, Any] = None, panel_agents: List = None) -> str:
        """동적 매니저 응답 생성 (Dynamic 모드용)"""
        if analysis is None:
            analysis = {"next_action": "continue_normal", "intervention": "계속 진행하겠습니다."}
        
        # 패널 이름들 추출 (구체적 호칭을 위해)
        panel_names = ""
        if panel_agents:
            panel_names = f"참여 패널: {', '.join([agent.name for agent in panel_agents])}"
        
        prompt = f"""
상황: {context}
토론 분석: {analysis}
{panel_names}

위 상황에서 **역동적이고 흥미진진한 토론**을 위한 진행자 발언을 생성해주세요.

다음 원칙을 따르세요:
1. **적극적이고 도전적인 진행**: 온화한 질문보다 직접적이고 도전적인 질문 선호
2. **구체적인 패널 대 패널 대립 유도**: "A 패널께서는 B 패널의 주장에 어떻게 반박하시겠습니까?"
3. **압박과 심화**: "방금 그 주장의 근거는 무엇입니까?", "반대 의견에 어떻게 대응하시겠습니까?"
4. **명확한 대립각 형성**: 패널들이 서로 직접 반박하도록 유도
5. **반복적이거나 뻔한 표현 금지**: "어떻게 생각하십니까?" 같은 평범한 질문 피하기
6. "[토론 진행자]"로 시작
7. 구체적인 패널 이름 사용 (모호한 표현 금지)

**라운드 타입별 톤:**
- **논쟁_유도**: "A 패널께서는 B 패널의 주장을 어떻게 반박하시겠습니까?" (도전적)
- **직접_대결**: "이제 A 패널과 B 패널께서 직접 맞서서 논쟁해 주십시오" (대결적)
- **새로운_관점**: "지금까지와는 완전히 다른 관점에서 접근해보겠습니다" (전환적)
- **근거_요구**: "구체적인 데이터와 근거를 제시해 주십시오. 추상적인 주장은 충분합니다" (압박적)

**발언 구조:**
1. 이전 내용 간략 정리 (1문장)
2. 왜 이런 방향이 필요한지 이유 제시 (1문장)  
3. 구체적인 패널에게 도전적 질문 (2문장)

**예시 (더 극적으로):**
- 논쟁 유도: "앞서 김철수 패널과 박미영 패널 사이에 명확한 견해 차이가 드러났습니다. 이제 직접적인 논쟁이 필요합니다. 김철수 패널께서는 박미영 패널의 교육 평등론이 현실을 무시한 이상론이라고 생각하지 않으십니까? 구체적으로 어떤 부분을 반박하시겠습니까?"
- 직접 대결: "지금이야말로 핵심 쟁점에 대해 정면승부를 할 때입니다. 김철수 패널과 박미영 패널께서 교육 정책에 대해 직접 맞서서 토론해 주십시오. 김철수 패널께서 먼저 박미영 패널의 주장을 정면으로 비판해 주시기 바랍니다."
"""
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": "전문적인 토론 진행자로서 상황에 맞는 적절한 개입을 하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            # "[토론 진행자]"가 없으면 추가
            if not result.startswith("[토론 진행자]"):
                result = f"[토론 진행자] {result}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"동적 응답 생성 실패: {e}")
            return "[토론 진행자] 계속 진행하겠습니다."
    
    def _get_max_tokens(self, task_type: str = "default") -> int:
        """작업 유형에 따른 max_tokens 계산"""
        base_tokens = self.config['ai']['max_tokens']
        multipliers = self.config['ai'].get('token_multipliers', {})
        multiplier = multipliers.get(task_type, 1.0)
        return int(base_tokens * multiplier)