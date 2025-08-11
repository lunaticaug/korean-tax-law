#!/usr/bin/env python3
"""
HTML을 마크다운으로 정확히 변환
Version 2.0.0 (2025-01-11)
- select 태그에서 조문 목록 추출
- 본문 내용 파싱
"""

from bs4 import BeautifulSoup
import re
import os

class ProperHtmlToMarkdown:
    def __init__(self):
        self.articles = []
        self.markdown_lines = []
        
    def load_html(self, filepath='cache/01_html_cache.html'):
        """HTML 파일 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
        
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        print(f"✅ HTML 파일 로드 완료 ({len(self.html_content):,} bytes)")
        return True
    
    def extract_article_list(self):
        """select 태그에서 조문 목록 추출"""
        print("\n📋 조문 목록 추출 중...")
        
        # select#lsJoMove 찾기
        select = self.soup.find('select', {'id': 'lsJoMove'})
        if not select:
            print("❌ 조문 선택 목록을 찾을 수 없습니다")
            return False
        
        options = select.find_all('option')
        print(f"  {len(options)}개 옵션 발견")
        
        for option in options:
            text = option.text.strip()
            value = option.get('value', '')
            
            if text and '제' in text and '조' in text:
                # 조문 정보 파싱
                match = re.match(r'\s*제(\d+(?:의\d+)?)조\s*\(([^)]+)\)', text)
                if match:
                    self.articles.append({
                        'number': match.group(1),
                        'title': match.group(2).strip(),
                        'value': value,
                        'full_text': text
                    })
            elif text and ('장' in text or '절' in text or '관' in text):
                # 장/절/관 정보
                self.articles.append({
                    'type': 'section',
                    'text': text.strip(),
                    'value': value
                })
        
        print(f"✅ {len([a for a in self.articles if 'number' in a])}개 조문 추출")
        return True
    
    def extract_article_contents(self):
        """본문에서 조문 내용 추출"""
        print("\n📖 조문 내용 추출 중...")
        
        # 조문 내용이 있는 p 태그들 찾기
        article_paragraphs = self.soup.find_all('p', class_='pty1_p4')
        
        for p in article_paragraphs:
            # 조문 번호 찾기
            label = p.find('label')
            if label:
                article_text = label.text.strip()
                match = re.match(r'제(\d+(?:의\d+)?)조\(([^)]+)\)', article_text)
                if match:
                    article_num = match.group(1)
                    
                    # 해당 조문의 내용 추출
                    content = p.get_text(strip=True)
                    # 체크박스 텍스트 제거
                    content = re.sub(r'제\d+(?:의\d+)?조\([^)]+\)', '', content, count=1).strip()
                    
                    # 기존 articles 리스트에 내용 추가
                    for article in self.articles:
                        if article.get('number') == article_num:
                            article['content'] = content
                            break
        
        print(f"✅ 내용 추출 완료")
    
    def generate_markdown(self):
        """마크다운 생성"""
        print("\n📝 마크다운 생성 중...")
        
        # 제목
        self.markdown_lines.append("# 법인세법")
        self.markdown_lines.append("[시행 2025. 7. 1.] [법률 제20613호, 2024. 12. 31., 일부개정]\n")
        
        current_chapter = ""
        current_section = ""
        
        for item in self.articles:
            if item.get('type') == 'section':
                text = item['text']
                # 장/절/관 구분
                if '장' in text and not '절' in text:
                    self.markdown_lines.append(f"\n## {text}\n")
                    current_chapter = text
                elif '절' in text:
                    self.markdown_lines.append(f"\n### {text}\n")
                    current_section = text
                elif '관' in text:
                    self.markdown_lines.append(f"\n#### {text}\n")
            
            elif 'number' in item:
                # 조문
                article_num = item['number']
                article_title = item['title']
                content = item.get('content', '')
                
                self.markdown_lines.append(f"\n**제{article_num}조({article_title})**")
                
                if content:
                    # 항 번호 처리
                    content = self.format_content(content)
                    self.markdown_lines.append(content)
                else:
                    self.markdown_lines.append("*(내용 없음)*")
    
    def format_content(self, content):
        """조문 내용 포맷팅"""
        # 개정 이력 표시
        content = re.sub(r'\[([^\]]+)\]', r'`[\1]`', content)
        content = re.sub(r'<([^>]+)>', r'`<\1>`', content)
        
        # 항 번호 처리
        lines = []
        
        # ① ② 등의 원문자 처리
        parts = re.split(r'([①②③④⑤⑥⑦⑧⑨⑩])', content)
        for i, part in enumerate(parts):
            if re.match(r'[①②③④⑤⑥⑦⑧⑨⑩]', part):
                lines.append(f"\n{part}")
            elif part.strip():
                lines.append(part.strip())
        
        return ' '.join(lines)
    
    def save_markdown(self, filepath='cache/04_law_proper.md'):
        """마크다운 파일 저장"""
        markdown_content = '\n'.join(self.markdown_lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n✅ {filepath} 저장 완료")
        print(f"   파일 크기: {len(markdown_content):,} bytes")
        print(f"   조문 수: {len([a for a in self.articles if 'number' in a])}개")
        
        # 미리보기
        print("\n📄 마크다운 미리보기:")
        print("="*60)
        preview_lines = markdown_content.split('\n')[:30]
        for line in preview_lines:
            if line:
                print(line[:100])
        print("...")

def main():
    print("🚀 HTML → 마크다운 정확한 변환")
    print("="*60)
    
    converter = ProperHtmlToMarkdown()
    
    # HTML 로드
    if not converter.load_html('cache/01_html_cache.html'):
        return
    
    # 조문 목록 추출
    if not converter.extract_article_list():
        return
    
    # 조문 내용 추출
    converter.extract_article_contents()
    
    # 마크다운 생성
    converter.generate_markdown()
    
    # 저장
    converter.save_markdown()
    
    print("\n✅ 변환 완료!")

if __name__ == "__main__":
    main()