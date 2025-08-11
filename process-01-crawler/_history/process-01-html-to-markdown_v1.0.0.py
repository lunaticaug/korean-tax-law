#!/usr/bin/env python3
"""
HTML을 마크다운으로 변환
Version 1.0.0 (2025-01-11)
- BeautifulSoup으로 HTML 파싱
- 법령 구조에 맞는 마크다운 생성
"""

from bs4 import BeautifulSoup
import re
import os

class HtmlToMarkdownConverter:
    def __init__(self):
        self.markdown = []
        
    def load_html(self, filepath='cache/01_html_cache.html'):
        """HTML 파일 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
        
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        print(f"✅ HTML 파일 로드 완료 ({len(self.html_content):,} bytes)")
        return True
    
    def convert_to_markdown(self):
        """HTML을 마크다운으로 변환"""
        print("\n📝 마크다운 변환 중...")
        
        # 제목 추출
        title = self.extract_title()
        if title:
            self.markdown.append(f"# {title}\n")
        
        # 본문 내용 추출
        content_area = self.find_content_area()
        if content_area:
            self.parse_content(content_area)
        else:
            # 전체 텍스트에서 추출
            self.parse_text_content()
        
        return '\n'.join(self.markdown)
    
    def extract_title(self):
        """제목 추출"""
        # 여러 방법으로 제목 찾기
        title_elements = [
            self.soup.find('h1'),
            self.soup.find('h2'),
            self.soup.find('title'),
            self.soup.find('div', class_='law_title')
        ]
        
        for elem in title_elements:
            if elem and elem.text:
                title = elem.text.strip()
                if '법인세법' in title:
                    return title
        
        # 텍스트에서 찾기
        text = self.soup.get_text()
        match = re.search(r'법인세법\s*\[시행[^\]]+\]', text)
        if match:
            return match.group()
        
        return "법인세법"
    
    def find_content_area(self):
        """본문 영역 찾기"""
        # 가능한 본문 컨테이너
        selectors = [
            {'class': 'lawcon'},
            {'class': 'law_contents'},
            {'id': 'conScroll'},
            {'id': 'lawmunView'}
        ]
        
        for selector in selectors:
            content = self.soup.find('div', selector)
            if content:
                print(f"  본문 영역 발견: {selector}")
                return content
        
        return None
    
    def parse_content(self, content_elem):
        """DOM 요소에서 마크다운 생성"""
        # 장/절 구조
        chapters = content_elem.find_all(['h3', 'h4', 'div'], class_=re.compile('chapter|section|장|절'))
        for chapter in chapters:
            text = chapter.get_text(strip=True)
            if text:
                if '장' in text and '제' in text:
                    self.markdown.append(f"\n## {text}\n")
                elif '절' in text:
                    self.markdown.append(f"\n### {text}\n")
        
        # 조문 추출
        articles = content_elem.find_all(text=re.compile(r'제\d+(?:의\d+)?조'))
        
        for article in articles:
            # 조문 전체 텍스트 가져오기
            parent = article.parent
            if parent:
                article_text = parent.get_text(strip=True)
                self.format_article(article_text)
    
    def parse_text_content(self):
        """텍스트 기반 파싱"""
        text = self.soup.get_text()
        
        # 본문 시작 찾기
        main_start = text.find('제1조(목적)')
        if main_start < 0:
            print("  ⚠️ 본문 시작점을 찾을 수 없습니다")
            self.markdown.append(text)  # 원본 텍스트 그대로
            return
        
        main_text = text[main_start:]
        
        # 장/절 처리
        lines = main_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 장 표시
            if re.match(r'제\d+장', line):
                self.markdown.append(f"\n## {line}\n")
            # 절 표시  
            elif re.match(r'제\d+절', line):
                self.markdown.append(f"\n### {line}\n")
            # 조문
            elif re.match(r'제\d+(?:의\d+)?조', line):
                self.format_article(line)
            # 일반 텍스트
            else:
                if len(line) > 2:  # 너무 짧은 줄 제외
                    self.markdown.append(line)
    
    def format_article(self, text):
        """조문 포맷팅"""
        # 제X조(제목) 형식
        match = re.match(r'(제\d+(?:의\d+)?조)\s*\(([^)]+)\)\s*(.*)', text, re.DOTALL)
        if match:
            article_num = match.group(1)
            article_title = match.group(2)
            article_content = match.group(3).strip()
            
            self.markdown.append(f"\n#### {article_num}({article_title})\n")
            
            if article_content:
                # 항 번호 처리 (①, ②, ... 또는 1., 2., ...)
                content = re.sub(r'([①②③④⑤⑥⑦⑧⑨⑩])', r'\n\1', article_content)
                content = re.sub(r'(\d+\.)', r'\n\1', content)
                
                # 목록 형식으로 변환
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if re.match(r'[①②③④⑤⑥⑦⑧⑨⑩]', line):
                        self.markdown.append(f"- {line}")
                    elif re.match(r'\d+\.', line):
                        self.markdown.append(f"  {line}")
                    elif line:
                        self.markdown.append(line)
        else:
            self.markdown.append(f"\n#### {text}\n")
    
    def save_markdown(self, filepath='cache/03_law_markdown.md'):
        """마크다운 파일 저장"""
        markdown_content = '\n'.join(self.markdown)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ {filepath} 저장 완료")
        print(f"   파일 크기: {len(markdown_content):,} bytes")
        print(f"   라인 수: {len(self.markdown):,} lines")
        
        # 미리보기
        print("\n📄 마크다운 미리보기 (처음 500자):")
        print("-"*50)
        print(markdown_content[:500])
        if len(markdown_content) > 500:
            print("...")

def main():
    print("🚀 HTML → 마크다운 변환 시작")
    print("="*60)
    
    converter = HtmlToMarkdownConverter()
    
    # HTML 로드
    if not converter.load_html('cache/01_html_cache.html'):
        print("❌ HTML 파일 로드 실패")
        return
    
    # 변환
    converter.convert_to_markdown()
    
    # 저장
    converter.save_markdown()
    
    print("\n✅ 변환 완료!")
    
    # 추가 옵션
    print("\n💡 팁: pandoc을 사용하면 더 정교한 변환 가능:")
    print("   brew install pandoc")
    print("   pandoc -f html -t markdown cache/01_html_cache.html -o output.md")

if __name__ == "__main__":
    main()