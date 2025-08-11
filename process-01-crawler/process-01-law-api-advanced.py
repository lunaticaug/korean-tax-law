#!/usr/bin/env python3
"""
법제처 Open API 고급 클라이언트
Version 1.0.0 (2025-01-11)
- 법령 본문 상세 조회 (특정 조문, 언어 선택)
- 부칙, 별표, 개정문 조회
- 다양한 출력 형식 지원 (HTML/XML/JSON)
"""

import requests
import xml.etree.ElementTree as ET
import json
import yaml
import os
from typing import Dict, Optional, List, Any
from datetime import datetime

class AdvancedLawAPIClient:
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
            
            total = root.find('.//totalCnt')
            if total is not None and total.text:
                result['total_count'] = int(total.text)
            
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
    
    def get_law_detail(self, 
                      law_id: str = None,
                      mst: str = None,
                      output_type: str = "XML",
                      jo_num: str = None,
                      lang: str = None) -> Optional[Any]:
        """
        법령 상세 조회 (고급 옵션)
        
        Args:
            law_id: 법령 ID (ID 또는 MST 중 하나는 필수)
            mst: 법령 마스터 번호 (법령테이블의 lsi_seq 값)
            output_type: 출력 형식 (HTML/XML/JSON)
            jo_num: 조번호 (6자리: 조번호4자리+조가지번호2자리, 예: 000200=2조)
            lang: 언어 (KO=한글, ORI=원문, 기본값=한글)
        """
        
        if not law_id and not mst:
            print("❌ law_id 또는 mst 중 하나는 필수입니다")
            return None
        
        url = f"{self.base_url}/lawService.do"
        params = {
            'OC': self.email_id,
            'target': 'law',
            'type': output_type
        }
        
        # 선택적 파라미터 추가
        if law_id:
            params['ID'] = law_id
        if mst:
            params['MST'] = mst
        if jo_num:
            params['JO'] = jo_num
        if lang:
            params['LANG'] = lang
        
        desc = f"법령 상세 조회 (Type: {output_type}"
        if jo_num:
            desc += f", 조: {jo_num}"
        if lang:
            desc += f", 언어: {lang}"
        desc += ")"
        
        print(f"📖 {desc}...")
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                if output_type == "JSON":
                    return response.json()
                else:
                    return response.text
            else:
                print(f"❌ 조회 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 요청 오류: {e}")
            return None
    
    def parse_law_detail_xml(self, xml_content: str) -> Dict:
        """법령 상세 XML 파싱하여 구조화"""
        try:
            root = ET.fromstring(xml_content)
            
            result = {
                '기본정보': {},
                '조문': [],
                '부칙': [],
                '별표': [],
                '개정문': None,
                '제개정이유': None
            }
            
            # 기본 정보 추출
            basic_fields = [
                '법령ID', '법령명_한글', '법령명_한자', '법령명약칭',
                '공포일자', '공포번호', '시행일자', '소관부처',
                '제개정구분', '소관부처명', '부서명', '부서연락처'
            ]
            
            for field in basic_fields:
                elem = root.find(f'.//{field}')
                if elem is not None and elem.text:
                    result['기본정보'][field] = elem.text
            
            # 조문 추출
            for article in root.findall('.//조문'):
                article_info = {}
                article_fields = [
                    '조문번호', '조문가지번호', '조문제목', '조문내용',
                    '조문시행일자', '조문제개정유형', '조문변경여부'
                ]
                
                for field in article_fields:
                    elem = article.find(field)
                    if elem is not None and elem.text:
                        article_info[field] = elem.text
                
                # 항 추출
                article_info['항'] = []
                for para in article.findall('.//항'):
                    para_info = {}
                    para_fields = ['항번호', '항내용', '항제개정유형']
                    for field in para_fields:
                        elem = para.find(field)
                        if elem is not None and elem.text:
                            para_info[field] = elem.text
                    
                    # 호 추출
                    para_info['호'] = []
                    for item in para.findall('.//호'):
                        item_info = {}
                        item_fields = ['호번호', '호내용']
                        for field in item_fields:
                            elem = item.find(field)
                            if elem is not None and elem.text:
                                item_info[field] = elem.text
                        if item_info:
                            para_info['호'].append(item_info)
                    
                    if para_info:
                        article_info['항'].append(para_info)
                
                if article_info:
                    result['조문'].append(article_info)
            
            # 부칙 추출
            for addendum in root.findall('.//부칙'):
                add_info = {}
                add_fields = ['부칙공포일자', '부칙공포번호', '부칙내용']
                for field in add_fields:
                    elem = addendum.find(field)
                    if elem is not None and elem.text:
                        add_info[field] = elem.text
                if add_info:
                    result['부칙'].append(add_info)
            
            # 별표 추출
            for table in root.findall('.//별표'):
                table_info = {}
                table_fields = [
                    '별표번호', '별표가지번호', '별표구분', '별표제목',
                    '별표내용', '별표서식파일링크', '별표HWP파일명',
                    '별표서식PDF파일링크', '별표PDF파일명'
                ]
                for field in table_fields:
                    elem = table.find(field)
                    if elem is not None and elem.text:
                        table_info[field] = elem.text
                if table_info:
                    result['별표'].append(table_info)
            
            # 개정문 및 제개정이유
            revision_elem = root.find('.//개정문내용')
            if revision_elem is not None and revision_elem.text:
                result['개정문'] = revision_elem.text
            
            reason_elem = root.find('.//제개정이유내용')
            if reason_elem is not None and reason_elem.text:
                result['제개정이유'] = reason_elem.text
            
            return result
            
        except ET.ParseError as e:
            print(f"❌ XML 파싱 오류: {e}")
            return {}
    
    def interactive_search(self):
        """대화형 검색 및 상세 조회"""
        print("\n" + "=" * 60)
        print("🔍 법제처 법령 고급 검색 시스템")
        print("=" * 60)
        
        while True:
            print("\n메뉴:")
            print("1. 법령 검색")
            print("2. 법령 ID/MST로 직접 조회")
            print("3. 특정 조문 조회")
            print("q. 종료")
            
            choice = input("\n선택: ").strip().lower()
            
            if choice == 'q':
                print("\n👋 종료합니다")
                break
            
            elif choice == '1':
                self.search_menu()
            
            elif choice == '2':
                self.direct_lookup_menu()
            
            elif choice == '3':
                self.article_lookup_menu()
    
    def search_menu(self):
        """검색 메뉴"""
        query = input("\n검색어 입력: ").strip()
        if not query:
            return
        
        results = self.search_law(query)
        if not results or not results['laws']:
            print("❌ 검색 결과가 없습니다")
            return
        
        print(f"\n✅ 총 {results['total_count']}건 검색됨")
        print("-" * 60)
        
        # 최대 10개 표시
        for i, law in enumerate(results['laws'][:10], 1):
            print(f"\n[{i}] {law.get('법령명한글', '')}")
            print(f"    ID: {law.get('법령ID', 'N/A')} / MST: {law.get('법령일련번호', 'N/A')}")
            print(f"    시행일: {law.get('시행일자', '')} / 소관: {law.get('소관부처명', '')}")
        
        choice = input("\n상세 조회할 번호 (0: 취소): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= min(10, len(results['laws'])):
            selected = results['laws'][int(choice) - 1]
            self.detail_menu(selected)
    
    def direct_lookup_menu(self):
        """직접 조회 메뉴"""
        print("\n법령 ID 또는 MST 번호 입력")
        id_type = input("1. 법령 ID / 2. MST 번호: ").strip()
        
        if id_type == '1':
            law_id = input("법령 ID: ").strip()
            if law_id:
                self.detail_menu({'법령ID': law_id})
        elif id_type == '2':
            mst = input("MST 번호: ").strip()
            if mst:
                self.detail_menu({'법령일련번호': mst})
    
    def article_lookup_menu(self):
        """특정 조문 조회 메뉴"""
        print("\n특정 조문 조회")
        
        # 법령 식별
        id_type = input("1. 법령 ID / 2. MST 번호: ").strip()
        law_id = None
        mst = None
        
        if id_type == '1':
            law_id = input("법령 ID: ").strip()
        elif id_type == '2':
            mst = input("MST 번호: ").strip()
        
        if not law_id and not mst:
            return
        
        # 조번호 입력
        print("\n조번호 입력 (예: 2조=2, 10조의2=10-2)")
        jo_input = input("조번호: ").strip()
        
        # 조번호 변환 (2 → 000200, 10-2 → 001002)
        jo_num = None
        if jo_input:
            if '-' in jo_input:
                main, sub = jo_input.split('-')
                jo_num = f"{int(main):04d}{int(sub):02d}"
            else:
                jo_num = f"{int(jo_input):04d}00"
        
        # 언어 선택
        lang = input("언어 (1. 한글 / 2. 원문): ").strip()
        lang_code = 'ORI' if lang == '2' else None
        
        # 형식 선택
        fmt = input("출력 형식 (1. XML / 2. JSON / 3. HTML): ").strip()
        output_type = {'1': 'XML', '2': 'JSON', '3': 'HTML'}.get(fmt, 'XML')
        
        # 조회 실행
        result = self.get_law_detail(
            law_id=law_id,
            mst=mst,
            output_type=output_type,
            jo_num=jo_num,
            lang=lang_code
        )
        
        if result:
            self.save_result(result, f"조문_{jo_num or '전체'}", output_type, law_name="직접조회")
    
    def detail_menu(self, law_info: Dict):
        """상세 조회 메뉴"""
        law_name = law_info.get('법령명한글', '법령')
        law_id = law_info.get('법령ID')
        mst = law_info.get('법령일련번호')
        
        print(f"\n📋 {law_name} 상세 조회 옵션")
        print("-" * 40)
        print("1. 전체 조문 (XML)")
        print("2. 전체 조문 (JSON)")
        print("3. 전체 조문 (HTML)")
        print("4. 구조화된 분석 (조문/부칙/별표 분리)")
        print("5. 특정 조문만 조회")
        print("6. 원문 조회")
        print("0. 취소")
        
        choice = input("\n선택: ").strip()
        
        if choice == '0':
            return
        
        output_type = None
        jo_num = None
        lang = None
        
        if choice in ['1', '2', '3']:
            output_type = {'1': 'XML', '2': 'JSON', '3': 'HTML'}[choice]
        elif choice == '4':
            output_type = 'XML'
        elif choice == '5':
            jo_input = input("조번호 (예: 2, 10-2): ").strip()
            if jo_input:
                if '-' in jo_input:
                    main, sub = jo_input.split('-')
                    jo_num = f"{int(main):04d}{int(sub):02d}"
                else:
                    jo_num = f"{int(jo_input):04d}00"
            output_type = 'XML'
        elif choice == '6':
            output_type = 'XML'
            lang = 'ORI'
        else:
            return
        
        # 조회 실행
        result = self.get_law_detail(
            law_id=law_id,
            mst=mst,
            output_type=output_type,
            jo_num=jo_num,
            lang=lang
        )
        
        if result:
            if choice == '4' and output_type == 'XML':
                # 구조화된 분석
                parsed = self.parse_law_detail_xml(result)
                self.display_structured_result(parsed)
                self.save_result(parsed, "구조화분석", 'JSON', law_name=law_name)
            else:
                # 일반 저장
                suffix = ""
                if jo_num:
                    suffix += f"_조{jo_num}"
                if lang:
                    suffix += "_원문"
                self.save_result(result, f"전체조문{suffix}", output_type, law_name=law_name)
    
    def display_structured_result(self, parsed: Dict):
        """구조화된 결과 표시"""
        print("\n" + "=" * 60)
        print("📊 법령 구조 분석 결과")
        print("=" * 60)
        
        # 기본 정보
        if parsed.get('기본정보'):
            print("\n[기본 정보]")
            for key, value in parsed['기본정보'].items():
                print(f"  {key}: {value}")
        
        # 조문 수
        if parsed.get('조문'):
            print(f"\n[조문] 총 {len(parsed['조문'])}개")
            # 처음 3개만 미리보기
            for article in parsed['조문'][:3]:
                title = article.get('조문제목', '')
                num = article.get('조문번호', '')
                print(f"  제{num}조: {title}")
            if len(parsed['조문']) > 3:
                print(f"  ... 외 {len(parsed['조문']) - 3}개")
        
        # 부칙
        if parsed.get('부칙'):
            print(f"\n[부칙] 총 {len(parsed['부칙'])}개")
        
        # 별표
        if parsed.get('별표'):
            print(f"\n[별표] 총 {len(parsed['별표'])}개")
            for table in parsed['별표'][:3]:
                title = table.get('별표제목', '')
                print(f"  - {title}")
        
        # 개정문/제개정이유
        if parsed.get('개정문'):
            print("\n[개정문] 있음")
        if parsed.get('제개정이유'):
            print("[제개정이유] 있음")
    
    def sanitize_data(self, data: Any) -> Any:
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
    
    def save_result(self, data: Any, filename_base: str, output_type: str, law_name: str = None):
        """
        결과 저장 (실행시간 기준 폴더 구조)
        
        Args:
            data: 저장할 데이터
            filename_base: 파일명 기본
            output_type: 출력 형식
            law_name: 법령명 (파일명에 포함)
        """
        # 실행 시간 기준 폴더
        save_dir = f"_cache/{self.session_folder}"
        
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 파일명 안전하게 만들기 (법령명 포함)
        if law_name:
            safe_law_name = law_name.replace('/', '_').replace('\\', '_')
            safe_name = f"{safe_law_name}_{filename_base}"
        else:
            safe_name = filename_base
        safe_name = safe_name.replace('/', '_').replace('\\', '_')
        
        # 저장 전 민감정보 제거
        clean_data = self.sanitize_data(data)
        
        if output_type == 'JSON' or isinstance(clean_data, dict):
            filename = f"{save_dir}/{safe_name}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(clean_data, dict):
                    json.dump(clean_data, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(clean_data))
        elif output_type == 'XML':
            filename = f"{save_dir}/{safe_name}_{timestamp}.xml"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(clean_data) if not isinstance(clean_data, str) else clean_data)
        elif output_type == 'HTML':
            filename = f"{save_dir}/{safe_name}_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(clean_data) if not isinstance(clean_data, str) else clean_data)
        else:
            filename = f"{save_dir}/{safe_name}_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(clean_data))
        
        print(f"✅ {filename} 저장 완료 ({len(str(clean_data)):,} bytes)")

def main():
    client = AdvancedLawAPIClient()
    client.interactive_search()

if __name__ == "__main__":
    main()