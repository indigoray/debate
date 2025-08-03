"""
Output Capture - 콘솔 출력을 캡처하여 마크다운으로 저장하는 유틸리티
"""

import sys
import io
import re
import datetime
from typing import Optional, List
from colorama import Fore, Style
import os


class ConsoleCapture:
    """콘솔 출력을 캡처하고 마크다운으로 변환하는 클래스"""
    
    def __init__(self):
        self.captured_output = []
        self.original_stdout = sys.stdout
        self.capture_active = False
        
    def start_capture(self):
        """출력 캡처 시작"""
        self.captured_output = []
        self.capture_active = True
        # stdout을 오버라이드하여 출력을 캡처
        sys.stdout = OutputInterceptor(self.original_stdout, self.captured_output)
        
    def stop_capture(self):
        """출력 캡처 중지"""
        if self.capture_active:
            sys.stdout = self.original_stdout
            self.capture_active = False
    
    def get_captured_text(self) -> str:
        """캡처된 텍스트 반환"""
        return ''.join(self.captured_output)
    
    def save_to_markdown(self, topic: str, output_dir: str = "debate_logs") -> str:
        """캡처된 내용을 마크다운 파일로 저장"""
        # 출력 디렉토리 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 주제를 30자 이내로 요약
        title = self._summarize_topic(topic)
        
        # 파일명 생성 (날짜_시간_주제요약.md)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{title}.md"
        filepath = os.path.join(output_dir, filename)
        
        # 마크다운 내용 생성
        markdown_content = self._convert_to_markdown(topic, self.get_captured_text())
        
        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def _summarize_topic(self, topic: str) -> str:
        """토론 주제를 30자 이내로 요약"""
        # 특수문자 제거하고 파일명에 적합하게 변환
        clean_topic = re.sub(r'[<>:"/\\|?*]', '', topic)
        clean_topic = clean_topic.replace(' ', '_')
        
        # 30자 제한
        if len(clean_topic) > 30:
            clean_topic = clean_topic[:27] + "..."
        
        return clean_topic
    
    def _convert_to_markdown(self, topic: str, content: str) -> str:
        """캡처된 콘솔 출력을 마크다운 형식으로 변환"""
        # ANSI 색상 코드 제거
        clean_content = self._remove_ansi_codes(content)
        
        # 현재 시간
        now = datetime.datetime.now()
        formatted_time = now.strftime("%Y년 %m월 %d일 %H시 %M분")
        
        # 마크다운 헤더 생성
        markdown = f"""# AI 패널 토론: {topic}

**토론 시간**: {formatted_time}
**생성 도구**: Debate Agents v1.0

---

## 토론 내용

"""
        
        # 내용을 섹션별로 구분하여 마크다운 형식으로 변환
        sections = self._parse_debate_sections(clean_content)
        
        for section_title, section_content in sections:
            markdown += f"### {section_title}\n\n"
            # 발언 뒤에 빈줄 추가하는 간단한 후처리
            formatted_content = self._add_blank_lines_after_speeches(section_content)
            markdown += f"{formatted_content}\n\n"
        
        # 푸터 추가
        markdown += f"""---

*이 토론은 AI 패널 토론 시뮬레이션 도구 'Debate Agents'로 생성되었습니다.*
*생성 시간: {formatted_time}*
"""
        
        return markdown
    
    def _remove_ansi_codes(self, text: str) -> str:
        """ANSI 색상 코드 제거"""
        # ANSI escape sequences 제거
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _parse_debate_sections(self, content: str) -> List[tuple]:
        """토론 내용을 섹션별로 파싱"""
        sections = []
        lines = content.split('\n')
        
        current_section = "토론 시작"
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # 섹션 구분 키워드 감지
            if '=' * 60 in line and 'Debate Agents' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "프로그램 시작"
                continue
            elif '👥 생성된 전문가 패널' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "전문가 패널 구성"
                continue
            elif '📋 토론 진행 방식' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "토론 진행 방식"
                continue
            elif '📰 주제 브리핑' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "주제 브리핑"
                continue
            elif '👥 패널 소개' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "패널 소개"
                continue
            elif '🎭 토론 시작' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "토론 진행"
                continue
            elif '1단계: 초기 의견 발표' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "1단계: 초기 의견 발표"
                continue
            elif '2단계: 상호 토론' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "2단계: 상호 토론"
                continue
            elif '📝 토론 마무리' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "토론 마무리"
                continue
            elif '🎯 토론 결론' in line:
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = "토론 결론"
                continue
            
            # 내용 추가 (빈 줄이 아닌 경우에만)
            if line:
                current_content.append(line)
        
        # 마지막 섹션 추가
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def _add_blank_lines_after_speeches(self, content: str) -> str:
        """모든 발언 뒤에 빈줄 추가 및 토론 진행자만 볼드체로 변환"""
        lines = content.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # AI 생성 마크다운 헤딩을 일반 텍스트로 변환 (폰트 크기 문제 해결)
            if stripped_line.startswith('###'):
                # ### 1. 주요 합의점 → **1. 주요 합의점**
                heading_text = stripped_line.lstrip('#').strip()
                result_lines.append(f"**{heading_text}**")
            
            # 수평선(---)을 시각적 구분선으로 변환
            elif stripped_line == '---':
                result_lines.append('・・・・・・・・・・・・・・・・・・・・')
            
            # 토론 진행자 발언만 볼드체로 변환
            elif '[토론 진행자]' in stripped_line:
                # 기존 볼드체 제거 후 새로 적용
                clean_line = stripped_line.replace('**', '').replace('🎭 ', '')
                modified_line = f"🎭 **{clean_line}**"
                result_lines.append(modified_line)
            
            # 일반 패널 발언에서는 볼드체 제거
            elif stripped_line.startswith('[') and ']' in stripped_line:
                # 패널 발언에서 볼드체 제거
                clean_line = stripped_line.replace('**', '').replace('***', '')
                result_lines.append(clean_line)
            
            else:
                result_lines.append(line)
            
            # 발언인지 확인 ([패널명] 또는 토론 진행자)
            is_speech = (
                (stripped_line.startswith('[') and ']' in stripped_line) or  # 패널 발언
                ('토론 진행자' in stripped_line)  # 토론 진행자 발언
            )
            
            # 발언이고, 다음 줄이 있고, 다음 줄이 빈줄이 아니면 빈줄 추가
            if is_speech and i + 1 < len(lines) and lines[i + 1].strip() != '':
                result_lines.append('')
        
        return '\n'.join(result_lines)


class OutputInterceptor(io.StringIO):
    """stdout을 가로채서 출력을 캡처하면서 동시에 원본 출력도 유지하는 클래스"""
    
    def __init__(self, original_stdout, captured_output: List[str]):
        super().__init__()
        self.original_stdout = original_stdout
        self.captured_output = captured_output
        
    def write(self, text):
        # 원본 stdout에도 출력 (사용자가 실시간으로 볼 수 있도록)
        self.original_stdout.write(text)
        
        # 캡처된 출력에도 저장
        self.captured_output.append(text)
        
        return len(text)
    
    def flush(self):
        self.original_stdout.flush()