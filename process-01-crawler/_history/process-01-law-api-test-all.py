#!/usr/bin/env python3
"""
법제처 Open API 전체 엔드포인트 테스트
Version 1.0.0 (2025-01-11)
- lawapi_guide.md 기반 모든 API 엔드포인트 테스트
- 각 API의 작동 여부 및 응답 형식 확인
"""

import requests
import xml.etree.ElementTree as ET
import json
import yaml
import os
from datetime import datetime
from typing import Dict, Any

class LawAPIComprehensiveTester:
    def __init__(self):
        """YAML 파일에서 설정 로드"""
        self.config = self.load_config()
        self.email_id = self.config.get('email_id')
        
        if not self.email_id or self.email_id == 'YOUR_EMAIL_ID_HERE':
            print("⚠️ API_law.yaml 파일에 이메일 ID를 입력해주세요!")
            self.email_id = input("임시로 사용할 이메일 ID 입력: ").strip() or "test"
        
        # 이메일에서 @ 앞부분만 추출
        if '@' in self.email_id:
            self.email_id = self.email_id.split('@')[0]
        
        self.base_url = "http://www.law.go.kr/DRF"
        self.test_results = []
        # 실행 시간 기준 폴더명 생성
        self.session_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"✅ API 테스터 초기화 완료")
    
    def load_config(self) -> Dict:
        """YAML 설정 파일 로드"""
        config_file = 'API_law.yaml'
        
        if not os.path.exists(config_file):
            return {'email_id': 'test'}
        
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
    
    def test_api_endpoint(self, name: str, url: str, params: Dict, 
                          expected_format: str = 'XML') -> Dict:
        """
        API 엔드포인트 테스트
        
        Returns:
            테스트 결과 딕셔너리
        """
        result = {
            'name': name,
            'url': url,
            'params': params,
            'status': 'FAIL',
            'response_code': None,
            'response_size': 0,
            'error': None,
            'sample_data': None
        }
        
        try:
            print(f"\n🔍 테스트: {name}")
            print(f"   URL: {url}")
            print(f"   Params: {params}")
            
            response = requests.get(url, params=params, timeout=10)
            result['response_code'] = response.status_code
            result['response_size'] = len(response.content)
            
            if response.status_code == 200:
                # 응답 형식 확인
                if expected_format == 'XML':
                    try:
                        root = ET.fromstring(response.content)
                        result['status'] = 'SUCCESS'
                        # 샘플 데이터 추출
                        result['sample_data'] = self.extract_xml_sample(root)
                    except ET.ParseError as e:
                        result['status'] = 'PARSE_ERROR'
                        result['error'] = str(e)[:100]
                
                elif expected_format == 'JSON':
                    try:
                        data = response.json()
                        result['status'] = 'SUCCESS'
                        result['sample_data'] = self.extract_json_sample(data)
                    except json.JSONDecodeError as e:
                        result['status'] = 'PARSE_ERROR'
                        result['error'] = str(e)[:100]
                
                elif expected_format == 'HTML':
                    if '<html' in response.text.lower() or '<!doctype' in response.text.lower():
                        result['status'] = 'SUCCESS'
                        result['sample_data'] = 'HTML 응답 확인'
                    else:
                        result['status'] = 'UNEXPECTED_FORMAT'
                
                print(f"   ✅ 상태: {result['status']} ({result['response_size']:,} bytes)")
            else:
                result['error'] = f"HTTP {response.status_code}"
                print(f"   ❌ HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
            print(f"   ⏱️ 타임아웃")
        except Exception as e:
            result['error'] = str(e)[:100]
            print(f"   ❌ 오류: {result['error']}")
        
        self.test_results.append(result)
        return result
    
    def extract_xml_sample(self, root: ET.Element) -> Dict:
        """XML에서 샘플 데이터 추출"""
        sample = {}
        
        # 전체 건수 찾기
        total = root.find('.//totalCnt')
        if total is not None and total.text:
            sample['totalCnt'] = total.text
        
        # 첫 번째 결과 찾기
        for tag in ['law', 'prec', 'cons', 'expc', 'admr', 'ftc', 'acr', 'ppc']:
            first = root.find(f'.//{tag}')
            if first is not None:
                sample['first_item_type'] = tag
                # 주요 필드 추출
                for field in ['법령명한글', '사건명', '안건명', '민원표시']:
                    elem = first.find(field)
                    if elem is not None and elem.text:
                        sample['first_item_name'] = elem.text
                        break
                break
        
        return sample if sample else {'note': 'XML 구조 확인됨'}
    
    def extract_json_sample(self, data: Any) -> Dict:
        """JSON에서 샘플 데이터 추출"""
        sample = {}
        
        if isinstance(data, dict):
            if 'totalCnt' in data:
                sample['totalCnt'] = data['totalCnt']
            if 'list' in data and isinstance(data['list'], list) and data['list']:
                sample['first_item'] = data['list'][0].get('법령명한글', 
                                      data['list'][0].get('사건명', '항목'))[:50]
        
        return sample if sample else {'note': 'JSON 구조 확인됨'}
    
    def test_law_apis(self):
        """법령 관련 API 테스트"""
        print("\n" + "="*60)
        print("📚 법령 관련 API 테스트")
        print("="*60)
        
        # 1. 현행법령 목록 조회
        self.test_api_endpoint(
            "현행법령 목록 조회 (XML)",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'law',
                'type': 'XML',
                'query': '법인세법',
                'display': '5'
            },
            'XML'
        )
        
        # 2. 현행법령 본문 조회
        self.test_api_endpoint(
            "현행법령 본문 조회 (XML)",
            f"{self.base_url}/lawService.do",
            {
                'OC': self.email_id,
                'target': 'law',
                'type': 'XML',
                'ID': '001823'  # 건축법 예시
            },
            'XML'
        )
        
        # 3. 시행일 법령 목록
        self.test_api_endpoint(
            "시행일 법령 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'eflaw',
                'type': 'XML',
                'query': '법인세법',
                'display': '5'
            },
            'XML'
        )
        
        # 4. 법령 연혁 목록
        self.test_api_endpoint(
            "법령 연혁 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'lsHistory',
                'type': 'HTML',
                'query': '법인세법'
            },
            'HTML'
        )
        
        # 5. 조항호목 단위 조회
        self.test_api_endpoint(
            "조항호목 단위 조회",
            f"{self.base_url}/lawService.do",
            {
                'OC': self.email_id,
                'target': 'lawjosub',
                'type': 'XML',
                'ID': '001823',
                'JO': '000300'  # 제3조
            },
            'XML'
        )
        
        # 6. 위임 법령 조회
        self.test_api_endpoint(
            "위임 법령 조회",
            f"{self.base_url}/lawService.do",
            {
                'OC': self.email_id,
                'target': 'lsDelegated',
                'type': 'XML',
                'ID': '000900'  # 초중등교육법
            },
            'XML'
        )
    
    def test_english_apis(self):
        """영문법령 API 테스트"""
        print("\n" + "="*60)
        print("🌐 영문법령 API 테스트")
        print("="*60)
        
        self.test_api_endpoint(
            "영문법령 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'elaw',
                'type': 'XML',
                'display': '5'
            },
            'XML'
        )
    
    def test_case_apis(self):
        """판례/결정례 API 테스트"""
        print("\n" + "="*60)
        print("⚖️ 판례/결정례 API 테스트")
        print("="*60)
        
        # 판례
        self.test_api_endpoint(
            "판례 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'prec',
                'type': 'XML',
                'query': '손해배상',
                'display': '5'
            },
            'XML'
        )
        
        # 헌재결정례 (추정)
        self.test_api_endpoint(
            "헌재결정례 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'cons',
                'type': 'XML',
                'display': '5'
            },
            'XML'
        )
        
        # 법령해석례 (추정)
        self.test_api_endpoint(
            "법령해석례 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'expc',
                'type': 'XML',
                'display': '5'
            },
            'XML'
        )
        
        # 행정심판례 (추정)
        self.test_api_endpoint(
            "행정심판례 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'admr',
                'type': 'XML',
                'display': '5'
            },
            'XML'
        )
    
    def test_committee_apis(self):
        """위원회 결정문 API 테스트"""
        print("\n" + "="*60)
        print("🏛️ 위원회 결정문 API 테스트")
        print("="*60)
        
        committees = [
            ('공정거래위원회', 'ftc'),
            ('국민권익위원회', 'acr'),
            ('개인정보보호위원회', 'ppc'),
            ('국가인권위원회', 'nhrck'),
        ]
        
        for name, target in committees:
            self.test_api_endpoint(
                f"{name} 결정문 목록",
                f"{self.base_url}/lawSearch.do",
                {
                    'OC': self.email_id,
                    'target': target,
                    'type': 'XML',
                    'display': '5'
                },
                'XML'
            )
    
    def test_additional_apis(self):
        """부가서비스 API 테스트"""
        print("\n" + "="*60)
        print("📊 부가서비스 API 테스트")
        print("="*60)
        
        # 법령 체계도
        self.test_api_endpoint(
            "법령 체계도 목록",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'lsStmd',
                'type': 'XML',
                'query': '법인세법'
            },
            'XML'
        )
        
        # 신구법 (추정)
        self.test_api_endpoint(
            "신구법 목록 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'lsRvs',
                'type': 'HTML',
                'query': '법인세법'
            },
            'HTML'
        )
        
        # 법령용어 (추정)
        self.test_api_endpoint(
            "법령용어 조회",
            f"{self.base_url}/lawSearch.do",
            {
                'OC': self.email_id,
                'target': 'lawterm',
                'type': 'XML',
                'query': '과세'
            },
            'XML'
        )
    
    def generate_report(self):
        """테스트 결과 리포트 생성"""
        print("\n" + "="*60)
        print("📋 테스트 결과 요약")
        print("="*60)
        
        # 통계
        total = len(self.test_results)
        success = sum(1 for r in self.test_results if r['status'] == 'SUCCESS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        parse_error = sum(1 for r in self.test_results if r['status'] == 'PARSE_ERROR')
        
        print(f"\n전체: {total}개")
        print(f"✅ 성공: {success}개")
        print(f"❌ 실패: {failed}개")
        print(f"⚠️ 파싱오류: {parse_error}개")
        
        # 상세 결과
        print("\n상세 결과:")
        print("-" * 60)
        
        for result in self.test_results:
            status_icon = {
                'SUCCESS': '✅',
                'FAIL': '❌',
                'PARSE_ERROR': '⚠️',
                'UNEXPECTED_FORMAT': '❓'
            }.get(result['status'], '?')
            
            print(f"\n{status_icon} {result['name']}")
            print(f"   상태: {result['status']}")
            if result['response_code']:
                print(f"   응답코드: {result['response_code']}")
            if result['response_size'] > 0:
                print(f"   응답크기: {result['response_size']:,} bytes")
            if result['error']:
                print(f"   오류: {result['error']}")
            if result['sample_data']:
                print(f"   샘플: {result['sample_data']}")
        
        # 결과 저장
        self.save_report()
    
    def save_report(self):
        """테스트 결과 저장"""
        save_dir = f'_cache/{self.session_folder}'
        os.makedirs(save_dir, exist_ok=True)
        
        # 민감한 정보 제거
        clean_results = []
        for result in self.test_results:
            clean_result = result.copy()
            # params에서 OC 값 제거
            if 'params' in clean_result and 'OC' in clean_result['params']:
                clean_result['params'] = {k: v for k, v in clean_result['params'].items() if k != 'OC'}
            clean_results.append(clean_result)
        
        # JSON 형식으로 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'{save_dir}/API테스트결과_{timestamp}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_time': timestamp,
                'total_tests': len(clean_results),
                'results': clean_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 리포트 저장: {report_file}")
        
        # 작동하는 API 목록 저장 (민감정보 제거)
        working_apis = []
        for r in clean_results:
            if r['status'] == 'SUCCESS':
                working_apis.append(r)
        
        if working_apis:
            working_file = f'{save_dir}/작동API목록_{timestamp}.json'
            with open(working_file, 'w', encoding='utf-8') as f:
                json.dump(working_apis, f, ensure_ascii=False, indent=2)
            print(f"💾 작동 API 목록: {working_file}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "="*60)
        print("🚀 법제처 Open API 전체 엔드포인트 테스트 시작")
        print("="*60)
        
        # 각 카테고리별 테스트
        self.test_law_apis()
        self.test_english_apis()
        self.test_case_apis()
        self.test_committee_apis()
        self.test_additional_apis()
        
        # 리포트 생성
        self.generate_report()
        
        print("\n✅ 테스트 완료!")

def main():
    tester = LawAPIComprehensiveTester()
    
    print("테스트 옵션:")
    print("1. 전체 API 테스트 (모든 엔드포인트)")
    print("2. 법령 API만 테스트")
    print("3. 판례/결정례 API만 테스트")
    print("4. 위원회 API만 테스트")
    print("5. 부가서비스 API만 테스트")
    
    choice = input("\n선택 (1-5): ").strip()
    
    if choice == '1':
        tester.run_all_tests()
    elif choice == '2':
        tester.test_law_apis()
        tester.generate_report()
    elif choice == '3':
        tester.test_case_apis()
        tester.generate_report()
    elif choice == '4':
        tester.test_committee_apis()
        tester.generate_report()
    elif choice == '5':
        tester.test_additional_apis()
        tester.generate_report()
    else:
        print("잘못된 선택입니다. 전체 테스트를 실행합니다.")
        tester.run_all_tests()

if __name__ == "__main__":
    main()