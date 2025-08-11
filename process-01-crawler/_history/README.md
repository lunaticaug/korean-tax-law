# 크롤러 버전 히스토리

## 버전 설명

### v1.0.0 - requests 기반 (실패)
- 파일: `process-01-crawl-law_v1.0.0_requests.py`
- 단순 HTTP 요청으로 시도
- JavaScript 렌더링 페이지라 실패

### v1.1.0 - webdriver-manager 사용
- 파일: `process-01-crawl-law_v1.1.0_webdriver-manager.py`
- webdriver-manager로 ChromeDriver 자동 설치
- 서드파티 패키지 의존성

### v1.2.0 - Selenium 4 자동 관리
- 파일: `process-01-crawl-law_v1.2.0_selenium4-auto.py`
- Selenium 4.6+ 내장 Manager 사용
- iframe 처리 추가

### v1.3.0 - 인터랙티브 모드
- 파일: `process-01-crawl-law_v1.3.0_interactive.py`
- 브라우저 열어두고 사용자 확인 후 크롤링
- 디버깅 용이

### v1.4.0 - 수동 ChromeDriver
- 파일: `process-01-crawl-law_v1.4.0_manual-driver.py`
- 공식 ChromeDriver 직접 다운로드 방식
- 서드파티 의존성 제거

## 최종 버전

현재 사용 중인 버전은 v2.0.0으로 상위 디렉토리의 `process-01-crawl-law.py`입니다.