# 법제처 API 크롤러 아키텍처 문서

## 📌 함수 구조 개요 (VSCode Outline)

### process-01-law-api.py
```
📄 process-01-law-api.py
├── 📦 class LawAPIClient
│   ├── 🔧 __init__(self)
│   ├── 📂 load_config(self) -> Dict
│   ├── 🔍 search_law(self, query: str, display: int) -> Optional[Dict]
│   ├── 📝 parse_search_xml(self, xml_content: bytes) -> Dict
│   ├── 📖 get_law_detail(self, law_id: str, output_type: str) -> Optional[str]
│   ├── 🔒 sanitize_data(self, data: any) -> any
│   ├── 💾 save_results(self, data: any, filename: str, law_name: str)
│   └── ⬇️ download_law(self, law_name: str, formats: List[str])
└── 🚀 main()
```

### process-01-law-api-interactive.py
```
📄 process-01-law-api-interactive.py
├── 📦 class InteractiveLawSearch
│   ├── 🔧 __init__(self)
│   ├── 📂 load_config(self) -> Dict
│   ├── 🔍 search_law(self, query: str, display: int) -> Optional[Dict]
│   ├── 📝 parse_search_xml(self, xml_content: bytes) -> Dict
│   ├── 🖥️ display_search_results(self, results: Dict) -> Optional[Dict]
│   ├── 📅 format_date(self, date_str: str) -> str
│   ├── 📖 get_law_detail(self, law_id: str, output_type: str) -> Optional[str]
│   ├── 🔒 sanitize_data(self, data: any) -> any
│   ├── ⬇️ download_law(self, law_info: Dict)
│   └── ▶️ run(self)
└── 🚀 main()
```

### process-01-law-api-advanced.py
```
📄 process-01-law-api-advanced.py
├── 📦 class AdvancedLawAPIClient
│   ├── 🔧 __init__(self)
│   ├── 📂 load_config(self) -> Dict
│   ├── 🔍 search_law(self, query: str, display: int) -> Optional[Dict]
│   ├── 📝 parse_search_xml(self, xml_content: bytes) -> Dict
│   ├── 📖 get_law_detail(self, law_id, output_type, ...) -> Optional[str]
│   ├── 🏗️ parse_law_detail_xml(self, xml_content: str) -> Dict
│   ├── ▶️ interactive_search(self)
│   ├── 📋 search_menu(self)
│   ├── 🔢 direct_lookup_menu(self)
│   ├── 📍 article_lookup_menu(self)
│   ├── 📊 detail_menu(self, law_info: Dict)
│   ├── 🖥️ display_structured_result(self, parsed: Dict)
│   ├── 🔒 sanitize_data(self, data: Any) -> Any
│   └── 💾 save_result(self, data: Any, filename_base: str, output_type: str)
└── 🚀 main()
```

## 📖 함수별 세부 설명

### 🔧 초기화 함수
#### `__init__(self)`
- **공통 기능**: YAML 설정 로드, API 기본 URL 설정, 세션 폴더 생성
- **처리 과정**:
  1. `load_config()` 호출하여 email_id 획득
  2. email_id에서 @ 앞부분만 추출 (OC 파라미터)
  3. base_url 설정: "http://www.law.go.kr/DRF"
  4. session_folder 생성: YYYYMMDD_HHMMSS 형식

### 📂 설정 관리
#### `load_config(self) -> Dict`
- **공통 기능**: API_law.yaml 파일 읽기
- **반환값**: {'email_id': 'user_email'}
- **예외처리**: 파일 없을 시 기본값 반환 또는 생성

### 🔍 검색 함수
#### `search_law(self, query: str, display: int) -> Optional[Dict]`
- **API 엔드포인트**: `/lawSearch.do`
- **파라미터**:
  - OC: 인증키 (email_id)
  - target: 'law'
  - type: 'XML'
  - query: 검색어
  - display: 결과 개수 (기본 20~50)
- **반환값**: 파싱된 검색 결과 딕셔너리

### 📝 XML 파싱
#### `parse_search_xml(self, xml_content: bytes) -> Dict`
- **공통 기능**: 검색 결과 XML을 딕셔너리로 변환
- **추출 필드**:
  - 법령일련번호
  - 법령명한글
  - 시행일자
  - 소관부처명
  - 공포일자/번호
- **반환 구조**:
  ```python
  {
      'total_count': int,
      'laws': [
          {'법령명한글': str, '법령일련번호': str, ...}
      ]
  }
  ```

### 📖 상세 조회
#### `get_law_detail(self, law_id: str, output_type: str) -> Optional[str]`
- **API 엔드포인트**: `/lawService.do`
- **파라미터 차이**:
  - **기본/대화형**: MST(법령일련번호) 사용
  - **고급형**: MST, ID, JO(조항) 등 추가 파라미터 지원
- **출력 형식**: HTML, XML, JSON

### 🏗️ 구조화 파싱 (고급형 전용)
#### `parse_law_detail_xml(self, xml_content: str) -> Dict`
- **고급형 전용 기능**: XML을 계층 구조로 파싱
- **파싱 구조**:
  ```python
  {
      '기본정보': {...},
      '조문': {
          '편': [...],
          '장': [...],
          '조': [...]
      }
  }
  ```

### 🖥️ 사용자 인터페이스
#### `display_search_results(self, results: Dict)` (대화형)
- 검색 결과를 번호 목록으로 표시
- 사용자 선택 대기
- 선택된 법령 정보 반환

#### `search_menu(self)`, `detail_menu(self)` (고급형)
- 메뉴 기반 네비게이션
- 다양한 검색/저장 옵션 제공

### 🔒 데이터 정제
#### `sanitize_data(self, data: any) -> any`
- **공통 기능**: 민감정보 제거
- **제거 대상**:
  - OC 파라미터
  - email_id
  - 이메일 패턴 (***@***.***로 마스킹)
- **재귀적 처리**: dict, list, str 모두 처리

### 💾 저장 함수
#### `save_results(self)` / `save_result(self)`
- **저장 경로**: `_cache/YYYYMMDD_HHMMSS/`
- **파일명 규칙**:
  - 기본형: `{법령명}_전체조문_{timestamp}.{ext}`
  - 대화형: `{법령명}_전체조문_{timestamp}.{ext}`
  - 고급형: `{법령명}_{type}_{timestamp}.{ext}`
- **저장 전 처리**: sanitize_data() 호출

### ⬇️ 다운로드 오케스트레이션
#### `download_law(self)`
- **실행 순서**:
  1. search_law() 호출
  2. 첫 번째 결과 선택 (기본형) 또는 사용자 선택 대기
  3. get_law_detail() 호출 (각 형식별)
  4. save_results() 호출

## 📊 세 파일 비교표

### 기능 비교

| 구분 | process-01-law-api.py | process-01-law-api-interactive.py | process-01-law-api-advanced.py |
|------|----------------------|-----------------------------------|--------------------------------|
| **실행 방식** | 자동 실행 | 대화형 루프 | 메뉴 시스템 |
| **법령 선택** | 하드코딩 목록 | 검색 후 선택 | 검색/ID직접입력/조항검색 |
| **사용자 입력** | 없음 | 검색어, 선택 번호 | 메뉴 선택, 다양한 옵션 |
| **결과 표시** | 콘솔 출력만 | 목록 표시 + 선택 | 구조화된 계층 표시 |
| **저장 옵션** | HTML, XML 고정 | 사용자 선택 | HTML, XML, JSON, 구조화 |

### API 사용 비교

| API 기능 | 기본형 | 대화형 | 고급형 |
|----------|--------|--------|--------|
| 법령 검색 (`lawSearch.do`) | ✅ | ✅ | ✅ |
| 법령 본문 (`lawService.do`) | ✅ | ✅ | ✅ |
| 조항 단위 조회 | ❌ | ❌ | ✅ |
| 부가 파라미터 (JO, HO) | ❌ | ❌ | ✅ |

### 코드 복잡도

| 항목 | 기본형 | 대화형 | 고급형 |
|------|--------|--------|--------|
| 클래스 메서드 수 | 8개 | 10개 | 14개 |
| 코드 라인 수 | ~300줄 | ~325줄 | ~600줄 |
| 사용자 상호작용 | 없음 | 간단 | 복잡 |
| 에러 처리 | 기본 | 중간 | 상세 |

### 사용 시나리오

| 용도 | 추천 파일 | 이유 |
|------|-----------|------|
| **정기 백업** | process-01-law-api.py | 자동화 가능, cron 작업 적합 |
| **특정 법령 검색** | process-01-law-api-interactive.py | 검색어로 쉽게 찾기 가능 |
| **상세 분석** | process-01-law-api-advanced.py | 조항별 조회, 구조화 데이터 |
| **대량 수집** | process-01-law-api.py | 목록 수정으로 일괄 처리 |
| **탐색적 조회** | process-01-law-api-interactive.py | 여러 법령 탐색에 유용 |

### 출력 형식 차이

| 형식 | 기본형 | 대화형 | 고급형 |
|------|--------|--------|--------|
| HTML | ✅ 원본 그대로 | ✅ 원본 그대로 | ✅ 원본 그대로 |
| XML | ✅ 원본 그대로 | ✅ 원본 그대로 | ✅ 원본 그대로 |
| JSON | ❌ | ❌ | ✅ 구조화 변환 |
| 메타데이터 | ✅ 검색결과만 | ✅ 법령정보 | ✅ 상세 메타데이터 |

### 폴더 구조

| 항목 | 공통 구조 |
|------|-----------|
| **기본 경로** | `_cache/YYYYMMDD_HHMMSS/` |
| **파일명 패턴** | `{법령명}_{유형}_{타임스탬프}.{확장자}` |
| **민감정보 처리** | 모든 파일에서 OC 파라미터 제거 |

## 🎯 결론

1. **핵심 로직은 99% 동일**: API 호출, XML 파싱, 저장 방식
2. **차이는 UI 레이어**: 자동/대화형/메뉴 방식
3. **고급형만의 특징**: 구조화 파싱(`parse_law_detail_xml`)과 조항 단위 조회
4. **통합 가능성**: 공통 로직을 base class로 추출하면 코드 중복 제거 가능