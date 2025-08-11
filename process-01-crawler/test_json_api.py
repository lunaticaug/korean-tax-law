#!/usr/bin/env python3
"""
법제처 API JSON 형식 테스트
- XML, JSON, HTML 형식으로 동일한 법령을 요청하여 비교
"""

import requests
import json
import yaml
import os
from datetime import datetime
import xml.etree.ElementTree as ET

def load_config():
    """API 설정 로드"""
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
            return config if config else {'email_id': 'test'}
    except Exception as e:
        print(f"❌ 설정 파일 오류: {e}")
        return {'email_id': 'test'}

def test_json_api():
    """JSON API 테스트"""
    config = load_config()
    email_id = config.get('email_id', 'test')
    
    # 이메일에서 @ 앞부분만 추출
    if '@' in email_id:
        email_id = email_id.split('@')[0]
    
    base_url = "http://www.law.go.kr/DRF"
    
    # 세션 폴더 생성
    session_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_dir = f'_cache/{session_folder}_json_test'
    os.makedirs(save_dir, exist_ok=True)
    
    print("="*60)
    print("🧪 법제처 API JSON 형식 테스트")
    print("="*60)
    
    # 1. 먼저 법인세법 검색
    print("\n1️⃣ 법인세법 검색 중...")
    search_url = f"{base_url}/lawSearch.do"
    search_params = {
        'OC': email_id,
        'target': 'law',
        'type': 'XML',
        'query': '법인세법',
        'display': '5'
    }
    
    search_resp = requests.get(search_url, params=search_params)
    if search_resp.status_code != 200:
        print(f"❌ 검색 실패: HTTP {search_resp.status_code}")
        return
    
    # XML 파싱하여 법령 ID 추출
    try:
        root = ET.fromstring(search_resp.content)
        law_id = None
        for law in root.findall('.//law'):
            law_name = law.find('법령명한글')
            if law_name is not None and law_name.text == '법인세법':
                law_id = law.find('법령일련번호').text
                print(f"✅ 법인세법 발견: ID={law_id}")
                break
        
        if not law_id:
            print("❌ 법인세법을 찾을 수 없습니다")
            return
    except Exception as e:
        print(f"❌ XML 파싱 오류: {e}")
        return
    
    # 2. 세 가지 형식으로 상세 조회 테스트
    detail_url = f"{base_url}/lawService.do"
    formats = ['XML', 'JSON', 'HTML']
    results = {}
    
    print("\n2️⃣ 각 형식으로 상세 조회 테스트...")
    print("-"*60)
    
    for fmt in formats:
        print(f"\n📋 {fmt} 형식 테스트:")
        
        params = {
            'OC': email_id,
            'target': 'law',
            'type': fmt,
            'MST': law_id
        }
        
        # OC 값 마스킹하여 출력
        display_params = params.copy()
        display_params['OC'] = '***'
        print(f"   요청: {detail_url}")
        print(f"   파라미터: {display_params}")
        
        try:
            resp = requests.get(detail_url, params=params, timeout=10)
            
            print(f"   응답 코드: {resp.status_code}")
            print(f"   Content-Type: {resp.headers.get('Content-Type', 'Unknown')}")
            print(f"   응답 크기: {len(resp.content):,} bytes")
            
            if resp.status_code == 200:
                # 파일 저장
                ext = fmt.lower()
                filename = f"{save_dir}/법인세법_{fmt}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                
                # 민감정보 제거 후 저장
                content = resp.text
                import re
                content = re.sub(r'[?&]OC=[^&"\s]*', '', content)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   💾 저장: {filename}")
                
                # 내용 미리보기
                if fmt == 'JSON':
                    try:
                        json_data = json.loads(content)
                        print(f"   📊 JSON 구조:")
                        print(f"      최상위 키: {list(json_data.keys())[:10]}")
                        
                        # JSON 구조 더 자세히 보기
                        if isinstance(json_data, dict):
                            for key in list(json_data.keys())[:5]:
                                value = json_data[key]
                                if isinstance(value, dict):
                                    print(f"      {key}: {{dict with {len(value)} keys}}")
                                elif isinstance(value, list):
                                    print(f"      {key}: [list with {len(value)} items]")
                                else:
                                    preview = str(value)[:50]
                                    print(f"      {key}: {preview}...")
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️ JSON 파싱 실패: {e}")
                        # 처음 500자 출력
                        print(f"   내용 미리보기: {content[:500]}")
                
                elif fmt == 'XML':
                    # XML 구조 확인
                    try:
                        root = ET.fromstring(content)
                        print(f"   📊 XML 구조:")
                        print(f"      루트 태그: {root.tag}")
                        print(f"      최상위 요소: {[child.tag for child in root[:5]]}")
                    except ET.ParseError as e:
                        print(f"   ⚠️ XML 파싱 실패: {e}")
                
                results[fmt] = True
            else:
                results[fmt] = False
                print(f"   ❌ 실패: HTTP {resp.status_code}")
                
        except Exception as e:
            results[fmt] = False
            print(f"   ❌ 오류: {e}")
    
    # 3. 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    for fmt, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{fmt:8s}: {status}")
    
    print(f"\n💾 결과가 {save_dir}/ 폴더에 저장되었습니다")
    
    # 4. 추가 테스트: JSON으로 검색도 가능한지
    print("\n" + "="*60)
    print("🧪 추가 테스트: 검색 API의 JSON 지원")
    print("="*60)
    
    for fmt in ['XML', 'JSON']:
        print(f"\n📋 {fmt} 형식으로 검색:")
        search_params['type'] = fmt
        
        try:
            resp = requests.get(search_url, params=search_params, timeout=10)
            print(f"   응답 코드: {resp.status_code}")
            print(f"   Content-Type: {resp.headers.get('Content-Type', 'Unknown')}")
            
            if resp.status_code == 200:
                if fmt == 'JSON':
                    try:
                        json_data = json.loads(resp.text)
                        print(f"   ✅ JSON 파싱 성공")
                        print(f"   최상위 키: {list(json_data.keys())[:10]}")
                    except:
                        print(f"   ❌ JSON 파싱 실패")
                        print(f"   내용: {resp.text[:200]}")
                else:
                    print(f"   ✅ 성공")
        except Exception as e:
            print(f"   ❌ 오류: {e}")

if __name__ == "__main__":
    test_json_api()