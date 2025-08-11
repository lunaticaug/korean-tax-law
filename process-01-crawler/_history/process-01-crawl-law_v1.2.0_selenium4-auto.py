#!/usr/bin/env python3
"""
법제처 법인세법 크롤링 - Selenium 4 자동 드라이버 관리
Version 2.0.0 (2025-01-11)
- Selenium 4.6+ 내장 Selenium Manager 사용
- ChromeDriver 별도 설치 불필요
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import re

def scrape_korean_tax_law():
    """법인세법 크롤링 - 드라이버 자동 관리"""
    
    print("🚀 Selenium 4 자동 드라이버로 법인세법 크롤링")
    print("ChromeDriver 설치 불필요 - Selenium이 자동 관리합니다!\n")
    
    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    # options.add_argument('--headless')  # 백그라운드 실행시 주석 해제
    
    # 드라이버 생성 - Selenium이 자동으로 ChromeDriver 다운로드/관리
    print("📥 ChromeDriver 자동 설정 중...")
    driver = webdriver.Chrome(options=options)
    print("✅ Chrome 브라우저 시작\n")
    
    try:
        # 법인세법 페이지 접속
        url = "https://www.law.go.kr/법령/법인세법"
        print(f"📖 페이지 접속: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기
        print("⏳ 페이지 로딩 대기 (10초)...")
        time.sleep(10)
        
        # iframe 처리
        print("🔄 iframe 감지, 프레임 전환 중...")
        try:
            iframe = driver.find_element(By.ID, 'lawService')
            driver.switch_to.frame(iframe)
            print("✅ iframe 내부로 전환 완료\n")
            time.sleep(3)  # iframe 콘텐츠 로딩 대기
        except:
            print("⚠️ iframe 없음, 메인 페이지에서 계속\n")
        
        # 페이지 소스 저장
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("✅ page_source.html 저장\n")
        
        # 콘텐츠 추출
        print("🔍 법령 내용 추출 중...")
        
        # 전체 텍스트 가져오기
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        
        # 데이터 구조화
        law_data = {
            'title': '',
            'articles': [],
            'raw_text': body_text,
            'url': url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 제목 추출
        title_match = re.search(r'법인세법\s*(?:\[.*?\])?', body_text)
        if title_match:
            law_data['title'] = title_match.group()
            print(f"📌 제목: {law_data['title']}")
        
        # 조문 추출 (제X조 패턴)
        article_pattern = r'제(\d+(?:의\d+)?)조[\s\(（](.*?)[\)）]'
        articles = re.findall(article_pattern, body_text)
        
        for article_num, article_title in articles:
            law_data['articles'].append({
                'number': article_num,
                'title': article_title.strip()
            })
        
        print(f"✅ {len(law_data['articles'])}개 조문 발견\n")
        
        # 결과 저장
        print("💾 결과 저장 중...")
        
        # JSON 파일
        with open('tax_law_result.json', 'w', encoding='utf-8') as f:
            json.dump(law_data, f, ensure_ascii=False, indent=2)
        print("✅ tax_law_result.json 저장")
        
        # 텍스트 파일
        with open('tax_law_text.txt', 'w', encoding='utf-8') as f:
            f.write(body_text)
        print("✅ tax_law_text.txt 저장")
        
        # 요약 출력
        print("\n" + "="*60)
        print("📊 크롤링 결과 요약")
        print("="*60)
        print(f"제목: {law_data['title'] or '미확인'}")
        print(f"조문 수: {len(law_data['articles'])}개")
        print(f"텍스트 길이: {len(body_text):,} 자")
        
        if law_data['articles']:
            print(f"\n처음 5개 조문:")
            for article in law_data['articles'][:5]:
                print(f"  - 제{article['number']}조 ({article['title']})")
        
        return law_data
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None
        
    finally:
        # 브라우저 종료
        driver.quit()
        print("브라우저를 종료했습니다.")

if __name__ == "__main__":
    result = scrape_korean_tax_law()
    
    if not result:
        print("\n대체 방법:")
        print("1. 법제처 사이트에서 HWP/PDF 직접 다운로드")
        print("2. 국가법령정보센터 OpenAPI 사용")