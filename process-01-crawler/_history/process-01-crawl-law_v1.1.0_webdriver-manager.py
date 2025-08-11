#!/usr/bin/env python3
"""
법제처 법인세법 Selenium 크롤링 스크립트
Version 1.0.0 (2025-01-11)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service  # Selenium 4는 Service 없이도 작동
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager  # Selenium 4는 자체 드라이버 관리
import json
import time
import re

class SeleniumTaxLawScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
    
    def setup_driver(self, headless):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Selenium 4는 자동으로 ChromeDriver를 다운로드하고 관리
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def scrape_law(self, url):
        """법령 페이지 크롤링"""
        try:
            print(f"페이지 접속 중: {url}")
            self.driver.get(url)
            time.sleep(3)  # 페이지 로딩 대기
            
            # 법령 내용이 로드될 때까지 대기
            try:
                # 여러 가능한 선택자 시도
                content_selectors = [
                    (By.ID, 'conScroll'),
                    (By.CLASS_NAME, 'lawcon'),
                    (By.ID, 'lawmunView'),
                    (By.CLASS_NAME, 'law_contents'),
                    (By.XPATH, '//div[contains(@class, "law")]')
                ]
                
                content_element = None
                for by, selector in content_selectors:
                    try:
                        content_element = self.wait.until(
                            EC.presence_of_element_located((by, selector))
                        )
                        if content_element:
                            print(f"콘텐츠 요소 발견: {selector}")
                            break
                    except:
                        continue
                
                if not content_element:
                    # iframe 확인
                    iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                    if iframes:
                        print("iframe 발견, 프레임 전환 시도")
                        self.driver.switch_to.frame(iframes[0])
                        content_element = self.driver.find_element(By.TAG_NAME, 'body')
                
                if content_element:
                    return self.extract_law_data(content_element)
                else:
                    print("법령 내용을 찾을 수 없습니다.")
                    return None
                    
            except Exception as e:
                print(f"요소 대기 중 오류: {e}")
                return None
                
        except Exception as e:
            print(f"크롤링 중 오류: {e}")
            return None
        finally:
            self.driver.quit()
    
    def extract_law_data(self, content_element):
        """법령 데이터 추출"""
        law_data = {
            'title': '',
            'articles': [],
            'raw_text': ''
        }
        
        # 전체 텍스트 추출
        raw_text = content_element.text
        law_data['raw_text'] = raw_text
        
        # 제목 추출
        title_pattern = r'법인세법\s*\[.*?\]'
        title_match = re.search(title_pattern, raw_text)
        if title_match:
            law_data['title'] = title_match.group()
        
        # 조문 추출 (제X조 패턴)
        article_pattern = r'제\d+조(?:의\d+)?[\s\(（].*?[\)）]?.*?(?=제\d+조|$)'
        articles = re.findall(article_pattern, raw_text, re.DOTALL)
        
        for article in articles:
            article_num_match = re.match(r'제(\d+(?:의\d+)?)조', article)
            if article_num_match:
                law_data['articles'].append({
                    'number': article_num_match.group(1),
                    'text': article.strip()
                })
        
        print(f"추출된 조문 수: {len(law_data['articles'])}")
        return law_data
    
    def save_to_file(self, data, filename="tax_law_selenium.json"):
        """데이터 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"데이터가 {filename}에 저장되었습니다.")
        
        # 텍스트 파일로도 저장
        txt_filename = filename.replace('.json', '.txt')
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(data.get('raw_text', ''))
        print(f"원본 텍스트가 {txt_filename}에 저장되었습니다.")

def main():
    print("Selenium을 사용한 법인세법 크롤링을 시작합니다...")
    print("Chrome 드라이버를 자동으로 다운로드합니다...")
    
    scraper = SeleniumTaxLawScraper(headless=False)  # 디버깅을 위해 headless=False
    url = "https://www.law.go.kr/법령/법인세법"
    
    result = scraper.scrape_law(url)
    
    if result:
        if result.get('articles'):
            print(f"\n성공: {len(result['articles'])}개의 조문을 추출했습니다.")
            scraper.save_to_file(result)
        else:
            print("\n조문 추출에 실패했지만 원본 텍스트는 저장합니다.")
            scraper.save_to_file(result)
    else:
        print("\n크롤링 실패")
        print("\n추가 대안:")
        print("1. 법제처에서 HWP/PDF 파일 직접 다운로드")
        print("2. 국가법령정보공동활용 OpenAPI 신청 (https://open.law.go.kr)")

if __name__ == "__main__":
    main()