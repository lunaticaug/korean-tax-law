#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국가법령정보 OPEN API - 전체 엔드포인트 샘플 호출 테스트 스크립트
- 목록 페이지를 파싱해 모든 가이드(guideResult) 페이지를 수집
- 각 가이드에서 '샘플 URL'을 자동 추출 후 호출
- 인증 파라미터는 가이드의 관례대로 OC=test 사용
- 사용 시: python test_openlaw_endpoints.py
"""
import os
import re
import time
import json
import html
import shutil
import random
import pathlib
import urllib.parse as urlparse

import requests
from bs4 import BeautifulSoup

GUIDE_LIST_URL = "https://open.law.go.kr/LSO/openApi/guideList.do"
GUIDE_BASE     = "https://open.law.go.kr"
OUT_DIR        = "openlaw_api_test_out"
USER_AGENT     = "Mozilla/5.0 (compatible; OpenLawAPITester/1.0; +https://open.law.go.kr)"
TIMEOUT_SEC    = 15
SLEEP_SEC      = 0.5   # 서버 배려용(무리한 동시호출 지양)

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

def ensure_dir(p: str):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def slugify(text: str) -> str:
    text = re.sub(r"\s+", "_", text.strip())
    text = re.sub(r"[^\w\-\.]+", "_", text, flags=re.UNICODE)
    return text.strip("_")[:120]

def get(url: str) -> requests.Response:
    return session.get(url, timeout=TIMEOUT_SEC, allow_redirects=True)

def find_all_guide_pages(list_html: str):
    """
    guideList 페이지에서 모든 guideResult.do?htmlName=... 링크를 추출
    - 일부는 a[href], 일부는 onclick 등으로 있을 수 있어 전체 HTML에서 정규식으로 긁습니다.
    """
    html_names = set(re.findall(r"guideResult\.do\?htmlName=([A-Za-z0-9_]+)", list_html))
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

def ensure_oc_param(u: str) -> str:
    """
    샘플 URL에 OC 파라미터가 빠져 있으면 OC=test 추가.
    또 type 파라미터가 전혀 없고 lawService/lawSearch면 type=XML을 붙여줍니다(보수적 보정).
    """
    parsed = urlparse.urlparse(u)
    qs = urlparse.parse_qs(parsed.query, keep_blank_values=True)
    changed = False

    if "OC" not in qs:
        qs["OC"] = ["test"]  # 가이드에서 쓰는 샘플 OC
        changed = True

    # type이 전혀 없고 DRF 호출이면 XML 기본
    if "type" not in qs and ("lawService.do" in parsed.path or "lawSearch.do" in parsed.path):
        qs["type"] = ["XML"]
        changed = True

    if changed:
        new_q = urlparse.urlencode({k: v[0] for k, v in qs.items()}, doseq=False)
        u = urlparse.urlunparse(parsed._replace(query=new_q))
    return u

def save_response(name_slug: str, resp: requests.Response, url: str):
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
    path = os.path.join(OUT_DIR, f"{safe_name}.{ext}")
    with open(path, "wb") as f:
        f.write(resp.content)
    return path

def main():
    print(f"[1/4] 목록 페이지 요청 → {GUIDE_LIST_URL}")
    r = get(GUIDE_LIST_URL)
    r.raise_for_status()
    guides = find_all_guide_pages(r.text)
    print(f"  - guideResult 페이지 수집: {len(guides)}개 발견")

    ensure_dir(OUT_DIR)
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
            url_fixed = ensure_oc_param(su)
            print(f"    [{sidx}/{len(samples)}] CALL → {url_fixed}")
            try:
                time.sleep(SLEEP_SEC + random.uniform(0, 0.3))
                resp = get(url_fixed)
                status = resp.status_code
                ctype  = resp.headers.get("Content-Type", "")
                size   = len(resp.content)
                if status == 200 and size > 0:
                    fname = save_response(slugify(f"{title}_{sidx}"), resp, url_fixed)
                    print(f"      OK {status} | {ctype} | {size} bytes → {fname}")
                    ok += 1
                else:
                    print(f"      FAIL {status} | {ctype} | {size} bytes")
                    fail_records.append({"stage":"call","guide":g,"title":title,"url":url_fixed,"status":status,"ctype":ctype,"size":size})
            except Exception as e:
                print(f"      EXC {type(e).__name__}: {e}")
                fail_records.append({"stage":"call","guide":g,"title":title,"url":url_fixed,"error":str(e)})

        meta.append({"guide": g, "title": title, "called": len(samples), "ok": ok})

    # 결과 요약 저장
    summary_path = os.path.join(OUT_DIR, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "fail": fail_records}, f, ensure_ascii=False, indent=2)
    print("\n[3/4] 요약 저장 →", summary_path)

    # 간단 요약 표
    total_called = sum(m["called"] for m in meta)
    total_ok     = sum(m["ok"]     for m in meta)
    print(f"[4/4] 전체 요약: 가이드 {len(meta)}건, 샘플 호출 {total_called}건, 성공 {total_ok}건, 실패 {total_called - total_ok}건")
    if fail_records:
        print("  - 실패 예시 3건:")
        for rec in fail_records[:3]:
            print("    >", rec)

if __name__ == "__main__":
    main()
