#!/usr/bin/env python3
"""
법제처 법인세법 크롤링 스크립트
Version 1.0.0 (2025-01-11)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Optional
import re

class KoreanTaxLawScraper:
    def __init__(self):
        self.base_url = "https://www.law.go.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_law_content_api(self, law_id: str = "법인세법") -> Optional[Dict]:
        """법제처 OpenAPI를 사용한 법령 조회 (API 키 필요)"""
        api_url = f"{self.base_url}/DRF/lawService.do"
        params = {
            'OC': 'nema0130',
            'target': 'law',
            'type': 'HTML',
            'mobileYn': 'N',
            'MST': law_id
        }
        
        try:
            response = self.session.get(api_url, params=params)
            if response.status_code == 200:
                return self.parse_law_html(response.text)
            else:
                print(f"API 요청 실패: {response.status_code}")
                return None
        except Exception as e:
            print(f"API 요청 중 오류: {e}")
            return None
    
    def scrape_law_page(self, url: str) -> Optional[Dict]:
        """일반 웹페이지 크롤링"""
        try:
            response = self.session.get(url)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"페이지 요청 실패: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 법령 내용이 있는 컨테이너 찾기
            content_area = soup.find('div', {'id': 'conScroll'}) or \
                          soup.find('div', {'class': 'lawcon'}) or \
                          soup.find('div', {'id': 'lawmunView'})
            
            if not content_area:
                print("법령 내용 영역을 찾을 수 없습니다.")
                return self.try_ajax_request(url)
            
            return self.extract_law_content(content_area)
            
        except Exception as e:
            print(f"크롤링 중 오류: {e}")
            return None
    
    def try_ajax_request(self, original_url: str) -> Optional[Dict]:
        """AJAX 요청으로 데이터 시도"""
        # URL에서 법령 ID 추출
        law_match = re.search(r'MST=(\d+)', original_url)
        if not law_match:
            return None
        
        law_mst = law_match.group(1)
        ajax_url = f"{self.base_url}/ajax/lawView.do"
        
        data = {
            'MST': law_mst,
            'ACT_TYP': 'view'
        }
        
        try:
            response = self.session.post(ajax_url, data=data)
            if response.status_code == 200:
                return self.parse_ajax_response(response.json())
        except Exception as e:
            print(f"AJAX 요청 실패: {e}")
        
        return None
    
    def extract_law_content(self, content_area) -> Dict:
        """법령 내용 추출"""
        law_data = {
            'title': '',
            'articles': [],
            'metadata': {}
        }
        
        # 제목 추출
        title = content_area.find('h2') or content_area.find('h3', {'class': 'title'})
        if title:
            law_data['title'] = title.get_text(strip=True)
        
        # 조문 추출
        articles = content_area.find_all(['div', 'p'], {'class': re.compile('law_con|article|조')})
        
        for article in articles:
            article_text = article.get_text(strip=True)
            if article_text:
                law_data['articles'].append({
                    'text': article_text,
                    'number': self.extract_article_number(article_text)
                })
        
        return law_data
    
    def extract_article_number(self, text: str) -> Optional[str]:
        """조문 번호 추출"""
        match = re.match(r'제(\d+)조', text)
        return match.group(1) if match else None
    
    def parse_law_html(self, html: str) -> Dict:
        """HTML 파싱"""
        soup = BeautifulSoup(html, 'html.parser')
        return self.extract_law_content(soup)
    
    def parse_ajax_response(self, data: Dict) -> Dict:
        """AJAX 응답 파싱"""
        if 'lawCon' in data:
            soup = BeautifulSoup(data['lawCon'], 'html.parser')
            return self.extract_law_content(soup)
        return data
    
    def save_to_file(self, data: Dict, filename: str = "korean_tax_law.json"):
        """결과를 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"데이터가 {filename}에 저장되었습니다.")

def main():
    scraper = KoreanTaxLawScraper()
    
    # 법인세법 URL
    url = "https://www.law.go.kr/법령/법인세법"
    
    print("법인세법 크롤링을 시작합니다...")
    
    # 방법 1: 직접 크롤링 시도
    result = scraper.scrape_law_page(url)
    
    if result and result.get('articles'):
        print(f"성공적으로 {len(result['articles'])}개의 조문을 추출했습니다.")
        scraper.save_to_file(result)
    else:
        print("크롤링에 실패했습니다. Selenium을 사용한 동적 크롤링이 필요할 수 있습니다.")
        print("\n대안:")
        print("1. 법제처 OpenAPI 사용 (API 키 필요)")
        print("2. Selenium을 사용한 동적 크롤링")
        print("3. 법제처 사이트에서 직접 다운로드 (HWP, PDF 형식)")

if __name__ == "__main__":
    main()