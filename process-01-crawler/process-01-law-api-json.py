#!/usr/bin/env python3
"""
법제처 Open API 클라이언트 - JSON 버전
Version 1.0.0 (2025-01-12)
- JSON 형식을 기본으로 사용
- XML과 동일한 데이터를 더 쉽게 파싱
"""

import requests
import json
import yaml
import os
from typing import Dict, Optional, List, Any
from datetime import datetime

class LawAPIClientJSON:
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
        print(f"✅ API 클라이언트 초기화 완료 (JSON 모드)")
    
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
    
    def search_law(self, query: str, display: int = 20, use_json: bool = True) -> Optional[Dict]:
        """
        법령 검색 (JSON 우선)
        
        Args:
            query: 검색어 (법령명)
            display: 결과 개수 (최대 100)
            use_json: JSON 형식 사용 여부
        """
        url = f"{self.base_url}/lawSearch.do"
        params = {
            'OC': self.email_id,
            'target': 'law',
            'type': 'JSON' if use_json else 'XML',
            'query': query,
            'display': display
        }
        
        print(f"\n🔍 '{query}' 검색 중... (형식: {'JSON' if use_json else 'XML'})")
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                if use_json:
                    return self.parse_search_json(response.text)
                else:
                    return self.parse_search_xml(response.content)
            else:
                print(f"❌ 검색 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 요청 오류: {e}")
            return None
    
    def parse_search_json(self, json_content: str) -> Dict:
        """검색 결과 JSON 파싱"""
        try:
            data = json.loads(json_content)
            search_result = data.get('LawSearch', {})
            
            result = {
                'total_count': int(search_result.get('totalCnt', 0)),
                'laws': []
            }
            
            # 법령 목록 파싱
            laws = search_result.get('law', [])
            if isinstance(laws, dict):  # 단일 결과인 경우
                laws = [laws]
            
            for law in laws:
                law_info = {
                    '법령일련번호': law.get('법령일련번호', ''),
                    '법령명한글': law.get('법령명한글', ''),
                    '법령약칭명': law.get('법령약칭명', ''),
                    '법령ID': law.get('법령ID', ''),
                    '공포일자': law.get('공포일자', ''),
                    '공포번호': law.get('공포번호', ''),
                    '제개정구분명': law.get('제개정구분명', ''),
                    '시행일자': law.get('시행일자', ''),
                    '소관부처명': law.get('소관부처명', ''),
                    '법령상세링크': law.get('법령상세링크', '')
                }
                result['laws'].append(law_info)
            
            print(f"✅ 총 {result['total_count']}건 검색됨")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return {'total_count': 0, 'laws': []}
    
    def parse_search_xml(self, xml_content: bytes) -> Dict:
        """검색 결과 XML 파싱 (호환성 유지)"""
        import xml.etree.ElementTree as ET
        result = {
            'total_count': 0,
            'laws': []
        }
        
        try:
            root = ET.fromstring(xml_content)
            
            total = root.find('.//totalCnt')
            if total is not None and total.text:
                result['total_count'] = int(total.text)
                print(f"✅ 총 {total.text}건 검색됨")
            
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
    
    def get_law_detail(self, law_id: str, output_type: str = "JSON") -> Optional[Any]:
        """
        법령 상세 조회
        
        Args:
            law_id: 법령 일련번호
            output_type: 출력 형식 (JSON, XML, HTML)
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
                if output_type == 'JSON':
                    return json.loads(response.text)
                else:
                    return response.text
            else:
                print(f"❌ 조회 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 요청 오류: {e}")
            return None
    
    def parse_law_detail_json(self, json_data: Dict) -> Dict:
        """
        JSON 법령 상세 파싱하여 구조화
        
        Returns:
            구조화된 법령 데이터
        """
        if '법령' not in json_data:
            return {}
        
        법령 = json_data['법령']
        
        # 구조화된 데이터 생성
        structured = {
            '법령키': 법령.get('법령키', ''),
            '기본정보': 법령.get('기본정보', {}),
            '조문': [],
            '부칙': [],
            '개정문': 법령.get('개정문', {}),
            '제개정이유': 법령.get('제개정이유', {})
        }
        
        # 조문 파싱
        조문단위들 = 법령.get('조문', {}).get('조문단위', [])
        for 조문 in 조문단위들:
            조문정보 = {
                '조문키': 조문.get('조문키', ''),
                '조문번호': 조문.get('조문번호', ''),
                '조문제목': 조문.get('조문제목', ''),
                '조문내용': 조문.get('조문내용', ''),
                '조문여부': 조문.get('조문여부', ''),
                '시행일자': 조문.get('조문시행일자', ''),
                '항': []
            }
            
            # 항 정보가 있으면 파싱
            if '항' in 조문:
                항단위들 = 조문['항'].get('항단위', [])
                if isinstance(항단위들, dict):
                    항단위들 = [항단위들]
                
                for 항 in 항단위들:
                    항정보 = {
                        '항번호': 항.get('항번호', ''),
                        '항내용': 항.get('항내용', ''),
                        '호': []
                    }
                    
                    # 호 정보가 있으면 파싱
                    if '호' in 항:
                        호단위들 = 항['호'].get('호단위', [])
                        if isinstance(호단위들, dict):
                            호단위들 = [호단위들]
                        
                        for 호 in 호단위들:
                            호정보 = {
                                '호번호': 호.get('호번호', ''),
                                '호내용': 호.get('호내용', '')
                            }
                            항정보['호'].append(호정보)
                    
                    조문정보['항'].append(항정보)
            
            structured['조문'].append(조문정보)
        
        # 부칙 파싱
        부칙단위들 = 법령.get('부칙', {}).get('부칙단위', [])
        if isinstance(부칙단위들, dict):
            부칙단위들 = [부칙단위들]
        
        for 부칙 in 부칙단위들:
            부칙정보 = {
                '부칙키': 부칙.get('부칙키', ''),
                '부칙공포일자': 부칙.get('부칙공포일자', ''),
                '부칙공포번호': 부칙.get('부칙공포번호', ''),
                '부칙내용': 부칙.get('부칙내용', [])
            }
            structured['부칙'].append(부칙정보)
        
        return structured
    
    def sanitize_data(self, data: Any) -> Any:
        """
        민감정보 제거 (재귀적)
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if key.upper() == 'OC' or key == 'email_id':
                    continue
                cleaned[key] = self.sanitize_data(value)
            return cleaned
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            if self.email_id and self.email_id in data:
                return data.replace(self.email_id, "***MASKED***")
            import re
            return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', data)
        else:
            return data
    
    def save_results(self, data: Any, filename: str):
        """
        결과 저장 (JSON 형식 우선)
        """
        save_dir = f'_cache/{self.session_folder}'
        os.makedirs(save_dir, exist_ok=True)
        filepath = f'{save_dir}/{filename}'
        
        # 민감정보 제거
        clean_data = self.sanitize_data(data)
        
        # 파일 확장자에 따라 저장
        if filename.endswith('.json'):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, ensure_ascii=False, indent=2)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(clean_data, str):
                    f.write(clean_data)
                else:
                    f.write(str(clean_data))
        
        print(f"💾 {filepath} 저장 완료")
    
    def display_law_structure(self, structured_data: Dict):
        """법령 구조를 보기 좋게 출력"""
        기본정보 = structured_data.get('기본정보', {})
        
        print("\n" + "="*60)
        print(f"📋 {기본정보.get('법령명_한글', 'Unknown')}")
        print("="*60)
        print(f"공포일자: {기본정보.get('공포일자', '')}")
        print(f"시행일자: {기본정보.get('시행일자', '')}")
        print(f"소관부처: {기본정보.get('소관부처', {}).get('content', '')}")
        print(f"제개정구분: {기본정보.get('제개정구분', '')}")
        
        조문들 = structured_data.get('조문', [])
        print(f"\n총 {len(조문들)}개 조문")
        
        # 처음 5개 조문만 표시
        for i, 조문 in enumerate(조문들[:5], 1):
            if 조문.get('조문여부') == '전문':
                print(f"\n[전문] {조문.get('조문내용', '')[:50]}...")
            else:
                제목 = 조문.get('조문제목', '')
                번호 = 조문.get('조문번호', '')
                print(f"\n제{번호}조({제목})")
                
                # 항이 있으면 개수 표시
                항들 = 조문.get('항', [])
                if 항들:
                    print(f"  └─ {len(항들)}개 항")
        
        if len(조문들) > 5:
            print(f"\n... 외 {len(조문들) - 5}개 조문")
    
    def download_law(self, law_name: str, formats: List[str] = None):
        """
        법령 검색 및 다운로드 (JSON 우선)
        
        Args:
            law_name: 법령명
            formats: 다운로드할 형식 리스트 ['JSON', 'XML', 'HTML']
        """
        if not formats:
            formats = ['JSON', 'XML']  # JSON을 기본으로!
        
        # 1. 법령 검색 (JSON으로)
        search_result = self.search_law(law_name, use_json=True)
        
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
                    ext = fmt.lower()
                    filename = f"{law_name}_전체조문_{timestamp}.{ext}"
                    
                    # JSON인 경우 구조화된 데이터도 저장
                    if fmt == 'JSON':
                        self.save_results(detail, filename)
                        
                        # 구조화된 버전도 저장
                        structured = self.parse_law_detail_json(detail)
                        self.save_results(structured, f"{law_name}_구조화_{timestamp}.json")
                        
                        # 구조 표시
                        self.display_law_structure(structured)
                    else:
                        self.save_results(detail, filename)
        
        # 4. 검색 결과 저장
        self.save_results(search_result, f"{law_name}_검색결과_{timestamp}.json")
        
        return search_result

def main():
    print("="*60)
    print("🚀 법제처 Open API 클라이언트 (JSON 버전)")
    print("="*60)
    
    # 클라이언트 초기화
    client = LawAPIClientJSON()
    
    # 법령 검색 및 다운로드
    laws_to_search = [
        "법인세법",
        # "소득세법",
        # "부가가치세법",
    ]
    
    for law_name in laws_to_search:
        result = client.download_law(law_name, formats=['JSON'])  # JSON만!
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
    print("JSON 파일로 저장되어 파싱이 더 쉽습니다!")

if __name__ == "__main__":
    main()