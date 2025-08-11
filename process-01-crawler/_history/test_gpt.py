#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국가법령정보 OPEN API - 전체 엔드포인트 샘플 호출 테스트 스크립트
Version 2.0.0 (2025-01-11)
- 목록 페이지를 파싱해 모든 가이드(guideResult) 페이지를 수집
- 각 가이드에서 '샘플 URL'을 자동 추출 후 호출
- API_law.yaml 설정 파일 지원 (없으면 OC=test 사용)
- 민감정보 자동 제거 기능 추가
- 사용 시: python test_gpt.py
"""
import os
import re
import time
import json
import html
import yaml
import random
import pathlib
import urllib.parse as urlparse
from datetime import datetime
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup

GUIDE_LIST_URL = "https://open.law.go.kr/LSO/openApi/guideList.do"
GUIDE_BASE     = "https://open.law.go.kr"
USER_AGENT     = "Mozilla/5.0 (compatible; OpenLawAPITester/2.0; +https://open.law.go.kr)"
TIMEOUT_SEC    = 15
SLEEP_SEC      = 0.5   # 서버 배려용(무리한 동시호출 지양)

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

def ensure_dir(p: str):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def load_config() -> Dict:
    """YAML 설정 파일 로드"""
    config_file = 'API_law.yaml'
    
    if not os.path.exists(config_file):
        print("ℹ️ API_law.yaml 파일이 없습니다. test 키를 사용합니다.")
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
        print(f"⚠️ YAML 파일 읽기 오류: {e}")
        return {'email_id': 'test'}

def sanitize_data(data: Any) -> Any:
    """
    민감정보 제거 (재귀적)
    - OC 파라미터 제거
    - 이메일 패턴 마스킹
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # OC 관련 필드 제거
            if key.upper() == 'OC' or key == 'email_id':
                continue
            # URL에서 OC 파라미터 제거
            if key in ['url', 'guide_url', 'sample_url'] and isinstance(value, str):
                value = re.sub(r'[?&]OC=[^&]*', '', value)
            # 값에서도 재귀적으로 제거
            cleaned[key] = sanitize_data(value)
        return cleaned
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, str):
        # 이메일 패턴 마스킹
        return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', data)
    else:
        return data

def slugify(text: str) -> str:
    text = re.sub(r"\s+", "_", text.strip())
    text = re.sub(r"[^\w\-\.]+", "_", text, flags=re.UNICODE)
    return text.strip("_")[:120]

def get(url: str) -> requests.Response:
    return session.get(url, timeout=TIMEOUT_SEC, allow_redirects=True)

def find_all_guide_pages(list_html: str):
    """
    guideList 페이지에서 모든 guideResult.do?htmlName=... 링크를 추출
    - onclick="javascript:openApiGuide('...')" 형식으로 되어 있음
    """
    # onclick 패턴에서 htmlName 추출
    html_names = set(re.findall(r"openApiGuide\(['\"]([A-Za-z0-9_]+)['\"]\)", list_html))
    
    # guideResult.do?htmlName= 패턴도 추가로 확인
    html_names.update(re.findall(r"guideResult\.do\?htmlName=([A-Za-z0-9_]+)", list_html))
    
    guides = [f"{GUIDE_BASE}/LSO/openApi/guideResult.do?htmlName={name}" for name in sorted(html_names)]
    return guides

def parse_guide_page(url: str):
    """
    가이드(detail) 페이지에서 제목/요청URL/샘플URL들 추출
    - 페이지 구조가 다양할 수 있어 완화된 파서 사용
    """
    r = get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    # 대략적인 제목
    title = None
    h = soup.find(["h2", "h3"])
    if h:
        title = h.get_text(strip=True)
    if not title:
        # 백업: 첫 줄에서 'API' 단어 포함 라인
        for line in text.splitlines():
            if "API" in line or "가이드" in line:
                title = line.strip()
                break
    if not title:
        title = url

    # 요청 URL (페이지에 "요청 URL" 패턴 존재)
    req_urls = re.findall(r"(https?://[^\s]+?lawService\.do[^\s]*)", text) \
             + re.findall(r"(https?://[^\s]+?lawSearch\.do[^\s]*)", text)
    req_urls = [u.rstrip(") ,") for u in req_urls]

    # 샘플 URL 섹션에서 링크 추출 (a[href] 우선)
    sample_urls = []
    for a in soup.find_all("a", href=True):
        href = html.unescape(a["href"])
        if "law.go.kr/DRF/" in href or "/DRF/" in href or "lawService.do" in href or "lawSearch.do" in href:
            if href.startswith("/"):
                href = urlparse.urljoin("http://www.law.go.kr", href)
            sample_urls.append(href)

    # 본문 텍스트 속 URL도 훑기
    text_urls = re.findall(r"(https?://[^\s\"'<>]+\blaw(?:Service|Search)\.do[^\s\"'<>]*)", text)
    sample_urls.extend(text_urls)

    # 정리
    def norm(u: str) -> str:
        u = u.replace("&amp;", "&")
        u = u.strip().rstrip(").,]")
        return u
    sample_urls = [norm(u) for u in sample_urls]
    # 샘플 URL만 남기고 중복 제거
    sample_urls = list(dict.fromkeys([u for u in sample_urls if "law.go.kr/DRF" in u]))

    return {
        "title": title,
        "guide_url": url,
        "request_urls": list(dict.fromkeys(req_urls)),
        "sample_urls": sample_urls,
        "html": r.text,
    }

def ensure_oc_param(u: str, oc_value: str = None) -> str:
    """
    샘플 URL에 OC 파라미터가 빠져 있으면 추가.
    또 type 파라미터가 전혀 없고 lawService/lawSearch면 type=XML을 붙여줍니다(보수적 보정).
    """
    parsed = urlparse.urlparse(u)
    qs = urlparse.parse_qs(parsed.query, keep_blank_values=True)
    changed = False

    if "OC" not in qs:
        # 설정 파일이나 기본값 사용
        if oc_value:
            qs["OC"] = [oc_value]
        else:
            qs["OC"] = ["test"]  # 기본값
        changed = True

    # type이 전혀 없고 DRF 호출이면 XML 기본
    if "type" not in qs and ("lawService.do" in parsed.path or "lawSearch.do" in parsed.path):
        qs["type"] = ["XML"]
        changed = True

    if changed:
        new_q = urlparse.urlencode({k: v[0] for k, v in qs.items()}, doseq=False)
        u = urlparse.urlunparse(parsed._replace(query=new_q))
    return u

def save_response(name_slug: str, resp: requests.Response, url: str, out_dir: str):
    ct = (resp.headers.get("Content-Type") or "").lower()
    # 확장자 추정
    if "json" in ct:
        ext = "json"
    elif "html" in ct:
        ext = "html"
    else:
        # 대부분 XML
        ext = "xml"
    safe_name = name_slug[:80]
    path = os.path.join(out_dir, f"{safe_name}.{ext}")
    
    try:
        # 텍스트로 디코딩 시도
        content = resp.text
        # OC 파라미터 제거
        content = re.sub(r'[?&]OC=[^&"\s]*', '', content)
        content = re.sub(r'<OC>[^<]*</OC>', '', content)  # XML 태그 내 OC 제거
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except:
        # 바이너리 데이터인 경우 그대로 저장
        with open(path, "wb") as f:
            f.write(resp.content)
    
    return path

def main():
    print("="*60)
    print("🚀 법제처 Open API 전체 엔드포인트 테스트")
    print("="*60)
    
    # 설정 로드
    config = load_config()
    email_id = config.get('email_id', 'test')
    
    # 이메일에서 @ 앞부분만 추출
    if '@' in email_id:
        email_id = email_id.split('@')[0]
    
    # 실행 시간 기준 폴더명 생성
    session_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = f'_cache/{session_folder}'
    
    print(f"ℹ️ 사용할 OC 값: {'***' if email_id != 'test' else 'test'}")
    print(f"📁 결과 저장 폴더: {out_dir}")
    print()
    
    print(f"[1/4] 목록 페이지 요청 → {GUIDE_LIST_URL}")
    r = get(GUIDE_LIST_URL)
    r.raise_for_status()
    guides = find_all_guide_pages(r.text)
    print(f"  - guideResult 페이지 수집: {len(guides)}개 발견")

    ensure_dir(out_dir)
    meta = []
    fail_records = []

    for idx, g in enumerate(guides, 1):
        print(f"\n[2/4] ({idx}/{len(guides)}) 가이드 분석 → {g}")
        try:
            info = parse_guide_page(g)
        except Exception as e:
            print(f"  ! 가이드 파싱 실패: {e}")
            fail_records.append({"stage": "parse", "guide": g, "error": str(e)})
            continue

        title = info["title"]
        samples = info["sample_urls"]
        print(f"  - 제목: {title}")
        print(f"  - 샘플 URL: {len(samples)}개 발견")

        # 샘플이 하나도 없으면 요청URL을 참고해서 보수적으로 1건 만들어 본다(가능할 때만)
        if not samples and info["request_urls"]:
            # 요청URL이 search/service 인지 보고 최소 파라미터를 붙인다.
            for req_url in info["request_urls"]:
                if "lawService.do" in req_url or "lawSearch.do" in req_url:
                    # 그냥 OC=test&type=XML 추가 (일부는 ID 등 추가필수 → 400/에러 가능)
                    u = req_url
                    joiner = "&" if ("?" in u) else "?"
                    samples.append(f"{u}{joiner}OC=test&type=XML")
                    break

        # 샘플 호출
        if not samples:
            print("  - 호출 샘플이 없어 SKIP")
            meta.append({"guide": g, "title": title, "called": 0, "ok": 0})
            continue

        ok = 0
        for sidx, su in enumerate(samples, 1):
            url_fixed = ensure_oc_param(su, email_id)
            # 출력시 OC 값 마스킹
            display_url = re.sub(r'OC=[^&]*', 'OC=***', url_fixed)
            print(f"    [{sidx}/{len(samples)}] CALL → {display_url}")
            try:
                time.sleep(SLEEP_SEC + random.uniform(0, 0.3))
                resp = get(url_fixed)
                status = resp.status_code
                ctype  = resp.headers.get("Content-Type", "")
                size   = len(resp.content)
                if status == 200 and size > 0:
                    # 가이드 번호를 포함해서 파일명 중복 방지
                    fname = save_response(slugify(f"{title}_{idx}_{sidx}"), resp, url_fixed, out_dir)
                    print(f"      ✅ {status} | {ctype} | {size} bytes → {fname}")
                    ok += 1
                else:
                    print(f"      ❌ {status} | {ctype} | {size} bytes")
                    # URL에서 OC 제거 후 저장
                    clean_url = re.sub(r'[?&]OC=[^&]*', '', url_fixed)
                    fail_records.append({"stage":"call","guide":g,"title":title,"url":clean_url,"status":status,"ctype":ctype,"size":size})
            except Exception as e:
                print(f"      ⚠️ {type(e).__name__}: {e}")
                # URL에서 OC 제거 후 저장
                clean_url = re.sub(r'[?&]OC=[^&]*', '', url_fixed)
                fail_records.append({"stage":"call","guide":g,"title":title,"url":clean_url,"error":str(e)})

        meta.append({"guide": g, "title": title, "called": len(samples), "ok": ok})

    # 결과 요약 저장 (민감정보 제거)
    clean_meta = sanitize_data(meta)
    clean_fails = sanitize_data(fail_records)
    
    summary_path = os.path.join(out_dir, "테스트요약.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_guides": len(meta),
            "meta": clean_meta, 
            "fail": clean_fails
        }, f, ensure_ascii=False, indent=2)
    print("\n[3/4] 요약 저장 →", summary_path)

    # 간단 요약 표
    total_called = sum(m["called"] for m in meta)
    total_ok     = sum(m["ok"]     for m in meta)
    print(f"\n[4/4] 📊 전체 요약")
    print("="*60)
    print(f"✅ 성공: {total_ok}건")
    print(f"❌ 실패: {total_called - total_ok}건")
    print(f"📚 가이드: {len(meta)}건")
    print(f"🔍 전체 호출: {total_called}건")
    
    if fail_records:
        print(f"\n⚠️ 실패 예시 (최대 3건):")
        for rec in fail_records[:3]:
            print(f"  - {rec.get('title', 'Unknown')}: {rec.get('error', rec.get('status', 'Unknown error'))}")
    
    print(f"\n💾 모든 결과가 {out_dir}/ 폴더에 저장되었습니다.")

if __name__ == "__main__":
    main()
