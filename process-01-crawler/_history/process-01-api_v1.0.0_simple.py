#!/usr/bin/env python3
"""
법제처 Open API 간단 테스트
Version 1.0.0 (2025-01-11)
- OC 파라미터 = 이메일 ID (@앞부분)
"""

import requests
import xml.etree.ElementTree as ET
import json

def test_law_api(email_id=None):
    """
    법제처 API 테스트
    
    Args:
        email_id: 이메일 주소의 @ 앞부분 (예: 'test', 'myname')
    """
    
    # 기본값은 공개 테스트 키
    if not email_id:
        email_id = input("이메일 ID를 입력하세요 (예: test@naver.com이면 'test' 입력): ").strip()
        if not email_id:
            email_id = "test"  # 기본 테스트 키
            print(f"테스트 키 사용: OC={email_id}")
    
    print(f"\n사용할 API 키(OC): {email_id}")
    print("="*60)
    
    # 1. 법령 목록 조회 (법인세법 검색)
    search_url = "http://www.law.go.kr/DRF/lawSearch.do"
    
    params = {
        'OC': email_id,
        'target': 'law',
        'type': 'XML',
        'query': '법인세법'
    }
    
    print(f"\n🔍 법인세법 검색 중...")
    print(f"URL: {search_url}")
    print(f"파라미터: {params}")
    
    try:
        response = requests.get(search_url, params=params)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            # XML 파싱
            try:
                root = ET.fromstring(response.content)
                
                # 전체 건수
                total = root.find('.//totalCnt')
                if total is not None:
                    print(f"\n✅ 검색 성공! 총 {total.text}건")
                
                # 첫 번째 결과
                first_law = root.find('.//law')
                if first_law is not None:
                    print("\n📋 첫 번째 검색 결과:")
                    
                    fields = [
                        ('법령명한글', '법령명'),
                        ('법령ID', 'ID'),
                        ('공포일자', '공포일'),
                        ('시행일자', '시행일'),
                        ('소관부처명', '소관부처')
                    ]
                    
                    for field, label in fields:
                        elem = first_law.find(field)
                        if elem is not None and elem.text:
                            print(f"  {label}: {elem.text}")
                    
                    # 상세 링크
                    link = first_law.find('법령상세링크')
                    if link is not None and link.text:
                        print(f"  상세링크: {link.text}")
                
                # 결과 저장
                with open('cache/api_test_result.xml', 'wb') as f:
                    f.write(response.content)
                print("\n💾 cache/api_test_result.xml 저장 완료")
                
            except ET.ParseError as e:
                print(f"❌ XML 파싱 오류: {e}")
                print(f"응답 내용(처음 500자): {response.text[:500]}")
        else:
            print(f"❌ API 요청 실패")
            print(f"응답: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    # 2. 다른 출력 형식 테스트
    print("\n" + "="*60)
    print("📝 다른 출력 형식 테스트")
    
    # JSON 형식
    params['type'] = 'JSON'
    print(f"\n🔍 JSON 형식으로 요청...")
    
    try:
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON 파싱 성공")
                
                # JSON 저장
                with open('cache/api_test_result.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("💾 cache/api_test_result.json 저장 완료")
                
            except json.JSONDecodeError:
                print("❌ JSON 파싱 실패")
    except Exception as e:
        print(f"❌ JSON 요청 실패: {e}")
    
    # 사용 가능한 URL 예시 출력
    print("\n" + "="*60)
    print("🔗 사용 가능한 API URL 예시:")
    print(f"1. XML: http://www.law.go.kr/DRF/lawSearch.do?OC={email_id}&target=law&type=XML")
    print(f"2. HTML: http://www.law.go.kr/DRF/lawSearch.do?OC={email_id}&target=law&type=HTML")
    print(f"3. JSON: http://www.law.go.kr/DRF/lawSearch.do?OC={email_id}&target=law&type=JSON")
    print(f"4. 검색: http://www.law.go.kr/DRF/lawSearch.do?OC={email_id}&target=law&type=XML&query=법인세법")

if __name__ == "__main__":
    import os
    os.makedirs('cache', exist_ok=True)
    
    print("🚀 법제처 Open API 테스트")
    print("="*60)
    print("📌 API 키는 이메일 주소의 @ 앞부분입니다")
    print("   예: test@naver.com → OC=test")
    print("="*60)
    
    test_law_api()