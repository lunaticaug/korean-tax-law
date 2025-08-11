#!/usr/bin/env python3
"""
법제처 Open API 대화형 검색 도구
Version 1.0.0 (2025-01-11)
- 사용자 입력을 받아 법령 검색
- 검색 결과 목록 표시 및 선택
- 다양한 형식으로 다운로드
"""

import requests
import xml.etree.ElementTree as ET
import json
import yaml
import os
from typing import Dict, Optional
from datetime import datetime

class InteractiveLawSearch:
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
            return {'email_id': 'YOUR_EMAIL_ID_HERE'}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # YAML frontmatter가 있는 경우 처리
                if content.startswith('---'):
                    parts = content.split('---')
                    if len(parts) >= 3:
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
    
    def search_law(self, query: str, display: int = 50) -> Optional[Dict]:
        """법령 검색"""
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
            
            # 법령 목록
            for law in root.findall('.//law'):
                law_info = {}
                
                fields = [
                    '법령일련번호', '법령명한글', '법령약칭명', '법령ID',
                    '공포일자', '공포번호', '제개정구분명', '시행일자',
                    '소관부처명', '법령구분명', '법령상세링크'
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
    
    def display_search_results(self, results: Dict) -> Optional[Dict]:
        """검색 결과 표시 및 선택"""
        if not results or not results['laws']:
            print("❌ 검색 결과가 없습니다")
            return None
        
        print(f"\n✅ 총 {results['total_count']}건 검색됨")
        print("-" * 80)
        
        # 최대 20개까지 표시
        display_count = min(len(results['laws']), 20)
        
        for i, law in enumerate(results['laws'][:display_count], 1):
            print(f"\n[{i}] {law.get('법령명한글', '')} {law.get('법령약칭명', '')}")
            print(f"    📅 시행일: {self.format_date(law.get('시행일자', ''))}")
            print(f"    🏛️ 소관부처: {law.get('소관부처명', '')}")
            print(f"    📋 구분: {law.get('법령구분명', '')}")
            print(f"    🔄 상태: {law.get('제개정구분명', '')}")
        
        if results['total_count'] > display_count:
            print(f"\n... 외 {results['total_count'] - display_count}건")
        
        print("\n" + "-" * 80)
        print("선택 옵션:")
        print("  번호 입력: 해당 법령 상세 조회")
        print("  0: 새로운 검색")
        print("  q: 종료")
        
        choice = input("\n선택: ").strip().lower()
        
        if choice == 'q':
            return 'quit'
        elif choice == '0':
            return None
        elif choice.isdigit() and 1 <= int(choice) <= display_count:
            return results['laws'][int(choice) - 1]
        else:
            print("❌ 잘못된 선택입니다")
            return None
    
    def format_date(self, date_str: str) -> str:
        """날짜 형식 변환 (20250701 → 2025.07.01)"""
        if len(date_str) == 8:
            return f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
        return date_str
    
    def get_law_detail(self, law_id: str, output_type: str = "HTML") -> Optional[str]:
        """법령 상세 조회"""
        url = f"{self.base_url}/lawService.do"
        params = {
            'OC': self.email_id,
            'target': 'law',
            'type': output_type,
            'MST': law_id
        }
        
        print(f"📖 법령 상세 조회 중 (Type: {output_type})...")
        
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
    
    def download_law(self, law_info: Dict):
        """선택한 법령 다운로드"""
        law_name = law_info.get('법령명한글', '법령')
        law_id = law_info.get('법령일련번호')
        
        if not law_id:
            print("❌ 법령 ID를 찾을 수 없습니다")
            return
        
        print(f"\n📥 '{law_name}' 다운로드 옵션")
        print("-" * 40)
        print("1. HTML (웹 페이지 형식)")
        print("2. XML (구조화된 데이터)")
        print("3. 모두 다운로드")
        print("0. 취소")
        
        choice = input("\n선택: ").strip()
        
        formats = []
        if choice == '1':
            formats = ['HTML']
        elif choice == '2':
            formats = ['XML']
        elif choice == '3':
            formats = ['HTML', 'XML']
        elif choice == '0':
            return
        else:
            print("❌ 잘못된 선택입니다")
            return
        
        # 실행시간 기준 폴더 생성
        save_dir = f'_cache/{self.session_folder}'
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for fmt in formats:
            detail = self.get_law_detail(law_id, fmt)
            if detail:
                # 민감정보 제거
                clean_detail = self.sanitize_data(detail)
                
                ext = 'html' if fmt == 'HTML' else 'xml'
                # 파일명에 사용할 수 없는 문자 제거
                safe_name = law_name.replace('/', '_').replace('\\', '_')
                filename = f"{save_dir}/{safe_name}_전체조문_{timestamp}.{ext}"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(clean_detail if isinstance(clean_detail, str) else str(clean_detail))
                
                print(f"✅ {filename} 저장 완료 ({len(str(clean_detail)):,} bytes)")
        
        # 메타데이터도 저장 (민감정보 제거)
        clean_metadata = self.sanitize_data(law_info)
        metadata_file = f"{save_dir}/{safe_name}_메타데이터_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(clean_metadata, f, ensure_ascii=False, indent=2)
        print(f"📋 {metadata_file} 메타데이터 저장 완료")
    
    def run(self):
        """대화형 검색 실행"""
        print("\n" + "=" * 60)
        print("🔍 법제처 법령 검색 시스템")
        print("=" * 60)
        print("\n검색 가능한 예시:")
        print("  - 법령명: 법인세법, 소득세법, 민법, 형법 등")
        print("  - 약칭: 개인정보보호법, 정보통신망법 등")
        print("  - 키워드: 세금, 개인정보, 환경 등")
        
        while True:
            print("\n" + "-" * 60)
            query = input("\n검색어 입력 (q: 종료): ").strip()
            
            if query.lower() == 'q':
                print("\n👋 검색을 종료합니다")
                break
            
            if not query:
                print("❌ 검색어를 입력해주세요")
                continue
            
            # 검색 실행
            results = self.search_law(query)
            
            if not results:
                continue
            
            # 결과 표시 및 선택
            selected = self.display_search_results(results)
            
            if selected == 'quit':
                print("\n👋 검색을 종료합니다")
                break
            elif selected and isinstance(selected, dict):
                # 법령 다운로드
                self.download_law(selected)

def main():
    searcher = InteractiveLawSearch()
    searcher.run()

if __name__ == "__main__":
    main()