#!/usr/bin/env python3
"""
법제처 오픈 API 테스트
Version 1.0.0 (2025-01-11)
- 국가법령정보공동활용 Open API 사용
- https://open.law.go.kr/
"""

import requests
import xml.etree.ElementTree as ET
import json
from typing import Dict, List, Optional
import os

class KoreanLawAPI:
    def __init__(self, api_key: str):
        """
        법제처 Open API 클라이언트
        
        Args:
            api_key: 발급받은 API 인증키
        """
        self.api_key = api_key
        self.base_url = "https://www.law.go.kr/DRF/lawService.do"
        self.search_url = "https://www.law.go.kr/DRF/lawSearch.do"
        
    def search_law(self, query: str = "법인세법", target: str = "law") -> Optional[Dict]:
        """
        법령 검색
        
        Args:
            query: 검색어 (법령명)
            target: 검색 대상 (law: 법령, article: 조문)
        """
        params = {
            'OC': self.api_key,
            'target': target,
            'type': 'XML',  # XML 또는 HTML
            'query': query
        }
        
        try:
            response = requests.get(self.search_url, params=params)
            if response.status_code == 200:
                return self.parse_search_result(response.text)
            else:
                print(f"❌ API 요청 실패: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 검색 중 오류: {e}")
            return None
    
    def get_law_detail(self, law_id: str, law_type: str = "LSW") -> Optional[Dict]:
        """
        법령 상세 정보 조회
        
        Args:
            law_id: 법령 ID (MST)
            law_type: 법령 구분 (LSW: 현행법령)
        """
        params = {
            'OC': self.api_key,
            'target': 'law',
            'type': 'XML',
            'MST': law_id,
            'mobileYn': 'N'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                return self.parse_law_detail(response.text)
            else:
                print(f"❌ 상세 조회 실패: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 조회 중 오류: {e}")
            return None
    
    def parse_search_result(self, xml_text: str) -> Dict:
        """검색 결과 XML 파싱"""
        result = {
            'total_count': 0,
            'laws': []
        }
        
        try:
            root = ET.fromstring(xml_text)
            
            # 전체 건수
            total_cnt = root.find('.//totalCnt')
            if total_cnt is not None:
                result['total_count'] = int(total_cnt.text)
            
            # 법령 목록
            for law in root.findall('.//law'):
                law_info = {}
                
                # 법령 기본 정보
                law_info['법령일련번호'] = self.get_xml_text(law, '법령일련번호')
                law_info['법령명'] = self.get_xml_text(law, '법령명')
                law_info['법령명한글'] = self.get_xml_text(law, '법령명한글')
                law_info['법령약칭명'] = self.get_xml_text(law, '법령약칭명')
                law_info['법령ID'] = self.get_xml_text(law, '법령ID')
                law_info['공포일자'] = self.get_xml_text(law, '공포일자')
                law_info['공포번호'] = self.get_xml_text(law, '공포번호')
                law_info['제개정구분명'] = self.get_xml_text(law, '제개정구분명')
                law_info['시행일자'] = self.get_xml_text(law, '시행일자')
                law_info['소관부처'] = self.get_xml_text(law, '소관부처')
                
                result['laws'].append(law_info)
            
            return result
            
        except ET.ParseError as e:
            print(f"❌ XML 파싱 오류: {e}")
            return result
    
    def parse_law_detail(self, xml_text: str) -> Dict:
        """법령 상세 정보 XML 파싱"""
        result = {
            'law_info': {},
            'articles': [],
            'raw_xml': xml_text[:500]  # 디버깅용
        }
        
        try:
            root = ET.fromstring(xml_text)
            
            # 법령 기본 정보
            basic_info = root.find('.//기본정보')
            if basic_info is not None:
                result['law_info'] = {
                    '법령명': self.get_xml_text(basic_info, '법령명_한글'),
                    '시행일자': self.get_xml_text(basic_info, '시행일자'),
                    '소관부처': self.get_xml_text(basic_info, '소관부처명')
                }
            
            # 조문 정보
            for article in root.findall('.//조문'):
                article_info = {
                    '조문번호': self.get_xml_text(article, '조문번호'),
                    '조문제목': self.get_xml_text(article, '조문제목'),
                    '조문내용': self.get_xml_text(article, '조문내용'),
                    '항': []
                }
                
                # 항 정보
                for paragraph in article.findall('.//항'):
                    para_info = {
                        '항번호': self.get_xml_text(paragraph, '항번호'),
                        '항내용': self.get_xml_text(paragraph, '항내용')
                    }
                    article_info['항'].append(para_info)
                
                result['articles'].append(article_info)
            
            return result
            
        except ET.ParseError as e:
            print(f"❌ XML 파싱 오류: {e}")
            return result
    
    def get_xml_text(self, element, tag: str) -> str:
        """XML 요소에서 텍스트 추출"""
        found = element.find(tag)
        return found.text if found is not None and found.text else ""
    
    def get_law_by_article(self, law_name: str, article_num: str) -> Optional[Dict]:
        """
        특정 조문 조회
        
        Args:
            law_name: 법령명
            article_num: 조문 번호
        """
        # 먼저 법령 검색
        search_result = self.search_law(law_name)
        if not search_result or not search_result['laws']:
            print(f"❌ 법령 '{law_name}'을 찾을 수 없습니다")
            return None
        
        # 첫 번째 검색 결과 사용
        law_id = search_result['laws'][0].get('법령ID')
        if not law_id:
            print("❌ 법령 ID를 찾을 수 없습니다")
            return None
        
        # 상세 정보 조회
        detail = self.get_law_detail(law_id)
        if detail:
            # 특정 조문 찾기
            for article in detail['articles']:
                if article['조문번호'] == article_num:
                    return article
        
        return None
    
    def save_to_file(self, data: Dict, filename: str):
        """결과를 파일로 저장"""
        os.makedirs('cache', exist_ok=True)
        filepath = f'cache/{filename}'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {filepath} 저장 완료")

def test_api():
    """API 테스트"""
    # API 키 입력 (환경변수 또는 직접 입력)
    api_key = os.getenv('LAW_API_KEY', '')
    
    if not api_key:
        api_key = input("법제처 API 키를 입력하세요: ").strip()
    
    if not api_key:
        print("❌ API 키가 필요합니다")
        print("https://open.law.go.kr/ 에서 발급받으세요")
        return
    
    # API 클라이언트 생성
    client = KoreanLawAPI(api_key)
    
    print("\n" + "="*60)
    print("🔍 법인세법 검색 중...")
    print("="*60)
    
    # 1. 법령 검색
    search_result = client.search_law("법인세법")
    if search_result:
        print(f"\n✅ 검색 결과: {search_result['total_count']}건")
        
        if search_result['laws']:
            first_law = search_result['laws'][0]
            print(f"\n첫 번째 결과:")
            print(f"  법령명: {first_law.get('법령명한글', '')}")
            print(f"  시행일자: {first_law.get('시행일자', '')}")
            print(f"  법령ID: {first_law.get('법령ID', '')}")
            
            # 2. 상세 정보 조회
            law_id = first_law.get('법령ID')
            if law_id:
                print(f"\n📖 법령 상세 정보 조회 중...")
                detail = client.get_law_detail(law_id)
                
                if detail and detail['articles']:
                    print(f"✅ {len(detail['articles'])}개 조문 조회 완료")
                    
                    # 처음 3개 조문 출력
                    print("\n📝 샘플 조문:")
                    for article in detail['articles'][:3]:
                        print(f"\n{article.get('조문번호', '')} {article.get('조문제목', '')}")
                        content = article.get('조문내용', '')[:200]
                        print(f"  {content}...")
                    
                    # 결과 저장
                    client.save_to_file(detail, 'api_law_detail.json')
                    client.save_to_file(search_result, 'api_search_result.json')
                else:
                    print("❌ 상세 정보를 가져올 수 없습니다")
    else:
        print("❌ 검색 실패")
    
    print("\n💡 API 사용 가능한 기능:")
    print("  1. 법령 검색 (search_law)")
    print("  2. 법령 상세 조회 (get_law_detail)")
    print("  3. 특정 조문 조회 (get_law_by_article)")
    print("  4. 법령 연혁 조회")
    print("  5. 법령 용어 사전")
    print("\n자세한 API 문서: https://open.law.go.kr/LSO/openApi/guideList.do")

if __name__ == "__main__":
    test_api()