#!/usr/bin/env python3
"""
법제처 법인세법 인터랙티브 브라우저 크롤링
Version 1.0.0 (2025-01-11)
- 브라우저를 열어두고 사용자가 직접 페이지 확인 후 크롤링
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import re

class InteractiveBrowserScraper:
    def __init__(self):
        self.setup_driver()
        self.data = None
    
    def setup_driver(self):
        """Chrome 드라이버 설정 (화면 표시)"""
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option('detach', True)  # 스크립트 종료 후에도 브라우저 유지
        
        # service = Service(ChromeDriverManager().install())
        # self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome 브라우저가 열렸습니다.")
    
    def open_law_page(self, url):
        """법령 페이지 열기"""
        print(f"\n📖 페이지 로딩 중: {url}")
        self.driver.get(url)
        print("⏳ 페이지가 완전히 로드될 때까지 기다려주세요...")
        
    def wait_for_user_confirmation(self):
        """사용자 확인 대기"""
        print("\n" + "="*60)
        print("👀 브라우저에서 페이지를 확인하세요:")
        print("1. 법령 내용이 모두 표시되었는지 확인")
        print("2. 필요시 스크롤하여 전체 내용 로드")
        print("3. 팝업이 있다면 닫기")
        print("="*60)
        
        while True:
            user_input = input("\n준비되셨나요? (y: 크롤링 시작, n: 취소, r: 페이지 새로고침): ").lower()
            if user_input == 'y':
                return True
            elif user_input == 'n':
                return False
            elif user_input == 'r':
                print("페이지를 새로고침합니다...")
                self.driver.refresh()
                time.sleep(3)
            else:
                print("y, n, 또는 r을 입력해주세요.")
    
    def extract_content(self):
        """현재 페이지에서 법령 내용 추출"""
        print("\n🔍 법령 내용을 추출하는 중...")
        
        # 여러 방법으로 콘텐츠 추출 시도
        extraction_methods = [
            self.extract_by_id,
            self.extract_by_class,
            self.extract_by_xpath,
            self.extract_full_page
        ]
        
        for method in extraction_methods:
            result = method()
            if result and (result.get('articles') or result.get('raw_text')):
                print(f"✅ {method.__name__} 방법으로 추출 성공!")
                self.data = result
                return True
        
        print("❌ 콘텐츠 추출 실패")
        return False
    
    def extract_by_id(self):
        """ID로 추출"""
        try:
            for elem_id in ['conScroll', 'lawmunView', 'content', 'lawContent']:
                try:
                    element = self.driver.find_element(By.ID, elem_id)
                    if element:
                        return self.parse_element(element)
                except:
                    continue
        except:
            pass
        return None
    
    def extract_by_class(self):
        """Class로 추출"""
        try:
            for class_name in ['lawcon', 'law_contents', 'content_body', 'law-content']:
                try:
                    element = self.driver.find_element(By.CLASS_NAME, class_name)
                    if element:
                        return self.parse_element(element)
                except:
                    continue
        except:
            pass
        return None
    
    def extract_by_xpath(self):
        """XPath로 추출"""
        try:
            xpaths = [
                '//div[contains(@class, "law")]',
                '//div[contains(@id, "law")]',
                '//article',
                '//main'
            ]
            for xpath in xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element:
                        return self.parse_element(element)
                except:
                    continue
        except:
            pass
        return None
    
    def extract_full_page(self):
        """전체 페이지 텍스트 추출"""
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            return self.parse_element(body)
        except:
            return None
    
    def parse_element(self, element):
        """요소에서 법령 데이터 파싱"""
        law_data = {
            'title': '',
            'articles': [],
            'raw_text': '',
            'html': ''
        }
        
        # HTML과 텍스트 저장
        law_data['html'] = element.get_attribute('innerHTML')
        law_data['raw_text'] = element.text
        
        # 제목 추출
        title_pattern = r'법인세법\s*(?:\[.*?\])?'
        title_match = re.search(title_pattern, law_data['raw_text'])
        if title_match:
            law_data['title'] = title_match.group()
        
        # 조문 추출
        article_pattern = r'제(\d+(?:의\d+)?)조[\s\(（](.*?)[\)）]?\s*(.*?)(?=제\d+(?:의\d+)?조|$)'
        articles = re.findall(article_pattern, law_data['raw_text'], re.DOTALL)
        
        for article_num, article_title, article_content in articles:
            law_data['articles'].append({
                'number': article_num,
                'title': article_title.strip(),
                'content': article_content.strip()[:500]  # 처음 500자만 저장
            })
        
        return law_data
    
    def save_results(self):
        """결과 저장"""
        if not self.data:
            print("저장할 데이터가 없습니다.")
            return
        
        # JSON 저장
        with open('tax_law_interactive.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print("✅ tax_law_interactive.json 저장 완료")
        
        # 원본 텍스트 저장
        with open('tax_law_raw.txt', 'w', encoding='utf-8') as f:
            f.write(self.data.get('raw_text', ''))
        print("✅ tax_law_raw.txt 저장 완료")
        
        # HTML 저장
        with open('tax_law.html', 'w', encoding='utf-8') as f:
            f.write(self.data.get('html', ''))
        print("✅ tax_law.html 저장 완료")
        
        # 요약 출력
        print(f"\n📊 추출 결과:")
        print(f"- 제목: {self.data.get('title', '미확인')}")
        print(f"- 추출된 조문 수: {len(self.data.get('articles', []))}")
        print(f"- 전체 텍스트 길이: {len(self.data.get('raw_text', ''))} 자")
    
    def keep_browser_open(self):
        """브라우저 유지 옵션"""
        print("\n" + "="*60)
        print("브라우저 옵션:")
        print("1. 브라우저 유지 (수동으로 닫기)")
        print("2. 브라우저 닫기")
        print("="*60)
        
        choice = input("선택 (1 또는 2): ")
        if choice == '2':
            self.driver.quit()
            print("브라우저를 닫았습니다.")
        else:
            print("브라우저가 열려있습니다. 수동으로 닫아주세요.")

def main():
    print("🚀 인터랙티브 브라우저 크롤러 시작")
    print("="*60)
    
    scraper = InteractiveBrowserScraper()
    
    # URL 입력 또는 기본값 사용
    url = input("\n법령 URL 입력 (Enter: 법인세법): ").strip()
    if not url:
        url = "https://www.law.go.kr/법령/법인세법"
    
    # 페이지 열기
    scraper.open_law_page(url)
    
    # 사용자 확인 대기
    if scraper.wait_for_user_confirmation():
        # 콘텐츠 추출
        if scraper.extract_content():
            scraper.save_results()
        else:
            print("\n추출 실패. 다음을 시도해보세요:")
            print("1. 페이지가 완전히 로드되었는지 확인")
            print("2. 다른 법령 사이트 사용")
            print("3. PDF/HWP 다운로드 옵션 확인")
    else:
        print("크롤링이 취소되었습니다.")
    
    # 브라우저 유지 여부 선택
    scraper.keep_browser_open()

if __name__ == "__main__":
    main()