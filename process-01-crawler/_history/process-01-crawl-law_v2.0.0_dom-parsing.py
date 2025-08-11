#!/usr/bin/env python3
"""
법제처 법인세법 크롤링 - Selenium 4 자동 드라이버
Version 2.0.0 (2025-01-11)
- Selenium 4.6+ 내장 Selenium Manager 사용
- ChromeDriver 별도 설치 불필요
- iframe 처리 추가

Version 1.0.0 (2025-01-11)  
- 초기 버전 작성
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
import re
import os

class KoreanTaxLawCrawler:
    def __init__(self, headless=False):
        self.setup_driver(headless)
    
    def setup_driver(self, headless):
        """Chrome 드라이버 설정 - Selenium 4 자동 관리"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Selenium 4는 자동으로 ChromeDriver를 다운로드하고 관리
        print("📥 ChromeDriver 자동 설정 중...")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        print("✅ Chrome 브라우저 시작\n")
    
    def crawl_law(self, url):
        """법령 페이지 크롤링"""
        try:
            print(f"📖 페이지 접속: {url}")
            self.driver.get(url)
            
            # 페이지 로딩 대기
            print("⏳ 페이지 로딩 대기 (10초)...")
            time.sleep(10)
            
            # iframe 처리
            try:
                print("🔄 iframe 감지 중...")
                iframe = self.driver.find_element(By.ID, 'lawService')
                self.driver.switch_to.frame(iframe)
                print("✅ iframe 내부로 전환 완료")
                time.sleep(3)  # iframe 콘텐츠 로딩 대기
            except:
                print("⚠️ iframe 없음, 메인 페이지에서 계속")
            
            # 콘텐츠 추출
            return self.extract_law_data()
                
        except Exception as e:
            print(f"❌ 크롤링 중 오류: {e}")
            return None
        finally:
            self.driver.quit()
            print("\n브라우저를 종료했습니다.")
    
    def extract_law_data(self):
        """법령 데이터 추출 - 좌측 조문 리스트 DOM 활용"""
        print("\n🔍 법령 내용 추출 중...")
        
        law_data = {
            'title': '',
            'articles': [],
            'raw_text': '',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # 전체 텍스트 백업용으로 저장
            body = self.driver.find_element(By.TAG_NAME, 'body')
            law_data['raw_text'] = body.text
            
            # 제목 추출
            title_pattern = r'법인세법\s*\[시행[^\]]+\]'
            title_match = re.search(title_pattern, law_data['raw_text'])
            if title_match:
                law_data['title'] = title_match.group().strip()
                print(f"📌 제목: {law_data['title']}")
            
            # 좌측 조문 리스트 스캔
            print("  좌측 조문 목록 스캔 중...")
            try:
                # XPath로 좌측 분할영역의 조문 리스트 찾기
                article_list = self.driver.find_element(By.XPATH, '/html/body/form[2]/div[2]/div[1]/div[2]/ul/li/div')
                
                # 하위 모든 조문 링크 요소 찾기
                article_links = article_list.find_elements(By.TAG_NAME, 'a')
                print(f"  {len(article_links)}개 조문 링크 발견")
                
                for link in article_links:
                    text = link.text.strip()
                    if text and '제' in text and '조' in text:
                        # 조문 텍스트 파싱
                        # 제X조(제목) 또는 제X조 제목 형식 처리
                        match = re.match(r'제(\d+(?:의\d+)?)조[\s\(（]?([^)）\n]*)', text)
                        if match:
                            article_num = match.group(1)
                            article_title = match.group(2).strip()
                            
                            # 말줄임표가 있으면 제거하고 표시
                            if '...' in article_title:
                                article_title = article_title.replace('...', '').strip()
                                # 실제 전체 제목은 본문에서 가져와야 함을 표시
                                article_title += ' [축약됨]'
                            
                            law_data['articles'].append({
                                'number': article_num,
                                'title': article_title,
                                'href': link.get_attribute('href')  # 링크 저장
                            })
                
            except Exception as e:
                print(f"  XPath 조문 리스트 추출 실패: {e}")
                
                # 대체 방법: CSS 선택자로 시도
                try:
                    article_links = self.driver.find_elements(By.CSS_SELECTOR, 'div.left_menu a, ul.tree_menu a, a[onclick*="goJoView"]')
                    print(f"  CSS 선택자로 {len(article_links)}개 링크 발견")
                    
                    for link in article_links:
                        text = link.text.strip()
                        if text and '제' in text and '조' in text:
                            match = re.match(r'제(\d+(?:의\d+)?)조[\s\(（]?([^)）\n]*)', text)
                            if match:
                                law_data['articles'].append({
                                    'number': match.group(1),
                                    'title': match.group(2).strip()
                                })
                except:
                    pass
            
            # 조문이 없으면 텍스트에서 추출
            if not law_data['articles']:
                print("  DOM 추출 실패, 텍스트 기반 추출")
                main_start = law_data['raw_text'].find('제1조(목적)')
                if main_start >= 0:
                    main_text = law_data['raw_text'][main_start:]
                    article_pattern = r'제(\d+(?:의\d+)?)조\(([^)]+)\)'
                    articles = re.findall(article_pattern, main_text)
                    
                    seen = set()
                    for article_num, article_title in articles:
                        if article_num not in seen:
                            seen.add(article_num)
                            law_data['articles'].append({
                                'number': article_num,
                                'title': article_title.strip()
                            })
            
            # 조문 번호순 정렬
            law_data['articles'].sort(key=lambda x: (
                int(x['number'].split('의')[0]),
                int(x['number'].split('의')[1]) if '의' in x['number'] else 0
            ))
            
            print(f"✅ {len(law_data['articles'])}개 조문 발견")
            
        except Exception as e:
            print(f"❌ 데이터 추출 실패: {e}")
        
        return law_data
    
    def save_results(self, data):
        """결과 저장 - 캐시 파일 형식"""
        if not data:
            print("저장할 데이터가 없습니다.")
            return
        
        # 캐시 디렉토리 생성
        os.makedirs('cache', exist_ok=True)
        
        # JSON 캐시 파일
        json_file = 'cache/01_law_data_cache.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {json_file} 저장")
        
        # 텍스트 캐시 파일
        txt_file = 'cache/01_law_text_cache.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(data.get('raw_text', ''))
        print(f"✅ {txt_file} 저장")
        
        # 요약 리포트
        self.print_summary(data)
    
    def print_summary(self, data):
        """크롤링 결과 요약"""
        print("\n" + "="*60)
        print("📊 크롤링 결과 요약")
        print("="*60)
        print(f"제목: {data.get('title', '미확인')}")
        print(f"조문 수: {len(data.get('articles', []))}개")
        print(f"텍스트 길이: {len(data.get('raw_text', '')):,} 자")
        print(f"크롤링 시간: {data.get('timestamp', '')}")
        
        if data.get('articles'):
            print(f"\n처음 5개 조문:")
            for article in data['articles'][:5]:
                print(f"  - 제{article['number']}조 ({article['title']})")

def main():
    print("🚀 법인세법 크롤링 시작")
    print("="*60)
    
    # 크롤러 초기화 (headless=False로 브라우저 표시)
    crawler = KoreanTaxLawCrawler(headless=False)
    
    # 법인세법 URL
    url = "https://www.law.go.kr/법령/법인세법"
    
    # 크롤링 실행
    result = crawler.crawl_law(url)
    
    if result:
        crawler.save_results(result)
        print("\n✅ 크롤링 완료!")
    else:
        print("\n❌ 크롤링 실패")
        print("대안: 법제처 사이트에서 HWP/PDF 직접 다운로드")

if __name__ == "__main__":
    main()