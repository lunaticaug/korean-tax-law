#!/usr/bin/env python3
"""
법제처 Open API - YAML 설정 파일 사용
Version 1.0.0 (2025-01-11)
- API_law.yaml에서 이메일 ID 읽기
- DART 크롤러와 동일한 방식
"""

import requests
import xml.etree.ElementTree as ET
import json
import yaml
import os
from typing import Dict, Optional

class LawAPIClient:
    def __init__(self):
        """YAML 파일에서 설정 로드"""
        self.config = self.load_config()
        self.email_id = self.config.get('email_id')
        
        if not self.email_id or self.email_id == 'YOUR_EMAIL_ID_HERE':
            print("⚠️ API_law.yaml 파일에 이메일 ID를 입력해주세요!")
            print("   예: test@naver.com이면 'test' 입력")
            self.email_id = input("임시로 사용할 이메일 ID 입력: ").strip() or "test"
        
        self.base_url = "http://www.law.go.kr/DRF"
        print(f"✅ API 클라이언트 초기화 (OC={self.email_id})")
    
    def load_config(self) -> Dict:
        """YAML 설정 파일 로드"""
        config_file = 'API_law.yaml'
        
        if not os.path.exists(config_file):
            print(f"⚠️ {config_file} 파일이 없습니다.")
            print("   생성 중...")
            with open(config_file, 'w') as f:
                f.write("email_id: YOUR_EMAIL_ID_HERE")
            return {'email_id': 'YOUR_EMAIL_ID_HERE'}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config else {}
        except Exception as e:
            print(f"❌ YAML 파일 읽기 오류: {e}")
            return {}
    
    def search_law(self, query: str, display: int = 20) -> Optional[Dict]:
        """
        법령 검색
        
        Args:
            query: 검색어 (법령명)
            display: 결과 개수 (최대 100)
        """
        url = f"{self.base_url}/lawSearch.do"
        params = {
            'OC': self.email_id,
            'target': 'law',
            'type': 'XML',
            'query': query,
            'display': display
        }
        
        print(f"\n🔍 '{query}' 검색 중...")
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return self.parse_search_xml(response.content)
            else:
                print(f"❌ 검색 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 요청 오류: {e}")
            return None
    
    def parse_search_xml(self, xml_content: bytes) -> Dict:
        """검색 결과 XML 파싱"""
        result = {
            'total_count': 0,
            'laws': []
        }
        
        try:
            root = ET.fromstring(xml_content)
            
            # 전체 건수
            total = root.find('.//totalCnt')
            if total is not None and total.text:
                result['total_count'] = int(total.text)
                print(f"✅ 총 {total.text}건 검색됨")
            
            # 법령 목록
            for law in root.findall('.//law'):
                law_info = {}
                
                fields = [
                    '법령일련번호', '법령명한글', '법령약칭명', '법령ID',
                    '공포일자', '공포번호', '제개정구분명', '시행일자',
                    '소관부처명', '법령상세링크'
                ]
                
                for field in fields:
                    elem = law.find(field)
                    if elem is not None and elem.text:
                        law_info[field] = elem.text
                
                if law_info:
                    result['laws'].append(law_info)
            
            return result
            
        except ET.ParseError as e:
            print(f"❌ XML 파싱 오류: {e}")
            return result
    
    def get_law_detail(self, law_id: str) -> Optional[str]:
        """
        법령 상세 조회 (HTML)
        
        Args:
            law_id: 법령 일련번호
        """
        url = f"{self.base_url}/lawService.do"
        params = {
            'OC': self.email_id,
            'target': 'law',
            'type': 'HTML',
            'MST': law_id
        }
        
        print(f"📖 법령 상세 조회 중 (ID: {law_id})...")
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ 조회 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 요청 오류: {e}")
            return None
    
    def save_results(self, data: Dict, filename: str):
        """결과 저장"""
        os.makedirs('cache', exist_ok=True)
        filepath = f'cache/{filename}'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 {filepath} 저장 완료")
    
    def download_law(self, law_name: str):
        """
        법령 검색 및 다운로드
        
        Args:
            law_name: 법령명
        """
        # 1. 법령 검색
        search_result = self.search_law(law_name)
        
        if not search_result or not search_result['laws']:
            print(f"❌ '{law_name}'을 찾을 수 없습니다")
            return
        
        # 2. 첫 번째 결과 선택
        first_law = search_result['laws'][0]
        print(f"\n📋 선택된 법령:")
        print(f"  - 법령명: {first_law.get('법령명한글', '')}")
        print(f"  - 시행일자: {first_law.get('시행일자', '')}")
        print(f"  - 소관부처: {first_law.get('소관부처명', '')}")
        
        # 3. 상세 정보 조회
        law_id = first_law.get('법령일련번호')
        if law_id:
            detail = self.get_law_detail(law_id)
            if detail:
                # HTML 저장
                html_file = f"cache/{law_name}_detail.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(detail)
                print(f"💾 {html_file} 저장 완료")
        
        # 4. 검색 결과 저장
        self.save_results(search_result, f"{law_name}_search.json")
        
        return search_result

def main():
    print("="*60)
    print("🚀 법제처 Open API 클라이언트")
    print("="*60)
    
    # 클라이언트 초기화
    client = LawAPIClient()
    
    # 법령 검색 및 다운로드
    laws_to_search = [
        "법인세법",
        "소득세법",
        "부가가치세법"
    ]
    
    for law_name in laws_to_search:
        result = client.download_law(law_name)
        if result:
            print(f"✅ {law_name} 처리 완료\n")
        else:
            print(f"❌ {law_name} 처리 실패\n")
        
        # API 부하 방지
        import time
        time.sleep(1)
    
    print("\n" + "="*60)
    print("📊 처리 완료!")
    print("cache/ 폴더에서 결과를 확인하세요")

if __name__ == "__main__":
    main()