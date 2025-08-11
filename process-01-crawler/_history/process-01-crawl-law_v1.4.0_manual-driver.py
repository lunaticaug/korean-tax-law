#!/usr/bin/env python3
"""
법제처 법인세법 크롤링 - 공식 ChromeDriver 사용
Version 1.0.0 (2025-01-11)

ChromeDriver 다운로드:
1. Chrome 버전 확인: chrome://version/
2. 공식 사이트: https://chromedriver.chromium.org/downloads
3. 또는 새 사이트: https://googlechromelabs.github.io/chrome-for-testing/
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import time
import re
import os
import platform
import subprocess

class OfficialChromeDriverScraper:
    def __init__(self, driver_path=None):
        """
        driver_path: ChromeDriver 실행 파일 경로
        None인 경우 자동으로 찾기 시도
        """
        self.driver_path = driver_path or self.find_chromedriver()
        self.setup_driver()
    
    def find_chromedriver(self):
        """시스템에서 ChromeDriver 찾기"""
        possible_paths = []
        
        # 현재 디렉토리
        possible_paths.append('./chromedriver')
        
        # 시스템별 기본 경로
        system = platform.system()
        if system == 'Darwin':  # macOS
            possible_paths.extend([
                '/usr/local/bin/chromedriver',
                '/opt/homebrew/bin/chromedriver',
                os.path.expanduser('~/Downloads/chromedriver'),
                './chromedriver'
            ])
        elif system == 'Windows':
            possible_paths.extend([
                'chromedriver.exe',
                'C:\\chromedriver\\chromedriver.exe',
                os.path.expanduser('~\\Downloads\\chromedriver.exe')
            ])
        else:  # Linux
            possible_paths.extend([
                '/usr/bin/chromedriver',
                '/usr/local/bin/chromedriver',
                os.path.expanduser('~/Downloads/chromedriver')
            ])
        
        # 경로에서 찾기
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ ChromeDriver 발견: {path}")
                return path
        
        print("❌ ChromeDriver를 찾을 수 없습니다.")
        return None
    
    def get_chrome_version(self):
        """설치된 Chrome 버전 확인"""
        try:
            system = platform.system()
            if system == 'Darwin':
                result = subprocess.run(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    capture_output=True, text=True
                )
            elif system == 'Windows':
                result = subprocess.run(
                    ['chrome.exe', '--version'],
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    ['google-chrome', '--version'],
                    capture_output=True, text=True
                )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"Chrome 버전: {version}")
                return version
        except:
            print("Chrome 버전을 확인할 수 없습니다.")
        return None
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        if not self.driver_path:
            self.print_download_instructions()
            raise FileNotFoundError("ChromeDriver를 찾을 수 없습니다. 위 안내를 따라 설치해주세요.")
        
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 디버깅을 위해 headless 모드 비활성화
        # chrome_options.add_argument('--headless')
        
        service = Service(self.driver_path)
        
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome 드라이버 초기화 성공")
        except Exception as e:
            print(f"❌ Chrome 드라이버 초기화 실패: {e}")
            self.print_download_instructions()
            raise
    
    def print_download_instructions(self):
        """ChromeDriver 다운로드 안내"""
        print("\n" + "="*60)
        print("ChromeDriver 설치 안내")
        print("="*60)
        
        chrome_version = self.get_chrome_version()
        
        print("\n1. Chrome 버전 확인:")
        print("   브라우저에서 chrome://version/ 접속")
        if chrome_version:
            print(f"   현재 버전: {chrome_version}")
        
        print("\n2. ChromeDriver 다운로드:")
        print("   공식 사이트: https://googlechromelabs.github.io/chrome-for-testing/")
        print("   구 사이트: https://chromedriver.chromium.org/downloads")
        
        print("\n3. 다운로드 후:")
        system = platform.system()
        if system == 'Darwin':
            print("   a) 다운로드한 파일을 이 스크립트와 같은 폴더에 복사")
            print("   b) 터미널에서 실행: chmod +x chromedriver")
            print("   c) macOS 보안 설정에서 허용 필요할 수 있음")
        elif system == 'Windows':
            print("   a) chromedriver.exe를 이 스크립트와 같은 폴더에 복사")
        else:
            print("   a) 다운로드한 파일을 이 스크립트와 같은 폴더에 복사")
            print("   b) 터미널에서 실행: chmod +x chromedriver")
        
        print("\n4. 스크립트 재실행:")
        print("   python official_chromedriver_scraper.py")
        print("="*60)
    
    def scrape_law(self, url):
        """법령 페이지 크롤링"""
        print(f"\n📖 페이지 접속: {url}")
        self.driver.get(url)
        
        print("⏳ 페이지 로딩 대기 (10초)...")
        time.sleep(10)
        
        # 페이지 소스 저장
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print("✅ page_source.html 저장")
        
        # 콘텐츠 추출
        law_data = self.extract_content()
        
        return law_data
    
    def extract_content(self):
        """법령 내용 추출"""
        law_data = {
            'title': '',
            'articles': [],
            'raw_text': ''
        }
        
        try:
            # 전체 body 텍스트
            body = self.driver.find_element(By.TAG_NAME, 'body')
            law_data['raw_text'] = body.text
            
            # 제목 찾기
            title_match = re.search(r'법인세법\s*(?:\[.*?\])?', law_data['raw_text'])
            if title_match:
                law_data['title'] = title_match.group()
            
            # 조문 파싱
            article_pattern = r'제(\d+(?:의\d+)?)조[\s\(（](.*?)[\)）]'
            articles = re.findall(article_pattern, law_data['raw_text'])
            
            for article_num, article_title in articles:
                law_data['articles'].append({
                    'number': article_num,
                    'title': article_title.strip()
                })
            
            print(f"✅ 추출 완료: {len(law_data['articles'])}개 조문")
            
        except Exception as e:
            print(f"❌ 추출 실패: {e}")
        
        return law_data
    
    def save_results(self, data):
        """결과 저장"""
        # JSON 저장
        with open('tax_law_official.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ tax_law_official.json 저장")
        
        # 텍스트 저장
        with open('tax_law_official.txt', 'w', encoding='utf-8') as f:
            f.write(data.get('raw_text', ''))
        print("✅ tax_law_official.txt 저장")
    
    def close(self):
        """드라이버 종료"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("브라우저를 닫았습니다.")

def main():
    print("🚀 공식 ChromeDriver를 사용한 법인세법 크롤링")
    print("="*60)
    
    # ChromeDriver 경로 (None이면 자동 탐색)
    driver_path = None
    
    # 사용자 입력 받기
    custom_path = input("ChromeDriver 경로 입력 (Enter: 자동 탐색): ").strip()
    if custom_path:
        driver_path = custom_path
    
    try:
        scraper = OfficialChromeDriverScraper(driver_path)
        
        url = "https://www.law.go.kr/법령/법인세법"
        result = scraper.scrape_law(url)
        
        if result and result.get('articles'):
            scraper.save_results(result)
            print(f"\n✅ 성공: {len(result['articles'])}개 조문 추출")
        elif result and result.get('raw_text'):
            scraper.save_results(result)
            print("\n⚠️ 조문 파싱 실패, 원본 텍스트만 저장")
        else:
            print("\n❌ 크롤링 실패")
        
        scraper.close()
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("\nChromeDriver가 올바르게 설치되었는지 확인해주세요.")

if __name__ == "__main__":
    main()