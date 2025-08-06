"""
PanelGenerator - 전문가 페르소나 생성 및 패널 에이전트 생성 클래스
"""

import logging
from typing import Dict, Any, List
from colorama import Fore, Style

from .panel_agent import PanelAgent
from ..utils.streaming import stream_openai_response, get_typing_speed


class PanelGenerator:
    """전문가 페르소나 생성 및 패널 에이전트 생성을 담당하는 클래스"""
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        PanelGenerator 초기화
        
        Args:
            config: 설정 딕셔너리
            api_key: OpenAI API 키
        """
        self.config = config
        self.api_key = api_key
        self.logger = logging.getLogger('debate_agents.panel_generator')
    
    def _create_expert_personas(self, topic: str, panel_size: int, system_prompt: str) -> List[Dict[str, str]]:
        """주제에 맞는 전문가 페르소나 생성"""
        persona_prompt = f"""
# 페르소나 생성 지시문

## 토론 주제
{topic}

## 미션
당신은 최고의 토론 프로그램을 만드는 PD입니다. 위 토론 주제에 대해 가장 흥미롭고, 치열하며, 깊이 있는 토론을 만들어낼 수 있는 {panel_size}명의 입체적인 전문가 패널을 캐스팅해주세요.

## 패널 구성 원칙
1.  **선명한 대립각**: 패널들은 단순히 다른 의견을 가진 것이 아니라, 세계관이나 신념 수준에서 뚜렷하게 대립해야 합니다. 찬성과 반대 입장을 명확히 나누고, 그 안에서도 결이 다른 관점을 제시해주세요.
2.  **입체적 캐릭터**: 단순한 '전문가'가 아닌, 개인적인 신념, 독특한 경험, 개성적인 말투를 가진 한 명의 '인물'을 만들어주세요.
3.  **예측 불가능성**: 모든 패널이 예측 가능한 결론("결국은 균형이 중요합니다")으로 쉽게 수렴하지 않도록, 자신의 주장을 끝까지 고수하거나, 예상치 못한 논리를 펼치는 캐릭터를 포함해주세요.

## 🚨 중요: 관점과 토론스타일 구분 원칙
- **관점**에는 주장, 입장, 논리만 포함하고 말투나 언어스타일은 절대 포함하지 마세요
- **토론스타일**에는 말투, 언어패턴, 표현방식만 포함하고 주장내용은 절대 포함하지 마세요
- 두 항목을 명확히 분리해서 작성하는 것이 핵심입니다

## 🎭 토론스타일 작성 가이드라인
- 구체적인 예시 문구("이 점에 주목해야 합니다", "철학적 맥락에서 보면" 등)를 직접 제시하지 마세요
- 대신 말하는 방식의 특징을 묘사하세요 (예: "학문적이고 신중한 어조", "열정적이고 직설적인 표현", "차분하고 분석적인 접근")
- 각 전문가만의 독특한 언어적 개성을 만들어주세요
- 상투적이거나 뻔한 표현 방식은 피하고 개성 있는 말투를 창조하세요

## 생성 형식 (아래 형식을 반드시 준수해주세요)
1.  전문가 이름: [이름]
    직업과 소속: [구체적인 직업과 소속]
    배경: [그의 주장을 뒷받침하는 구체적인 개인적 경험, 연구 이력, 저서 등 (예: 20년간 성별 뇌 구조 차이를 연구해온 권위자. 저서 '남성의 뇌, 여성의 뇌'가 베스트셀러가 됨)]
    관점: [토론 주제에 대한 핵심 주장, 논리, 및 입장만 기술. 언어 스타일은 포함하지 말 것 (예: "뇌 구조의 차이가 역할 분담의 핵심 근거라고 주장. fMRI 연구 데이터를 활용하며, 과학적 증거를 중시")]
    토론스타일: [말투와 언어 패턴의 특징만 기술. 주장 내용은 포함하지 말 것. 
    ※ 주의: 예시로 제시된 구체적 표현("연구에 따르면", "객관적 수치로" 등)을 그대로 반복하지 말고, 그 스타일의 특징(논리적, 감정적, 열정적, 신중한 등)과 말하는 방식의 패턴을 자연스럽게 묘사하세요]

2.  전문가 이름: ... (반복)

(총 {panel_size}명)
"""
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            print(f"\n{Fore.YELLOW}🤖 전문가 패널을 생성하고 있습니다...{Style.RESET_ALL}")
            
            # 타이핑 속도 가져오기
            typing_speed = get_typing_speed(self.config)
            
            # 토큰 계산 (AI 안내용 vs API 실제용)
            base_tokens = self._get_max_tokens('persona_generation')
            announced_tokens = base_tokens  # AI에게 알려줄 토큰 수
            actual_max_tokens = int(base_tokens * 1.2)  # API에 실제 전송할 토큰 수 (1.2배 여유분)
            
            enhanced_prompt = self._enhance_prompt_with_token_info(persona_prompt, announced_tokens)
            
            if typing_speed > 0:
                # 스트리밍으로 페르소나 생성 과정 출력
                result = stream_openai_response(
                    client=client,
                    model=self.config['ai']['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    max_tokens=actual_max_tokens,
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
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    max_tokens=actual_max_tokens,
                    temperature=self.config['ai']['temperature']
                )
                result = response.choices[0].message.content
                print(f"{Fore.CYAN}{result}{Style.RESET_ALL}")
            
            # 디버깅을 위해 AI 응답 로그 출력
            self.logger.info(f"AI 페르소나 생성 응답: {result}")
            
            # 응답 파싱하여 전문가 정보 추출
            personas = self._parse_expert_personas(result, panel_size)
            self.logger.info(f"{len(personas)}명의 전문가 페르소나 생성 완료")
            
            return personas
            
        except Exception as e:
            self.logger.error(f"전문가 페르소나 생성 실패: {e}")
            self.logger.info("기본 페르소나를 사용합니다.")
            default_personas = self._get_default_personas()
            self.logger.info(f"기본 페르소나 {len(default_personas)}명 로드 완료")
            return default_personas[:panel_size]
    
    def create_panel_agents(self, topic: str, panel_size: int, system_prompt: str) -> List[PanelAgent]:
        """주제부터 시작해서 페르소나 생성과 패널 에이전트 생성을 한 번에 처리"""
        # 1. 페르소나 생성
        personas = self._create_expert_personas(topic, panel_size, system_prompt)
        
        # 2. 패널 에이전트 생성
        panel_agents = []
        
        for i, persona in enumerate(personas, 1):
            agent = PanelAgent(
                name=persona['name'],
                expertise=persona['expertise'],
                background=persona['background'],
                perspective=persona['perspective'],
                debate_style=persona['debate_style'],
                config=self.config,
                api_key=self.api_key
            )
            panel_agents.append(agent)
        
        self.logger.info(f"{len(panel_agents)}명의 패널 에이전트 생성 완료")
        return panel_agents
    
    def _get_max_tokens(self, task_type: str = "default") -> int:
        """작업 유형에 따른 max_tokens 계산"""
        base_tokens = self.config['ai']['max_tokens']
        multipliers = self.config['ai'].get('token_multipliers', {})
        multiplier = multipliers.get(task_type, 1.0)
        return int(base_tokens * multiplier)
    
    def _enhance_prompt_with_token_info(self, prompt: str, announced_tokens: int) -> str:
        """프롬프트에 토큰 제한 정보 추가"""
        return f"""
{prompt}

**중요 지침**: 이 응답은 최대 {announced_tokens}토큰으로 제한됩니다. 반드시 이 범위 내에서 완결된 페르소나 정보를 작성하세요. 중간에 잘리지 않도록 각 전문가의 정보를 완전히 작성하고, 마지막 항목까지 완전히 끝내세요.
"""
    
    def _parse_expert_personas(self, response: str, panel_size: int) -> List[Dict[str, str]]:
        """AI 응답에서 전문가 정보 파싱 (개선된 버전)"""
        personas = []
        
        # 디버깅을 위한 로그
        self.logger.info(f"파싱 시작. 응답 길이: {len(response)}")
        
        try:
            # 다양한 형식에 대응하는 유연한 파싱
            lines = response.split('\n')
            current_expert = {}
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 전문가 이름 찾기 (다양한 형식 지원)
                if '전문가 이름' in line and ':' in line:
                    # 이전 전문가 정보가 있으면 저장
                    if current_expert and 'name' in current_expert:
                        self._finalize_expert(current_expert)
                        personas.append(current_expert)
                    
                    # 새 전문가 시작
                    current_expert = {}
                    name_part = line.split(':', 1)[-1].strip()
                    name_part = name_part.replace('**', '').replace('[', '').replace(']', '').strip()
                    current_expert['name'] = name_part.replace(' ', '')
                
                # 전문분야 정보
                elif '직업과 소속' in line and ':' in line:
                    expertise_part = line.split(':', 1)[-1].strip()
                    expertise_part = expertise_part.replace('**', '').replace('[', '').replace(']', '').strip()
                    current_expert['expertise'] = expertise_part
                
                # 배경
                elif '배경' in line and ':' in line:
                    background_part = line.split(':', 1)[-1].strip()
                    background_part = background_part.replace('**', '').replace('[', '').replace(']', '').strip()
                    current_expert['background'] = background_part
                
                # 관점
                elif '관점' in line and ':' in line:
                    perspective_part = line.split(':', 1)[-1].strip()
                    perspective_part = perspective_part.replace('**', '').replace('[', '').replace(']', '').strip()
                    current_expert['perspective'] = perspective_part
                
                # 토론 스타일
                elif '토론스타일' in line and ':' in line:
                    debate_style_part = line.split(':', 1)[-1].strip()
                    debate_style_part = debate_style_part.replace('**', '').replace('[', '').replace(']', '').strip()
                    current_expert['debate_style'] = debate_style_part
            
            # 마지막 전문가 정보 저장
            if current_expert and 'name' in current_expert:
                self._finalize_expert(current_expert)
                personas.append(current_expert)
            
            self.logger.info(f"파싱 완료. {len(personas)}명의 전문가 추출됨")
            
            # 최소한의 전문가가 없으면 기본 페르소나 사용
            if len(personas) == 0:
                self.logger.warning("파싱된 전문가가 없음. 기본 페르소나 사용")
                return self._get_default_personas()[:panel_size]
            
            return personas[:panel_size]
            
        except Exception as e:
            self.logger.error(f"파싱 중 오류 발생: {e}")
            return self._get_default_personas()[:panel_size]
    
    def _finalize_expert(self, expert: Dict[str, str]) -> None:
        """전문가 정보 최종 처리"""
        expert.setdefault('expertise', '전문가')
        expert.setdefault('background', '해당 분야의 경험이 풍부한 전문가')
        expert.setdefault('perspective', '균형잡힌 관점으로 토론에 참여')
        expert.setdefault('debate_style', '논리적이고 차분한 어조로 근거를 바탕으로 의견을 제시하는 스타일')
    
    def _get_default_personas(self) -> List[Dict[str, str]]:
        """기본 전문가 페르소나"""
        return [
            {
                "name": "김철수",
                "expertise": "신경과학자, 서울대 의대 교수",
                "background": "15년간 성별 뇌 구조 차이 연구, 국제학술지 100편 이상 발표, 저서 '남성의 뇌, 여성의 뇌' 베스트셀러",
                "perspective": "남녀 뇌의 구조적 차이는 과학적 사실이며, 이는 교육 방식에 반영되어야 한다는 입장. fMRI, DTI 등 뇌영상 연구 데이터를 근거로 논증한다.",
                "debate_style": "논리적이고 데이터 중심적인 스타일. '연구에 따르면...', '통계적으로 유의한...' 등의 학술적 표현을 자주 사용하며, 차분하고 객관적인 어조로 과학적 근거를 제시한다."
            },
            {
                "name": "박미영",
                "expertise": "교육심리학자, 이화여대 교육학과 교수",
                "background": "20년간 성별 교육 격차 연구, UNESCO 교육 평등 자문위원, 여성 교육 정책 전문가",
                "perspective": "성별 차이보다 개인차가 크며, 성별 분리 교육은 고정관념을 강화한다고 주장. 교육현장 데이터와 국제비교연구를 통해 반박한다.",
                "debate_style": "따뜻하면서도 논리적인 설득형 스타일. '제가 만난 학생들을 보면...', '실제 교육현장에서는...' 등 현장 사례를 자주 인용하며, 공감과 데이터를 함께 활용하는 균형잡힌 어조를 사용한다."
            },
            {
                "name": "이준호",
                "expertise": "진화심리학자, 연세대 심리학과 교수",
                "background": "진화적 관점에서 성별 차이 연구 10년, 하버드 방문연구원 경력, 다수의 국제 공동연구 참여",
                "perspective": "진화적 관점에서 성별 차이는 적응적 의미가 있으며, 교육에서도 고려되어야 한다고 본다. 진화심리학 이론과 문화간 비교연구를 활용한다.",
                "debate_style": "철학적이고 거시적인 관점의 사색형 스타일. '인류 진화사를 보면...', '생존과 번식의 관점에서...' 등 넓은 시각의 표현을 사용하며, 깊이 있고 성찰적인 어조로 발언한다."
            },
            {
                "name": "최소연",
                "expertise": "젠더학자, 성공회대 민주자유전공 교수",
                "background": "젠더 이론과 교육 불평등 연구 12년, 시민단체 활동 경력, 성평등 정책 자문",
                "perspective": "생물학적 결정론은 위험하며, 성별 분리 교육은 사회적 차별을 재생산한다는 관점. 젠더 이론과 사회구조적 분석, 역사적 사례를 활용한다.",
                "debate_style": "비판적이고 열정적인 성찰형 스타일. '그것은 전형적인 생물학적 환원주의입니다', '우리는 질문해야 합니다' 등 기존 관념에 도전하는 표현을 사용하며, 강한 확신과 열정적인 어조로 의견을 제시한다."
            }
        ]