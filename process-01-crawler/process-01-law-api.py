#!/usr/bin/env python3
"""
법제처 Open API 클라이언트
Version 3.0.0 (2025-01-11)
- API_law.yaml 설정 파일 사용
- 법령 검색 및 상세 내용 다운로드
- DART 크롤러와 동일한 패턴 적용
"""

import requests
import xml.etree.ElementTree as ET
import json
import yaml
import os
from typing import Dict, Optional, List
from datetime import datetime

class LawAPIClient:
    def __init__(self):
        """YAML 파일에서 설정 로드"""
        self.config = self.load_config()
        self.email_id = self.config.get('email_id')
        
        if not self.email_id or self.email_id == 'YOUR_EMAIL_ID_HERE':
            print("⚠️ API_law.yaml 파일에 이메일 ID를 입력해주세요!")
            print("   예: test@naver.com이면 'test' 입력")
            self.email_id = input("임시로 사용할 이메일 ID 입력: ").strip() or "test"
        
        # 이메일에서 @ 앞부분만 추출
        if '@' in self.email_id:
            self.email_id = self.email_id.split('@')[0]
        
        self.base_url = "http://www.law.go.kr/DRF"
        # 실행 시간 기준 폴더명 생성
        self.session_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"✅ API 클라이언트 초기화 완료")
    
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
                content = f.read()
                # YAML frontmatter가 있는 경우 처리
                if content.startswith('---'):
                    # frontmatter 제거하고 실제 YAML 부분만 파싱
                    parts = content.split('---')
                    if len(parts) >= 3:
                        # 세 번째 부분이 실제 설정
                        yaml_content = parts[2].strip()
                    else:
                        yaml_content = content
                else:
                    yaml_content = content
                    
                config = yaml.safe_load(yaml_content)
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
    
    def get_law_detail(self, law_id: str, output_type: str = "HTML") -> Optional[str]:
        """
        법령 상세 조회
        
        Args:
            law_id: 법령 일련번호
            output_type: 출력 형식 (HTML, XML)
        """
        url = f"{self.base_url}/lawService.do"
        params = {
            'OC': self.email_id,
            'target': 'law',
            'type': output_type,
            'MST': law_id
        }
        
        print(f"📖 법령 상세 조회 중 (ID: {law_id}, Type: {output_type})...")
        
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
    
    def sanitize_data(self, data: any) -> any:
        """
        민감정보 제거 (재귀적)
        - OC 파라미터 제거
        - 이메일 ID 마스킹
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                # OC 관련 필드 제거
                if key.upper() == 'OC' or key == 'email_id':
                    continue
                # 값에서도 재귀적으로 제거
                cleaned[key] = self.sanitize_data(value)
            return cleaned
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # 문자열 내 이메일 ID 마스킹
            if self.email_id and self.email_id in data:
                return data.replace(self.email_id, "***MASKED***")
            # 이메일 패턴 마스킹
            import re
            return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', data)
        else:
            return data
    
    def save_results(self, data: any, filename: str, law_name: str = None):
        """
        결과 저장 (실행시간 기준 폴더 구조)
        
        Args:
            data: 저장할 데이터
            filename: 파일명 (타임스탬프 포함)
            law_name: 법령명 (현재 미사용, 호환성 유지)
        """
        # 실행 시간 기준 폴더
        save_dir = f'_cache/{self.session_folder}'
        
        os.makedirs(save_dir, exist_ok=True)
        filepath = f'{save_dir}/{filename}'
        
        # 저장 전 민감정보 제거
        clean_data = self.sanitize_data(data)
        
        if filename.endswith('.json'):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, ensure_ascii=False, indent=2)
        else:
            # 문자열 데이터도 정제
            if isinstance(clean_data, str):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(clean_data)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(clean_data))
        
        print(f"💾 {filepath} 저장 완료")
    
    def download_law(self, law_name: str, formats: List[str] = None):
        """
        법령 검색 및 다운로드
        
        Args:
            law_name: 법령명
            formats: 다운로드할 형식 리스트 ['HTML', 'XML']
        """
        if not formats:
            formats = ['HTML', 'XML']
        
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
        
        # 3. 각 형식으로 상세 정보 조회 및 저장
        law_id = first_law.get('법령일련번호')
        if law_id:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for fmt in formats:
                detail = self.get_law_detail(law_id, fmt)
                if detail:
                    ext = 'html' if fmt == 'HTML' else 'xml'
                    filename = f"{law_name}_전체조문_{timestamp}.{ext}"
                    self.save_results(detail, filename, law_name=law_name)
        
        # 4. 검색 결과 저장
        self.save_results(search_result, f"{law_name}_검색결과_{timestamp}.json", law_name=law_name)
        
        return search_result

def main():
    print("="*60)
    print("🚀 법제처 Open API 클라이언트")
    print("="*60)
    
    # 클라이언트 초기화
    client = LawAPIClient()
    
    # 법령 검색 및 다운로드
    # 원하는 법령명을 추가하거나 수정하세요
    laws_to_search = [
        "법인세법",
        # "소득세법",
        # "부가가치세법",
        # "상속세및증여세법",
        # "조세특례제한법",
        # "국세기본법",
        # "관세법",
    ]
    
    for law_name in laws_to_search:
        result = client.download_law(law_name, formats=['HTML', 'XML'])
        if result:
            print(f"✅ {law_name} 처리 완료\n")
        else:
            print(f"❌ {law_name} 처리 실패\n")
        
        # API 부하 방지
        import time
        time.sleep(1)
    
    print("\n" + "="*60)
    print("📊 처리 완료!")
    print("_cache/ 폴더에서 결과를 확인하세요")

if __name__ == "__main__":
    main()