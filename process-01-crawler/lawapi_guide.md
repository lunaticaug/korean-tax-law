좋습니다. 법제처 open API 가이드 페이지에 포함된 **모든 API 엔드포인트의 명세서를 하나로 정리**해드릴게요.

각 API의 요청 URL, 요청 파라미터, 설명, 샘플 URL, 출력 결과 필드 등을 빠짐없이 수집해 문서 형태로 제공하겠습니다. 작업이 완료되면 확인하실 수 있도록 알려드릴게요.


# 국가법령정보센터 OPEN API 엔드포인트 종합 가이드

본 문서는 국가법령정보 공동활용 사이트에서 제공하는 **OPEN API** 엔드포인트와 그 요청 파라미터, 응답 필드를 정리한 명세서입니다. 개발자가 코드를 작성하는 데 참고할 수 있도록 **엔드포인트별 요청 URL, 요청 변수, 샘플 URL, 응답 필드** 등을 상세히 나열합니다.

> **참고:** 각 API를 사용하기 위해서는 법제처 OPEN API 사용 신청 및 승인 후, **OC (OpenAPI Certification)** 값으로 신청 시 기재한 **이메일 ID**를 사용해야 합니다.

## 법령(현행/시행일/연혁) 관련 API

### 현행법령 목록 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=law`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 사용자 이메일의 ID (예: `g4c`@korea.kr 이메일이면 OC=`g4c`)
  * `target` (string, 필수): 서비스 대상 (`law`)
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`)
  * `search` (int): 검색범위 (기본값 `1`=법령명 검색, `2`=본문검색)
  * `query` (string): 검색어 (법령명에서 찾을 질의어, 정확한 검색을 위해 문자열 전체 일치 사용 예: `query="자동차"`)
  * `display` (int): 검색 결과 건수 (기본값 `20`, 최대 `100`)
  * `page` (int): 검색 결과 페이지 번호 (기본값 `1`)
  * `sort` (string): 정렬 옵션 (기본 `lasc`: 법령명 오름차순)

    * `ldes`: 법령명 내림차순
    * `dasc`: 공포일자 오름차순 / `ddes`: 공포일자 내림차순
    * `nasc`: 공포번호 오름차순 / `ndes`: 공포번호 내림차순
    * `efasc`: 시행일자 오름차순 / `efdes`: 시행일자 내림차순
  * 그 외 검색 필터:

    * `date` (int): 공포일자 (예: `20230101`)
    * `efYd` (string): 시행일자 범위 (예: `20090101~20090130`)
    * `ancYd` (string): 공포일자 범위 (예: `20090101~20090130`)
    * `ancNo` (string): 공포번호 범위 (예: `306~400`)
    * `rrClsCd` (string): 제개정 종류 코드 (예: `300201`=제정, `300202`=일부개정 등)
    * `nb` (int): 공포번호 검색 (정확히 일치하는 공포번호)
    * `org` (string): 소관부처 코드 (소관 부처별 검색)
    * `knd` (string): 법령종류 코드
    * `lsChapNo` (string): 법령 분류편 코드 (예: `01`=제1편, `02`=제2편, ...)
    * `gana` (string): 가나다 순 검색 키 (예: `ga`, `na`, `da` ...)
    * `popYn` (string): 상세화면 팝업여부 (`Y`일 경우 팝업화면용 응답)

* **샘플 요청:**

  1. 현행법령 **XML** 전체 검색:
     `.../lawSearch.do?OC=test&target=law&type=XML`
  2. 현행법령 **HTML** 전체 검색:
     `.../lawSearch.do?OC=test&target=law&type=HTML`
  3. 법령명에 `"자동차관리법"`을 포함한 검색 (XML):
     `.../lawSearch.do?OC=test&target=law&type=XML&query=자동차관리법`

* **응답 필드:** (XML/JSON의 각 필드)

  * `target` (string): 검색 서비스 대상
  * `키워드` (string): 검색어
  * `section` (string): 검색범위 (예: `"법령명"`)
  * `totalCnt` (int): 검색 결과 총 건수
  * `page` (int): 현재 페이지 번호
  * 이후는 각 검색 결과 항목의 필드 목록 (반복):

    * `lawId` (int): 검색 결과 일련번호 (※ `law id`로 표기되기도 함)
    * `법령일련번호` (int)
    * `현행연혁코드` (string)
    * `법령명한글` (string)
    * `법령약칭명` (string)
    * `법령ID` (int)
    * `공포일자` (int)
    * `공포번호` (int)
    * `제개정구분명` (string)
    * `소관부처명` (string)
    * `소관부처코드` (int)
    * `법령구분명` (string)
    * `공동부령구분` (string) (공동부령일 경우 구분 정보)
    * `공포번호(공동)` (string) (공동부령의 공포번호)
    * `시행일자` (int)
    * `자법타법여부` (string)
    * `법령상세링크` (string): 법령 상세정보 URL

### 현행법령 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=law`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 사용자 이메일 ID
  * `target` (string, 필수): 서비스 대상 (`law`)
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`)
  * **법령 지정 파라미터 (하나 이상 필수):**

    * `ID` (char): 법령 ID (법령마다 부여된 ID)
    * `MST` (char): 법령 마스터 번호 (내부 식별자, `lsi_seq`)
    * (*ID나 MST 중 하나는 반드시 입력하며, ID를 넣으면 해당 법령의 현행 본문을 조회함*)
  * **대체 입력 옵션:** (ID/MST 대신 아래 조합으로 특정 법령 지정 가능)

    * `LM` (string): 법령명 (법령명으로 직접 조회, 해당 법령의 링크)
    * `LD` (int): 법령 공포일자
    * `LN` (int): 법령 공포번호
    * ※ 예를 들어, 법령명+공포일자+공포번호를 함께 지정하여 특정 법령 버전을 찾을 수 있음.
  * `JO` (int): 조회할 조문의 번호 (생략시 전체 조문 표시)

    * 값 형식: 6자리 (조번호 4자리 + 조문가지번호 2자리). 예: `000200` = 제2조, `001002` = 제10조의2
  * `LANG` (char): 원문/한글 여부 (기본 한글)

    * `KO`: 한글 (기본값), `ORI`: 원문 (영문법령의 경우 원문)
    * (*현행 법령은 주로 한글이므로 거의 `KO`*)

* **샘플 요청:**

  1. 법령 **HTML** 본문 상세조회 (MST로 조회):
     `.../lawService.do?OC=test&target=law&MST=152338&type=HTML`
  2. 법령 **XML** 본문 상세조회 (MST로 조회):
     `.../lawService.do?OC=test&target=law&MST=152338&type=XML`
     *(예시 MST=152338는 특정 법령의 내부 식별자)*

* **응답 필드:** (법령 본문의 메타정보 및 조문 내용 등)

  * 법령 기본 정보:

    * `법령ID` (int): 법령 ID
    * `공포일자` (int) / `공포번호` (int)
    * `언어` (string): 법령 언어 (한글/영문 여부)
    * `법종구분` (string) 및 `법종구분코드` (string): 법령 종류 및 코드
    * `법령명_한글` (string) / `법령명_한자` (string) / `법령명약칭` (string)
    * `제명변경여부` (string): 법령 제명이 변경된 경우 `Y` (개정으로 제목 바뀜 여부)
    * `한글법령여부` (string): `Y`이면 한글법령 (주로 법령 원문이 한글임을 표시)
    * `편장절관` (int): 편/장/절/관 등 체계 단위 번호 (일련번호)
    * `소관부처코드` (int) 및 `소관부처` (string): 소관 부처 코드 및 명칭
    * `전화번호` (string): 담당 부서 전화번호
    * `시행일자` (int): 법령 시행일자
    * `제개정구분` (string): 제정/개정/폐지 구분명
    * `별표편집여부` (string): 별표 편집여부 (별표가 편집되었는지 여부)
    * `공포법령여부` (string): 공포법령 여부 (`Y`=공포된 법령 원문 여부)
    * `부서명` (string): 담당 부서명
    * `부서연락처` (string): 담당 부서 연락처
    * `공동부령구분` 및 `구분코드` (string): 공동부령인 경우의 구분명 및 코드
    * `공포번호(공동)` (string): 공동부령의 공포번호
  * 조문/항/호/목 정보: (요청시 JO 지정에 따라 특정 조문만 또는 전체)

    * `조문번호` (int) 및 `조문가지번호` (int): 조문 번호 및 가지 번호
    * `조문여부` (string): 해당 항목이 조문인지 여부
    * `조문제목` (string) 및 `조문내용` (string)
    * `조문시행일자` (int): 해당 조문의 시행일자
    * `조문제개정유형` (string): 조문의 개정 유형 (신설/개정 등)
    * `조문이동이전`/`조문이동이후` (int): 조문 이동 전/후 조문번호 (있다면)
    * `조문변경여부` (string): `Y`이면 해당 조문 내 변경 내용 있음
    * `항번호` (int) 및 `항내용` (string)
    * `항제개정유형` (string) 및 `항제개정일자문자열` (string): 항의 개정 유형 및 개정일자
    * `호번호` (int) 및 `호내용` (string)
    * `목번호` (string) 및 `목내용` (string) (목이 있는 경우)
    * `조문참고자료` (string): 조문에 딸린 참고자료
    * `부칙공포일자` (int) / `부칙공포번호` (int): 부칙의 공포일자 및 번호
    * `부칙내용` (string): 부칙 내용
    * `별표번호` (int) 및 `별표가지번호` (int): 별표 일련번호 및 가지 번호
    * `별표구분` (string): 별표 구분 (양식 등)
    * `별표제목` (string 및 문자열): 별표 제목
    * `별표시행일자` (int): 별표 시행일자
    * `별표서식파일링크` (string): 별표 서식 파일 (예: HWP) 링크
    * `별표HWP파일명` / `별표PDF파일링크` 등: 별표 원본 파일명 및 링크 (HWP/PDF 등)
    * `별표이미지파일명`: 별표 이미지 파일명 (있는 경우)
    * `별표내용` (string): 별표의 내용 (텍스트로 제공되는 경우)
    * `개정문내용` (string): 개정문 전문 내용
    * `제개정이유내용` (string): 제·개정 이유

### 시행일 법령 목록 조회 API

(특정 시행일을 기준으로 현행/연혁 법령 검색)

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=eflaw`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): 서비스 대상 (`eflaw`)
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`; 기본값 XML)
  * `search` (int): 검색범위 (`1`=법령명(기본), `2`=본문)
  * `query` (string): 검색어 (법령명에서 질의어)
  * `nw` (int): **법령 현황 필터**

    * `1`: 연혁법령만 (폐지된 과거 법령)
    * `2`: 시행예정법령만 (미래 효력 예정)
    * `3`: 현행법령만 (현재 효력)
    * *(복수 선택시 쉼표로 구분: 예 `nw=1,3` => 연혁+현행 포함)*
    * 기본값은 `전체` (모든 현행/연혁/예정 포함)
  * `LID` (string): 법령ID로 특정 법령 검색 (예: `LID=830`이면 ID 830인 법령 검색)
  * `display`, `page`, `sort`: 사용 방법은 현행법령 목록과 동일 (정렬옵션 동일)
  * 기타 필터: `efYd`(시행일자 범위), `date`(공포일자), `ancYd`, `ancNo`, `rrClsCd`, `nb`, `org`, `knd`, `gana`, `popYn` 등의 파라미터는 **현행법령 목록 조회 API**와 동일하게 사용 가능.

* **샘플 요청:**

  1. 현행/연혁 **XML** 법령 전체 검색:
     `.../lawSearch.do?OC=test&target=eflaw&type=XML`
  2. **HTML** 검색:
     `.../lawSearch.do?OC=test&target=eflaw&type=HTML`
  3. **질의어**로 검색 (예: `자동차관리법`):
     `.../lawSearch.do?OC=test&target=eflaw&query=자동차관리법`
  4. **공포일자 내림차순** 정렬:
     `.../lawSearch.do?OC=test&target=eflaw&type=XML&sort=ddes`
  5. **소관부처** 특정 (예: 국토교통부 코드 `1613000`):
     `.../lawSearch.do?OC=test&target=eflaw&type=XML&org=1613000`
  6. **법령ID로** 특정 법령 검색 (예: 법령ID 830):
     `.../lawSearch.do?OC=test&target=eflaw&type=XML&LID=830`

* **응답 필드:** (현행법령 목록과 거의 동일)

  * 기본적으로 **현행법령 목록 조회**의 필드와 동일하나, **현행연혁코드** 등이 혼재될 수 있습니다.
  * 주요 필드: `법령일련번호`, `현행연혁코드`, `법령명한글`, `법령약칭명`, `법령ID`, `공포일자`, `공포번호`, `제개정구분명`, `소관부처명/코드`, `법령구분명`, `공동부령구분`, `공포번호(공동)`, `시행일자`, `자법타법여부`, `법령상세링크` 등.
    *(현행/연혁/예정 여부에 따라 현행연혁코드 등이 표시됨)*

### 시행일 법령 본문 조회 API

(특정 시행일자의 법령 본문 조회 또는 연혁 법령 조회)

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=eflaw`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): 서비스 대상 (`eflaw`)
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`; 기본 XML)
  * **법령 지정 (ID 또는 MST 필수):**

    * `ID` (char): 법령 ID. *ID로 조회하면 해당 법령의 **현행 본문**을 반환*
    * `MST` (char): 법령 마스터 번호 (`lsi_seq`). *MST와 함께 `efYd`를 지정하면 특정 시행일자의 연혁 본문*
  * `efYd` (int, 필수 *MST 사용 시*): 법령의 시행일자 (YYYYMMDD). MST 사용 시 필수이며, 이 날짜 기준의 법령 본문을 조회

    * (*ID로 조회하는 경우 `efYd`는 무시되고 입력하지 않음*)
  * `JO` (int): 조문 번호 (6자리 형식, 생략 시 전체 조문)
  * `chrClsCd` (char): 원문/한글 여부 (기본 한글). `010202`=한글, `010201`=원문

* **샘플 요청:**

  1. **HTML 상세** (법령 ID로 현행법령 조회):
     `.../lawService.do?OC=test&target=eflaw&ID=1747&type=HTML` (자동차관리법 ID 1747)
  2. **XML 연혁** (법령 MST + 시행일자 지정):
     `.../lawService.do?OC=test&target=eflaw&MST=166520&efYd=20151007&type=XML`
  3. **특정 조문(XML)** 조회 (MST + 시행일자 + 조문):
     `.../lawService.do?OC=test&target=eflaw&MST=166520&efYd=20151007&JO=000300&type=XML` (제3조)

* **응답 필드:** 현행법령 본문 조회 API와 거의 동일하나, 연혁 법령의 특성이 반영됨. 추가적으로 다음과 같은 필드를 포함합니다.

  * `조문시행일자문자열` / `별표시행일자문자열`: 조문 및 별표의 시행일자 (연혁 정보 포함 문자열)
  * `별표편집여부`: 별표 편집 여부
  * `공포법령여부`: 공포법령 여부 (연혁일 경우 폐지 법령 등 표시)
  * **나머지 필드**: 법령ID, 공포일자, 공포번호, 법령명, 조문/항/호 내용 등은 **현행법령 본문 조회 API**와 유사하게 제공됩니다.

### 법령 연혁 목록 조회 API

(특정 법령의 연혁 이력 목록 조회)

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=lsHistory`&#x20;

* **요청 변수:**

  * `OC` (string, 필수) : 이메일 ID

  * `target` (string, 필수) : 서비스 대상 (`lsHistory`)

  * `type` (char, 필수) : 출력 형태 (HTML만 지원)

  * `query` (string) : 법령명 검색 질의 (특정 법령명을 입력)

  * `display`, `page` : 검색 결과 개수, 페이지 (기본 20개, 1페이지)

  * `sort` : 정렬옵션 (기본 `lasc`: 법령명 오름차순) (`ldes`, `dasc`, `ddes`, `nasc`, `ndes`, `efasc`, `efdes` 사용 가능)

  * 기타 필터: `efYd`, `date`, `ancYd`, `ancNo`, `rrClsCd`, `org`, `knd`, `lsChapNo`, `gana`, `popYn` 등 **현행법령 목록 조회**와 동일한 파라미터 사용 가능.

  > **Note:** 법령 연혁 목록 조회는 **특정 법령의 모든 연혁**을 보여주며, 일반적으로 `query`에 법령명을 넣어 사용합니다. (예: *자동차관리법*의 제정부터 최신까지 모든 버전 목록)

* **샘플 요청:**

  1. *자동차관리법* 연혁 HTML 조회:
     `.../lawSearch.do?OC=test&target=lsHistory&type=HTML&query=자동차관리법`
  2. *행정안전부*(소관부처 코드 1741000) 소관 법령 연혁 HTML 조회:
     `.../lawSearch.do?OC=test&target=lsHistory&type=HTML&org=1741000`

* **응답 필드:** (HTML 형태로 연혁 목록 제공)

  * `totalCnt`, `page` 등 검색 메타정보와 함께, 각 결과별로 **법령 연혁 목록 항목**이 제공됩니다. 주요 필드:

    * `법령 일련번호` (int) – 해당 법령 버전의 일련번호
    * `법령명` (string) – 법령 이름
    * `법령ID` (int) – 법령 ID
    * `공포일자` (int) / `공포번호` (int) – 버전별 공포일 및 번호
    * `제개정구분명` (string) – 제정/개정/폐지 구분명
    * `소관부처코드`/`소관부처명` – 해당 버전 소관 부처
    * `법령구분명` – 법령 구분 (법률/령/규칙 등)
    * `시행일자` (int) – 해당 버전의 시행일자
    * `본문 상세링크` – 그 연혁 법령 본문 조회 링크

### 법령 연혁 본문 조회 API

(특정 법령의 연혁 상세 내용 조회)

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=lsHistory`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): 서비스 대상 (`lsHistory`)
  * `type` (char, 필수): 출력 형태 (`HTML`만 지원)
  * **법령 지정 (ID 또는 MST 필수):**

    * `ID` (char): 법령 ID (또는)
    * `MST` (char): 법령 마스터 번호 (`lsi_seq`)
  * `LM`, `LD`, `LN`: 법령명, 공포일자, 공포번호로 특정 연혁 버전을 지정 가능 (조합 사용)
  * `chrClsCd` (char): 원문/한글 여부 (`010202`: 한글(기본), `010201`: 원문)

* **샘플 요청:**

  1. 법령 연혁 **HTML** 상세조회 (MST로 특정 버전):
     `.../lawService.do?OC=test&target=lsHistory&MST=9094&type=HTML`
     (MST=9094, 예시)
  2. 다른 연혁 예시 (MST=166500):
     `.../lawService.do?OC=test&target=lsHistory&MST=166500&type=HTML`

* **응답:** 연혁 법령의 **HTML 본문** 페이지가 반환됩니다 (데이터 필드보다는 사람이 읽는 형태). 해당 연혁 버전의 조문, 부칙 등 전체 내용을 HTML로 제공하며, 기계가 파싱하기보다는 브라우저 표시용입니다.
  *(※ 응답 필드 테이블이 별도로 제공되지 않으며, **본문 전체 HTML**로 출력됨)*

### 현행법령 **조항/항/호/목 단위** 조회 API

* **현행법령 본문 조항호목 조회 API** (특정 법령의 특정 조항-항-호-목만 조회)

  * **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=lawjosub`&#x20;
  * **요청 변수:**

    * `OC` (string, 필수): 이메일 ID
    * `target` (string, 필수): `lawjosub` (현행 법령 조문 단위)
    * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`)
    * `ID` (char): 법령 ID (또는)
    * `MST` (char): 법령 마스터 번호 (`lsi_seq`)
    * *ID나 MST 중 하나는 필수이며, ID로 조회 시 해당 법령의 현행 전체 본문이 조회됩니다*
    * `JO` (char, 필수): 조 번호 (6자리, 조 + 가지번호)
    * `HANG` (char): 항 번호 (6자리)
    * `HO` (char): 호 번호 (6자리)
    * `MOK` (char): 목 번호 (한 글자, 가\~하) – 한글 목은 UTF-8 인코딩 필요

      * 예: "다" 목은 URL 인코딩하여 `MOK=%EB%8B%A4` 또는 `URLDecoder.decode("다","UTF-8")`로 전달
  * **샘플 요청:**

    1. **XML 상세** – *건축법* 제3조제1항제2호다목:
       `.../lawService.do?OC=test&target=lawjosub&type=XML&ID=001823&JO=000300&HANG=000100&HO=000200&MOK=다`
    2. **HTML 상세** – 동일 조항:
       `.../lawService.do?OC=test&target=lawjosub&type=HTML&ID=001823&JO=000300&HANG=000100&HO=000200&MOK=다`
  * **응답 필드:** (지정한 조항/항/호/목의 내용과 상위 메타정보)

    * `법령키` (int), `법령ID` (int), `공포일자` (int), `공포번호` (int) 등 법령 기본정보
    * `언어` (string), `법령명_한글`, `법령명_한자` 등
    * `법종구분코드`, `법종구분명` (법령종류)
    * `제명변경여부` (`Y`=제명 변경됨)
    * `한글법령여부` (`Y`=한글법령)
    * `편장절관`, `소관부처코드`, `소관부처` 등
    * `전화번호`, `시행일자`, `제개정구분` 등
    * `조문별시행일자` (string), `조문시행일자문자열` (string)
    * `별표시행일자문자열`, `별표편집여부`, `공포법령여부`, `시행일기준편집여부` 등
    * **지정한 조문 내용:** `조문번호`, `조문여부`, `조문제목`, `조문시행일자`, `조문이동이전/이후`, `조문변경여부`, `조문내용`
    * 해당 `항번호`와 `항내용`, `호번호`와 `호내용`, `목번호`와 `목내용` 등 구조에 따른 내용

* **시행일 법령 본문 조항호목 조회 API** (연혁 법령의 특정 조문만 조회)

  * 요청 URL 및 파라미터는 `target=eflawjosub` (추정, 문서에 명시)로 사용됩니다.
  * 사용법은 `lawjosub`와 유사하되, `efYd` (시행일자) 지정이 추가로 필요합니다 (연혁 버전 식별).
  * (예: `.../lawService.do?OC=test&target=eflawjosub&MST=...&efYd=YYYYMMDD&JO=...&HANG=...` 등의 형태)
  * ※ 해당 가이드 페이지는 유사한 패턴으로 존재하며, **현행법령 조문 조회**와 동일한 방식으로 작동합니다.

### 위임 법령 조회 API

(상위 법령의 개별 조문에 의해 **위임된 하위법령** 정보를 조회)

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=lsDelegated`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): `lsDelegated`
  * `type` (char, 필수): 출력 형태 (`XML`/`JSON` 지원) *(HTML 미지원)*
  * `ID` (char): 법령 ID (또는)
  * `MST` (char): 법령 마스터 번호 (`lsi_seq`)
  * (*ID 또는 MST 중 하나 필수. ID 입력 시 해당 법령의 현행 본문을 기준으로 조회*)

* **샘플 요청:**

  1. *초·중등교육법*의 위임 법령 조회 (XML):
     `.../lawService.do?OC=test&target=lsDelegated&type=XML&ID=000900`
     (법령 ID 000900인 **초·중등교육법** 조문들의 위임내용 조회)

* **응답 필드:** (해당 법령의 각 조문에서 **위임된 하위법령/규칙/자치법규** 목록)

  * `법령일련번호`, `법령명`, `법령ID`, `공포일자`, `공포번호`, `소관부처코드`, `전화번호`, `시행일자` 등 상위법령 정보
  * `조문번호`, `조문제목`: 위임 근거 조문 번호 및 제목
  * **위임된 법령**:

    * `위임구분` (string): 위임된 법령 종류 (법률, 대통령령 등)
    * `위임법령일련번호`, `위임법령제목`: 위임된 하위법령의 일련번호 및 제목
    * `위임법령조문번호`, `위임법령조문가지번호`, `위임법령조문제목`: 위임된 법령의 해당 조문 번호/제목
    * `링크텍스트`, `라인텍스트`, `조항호목`: 상위 법령 조문 내 위임 근거 문장 (링크 걸릴 텍스트)
  * **위임된 행정규칙** (있다면):

    * `위임행정규칙일련번호`, `위임행정규칙제목` 및 링크텍스트/라인텍스트/조항호목 (위와 유사)
  * **위임된 자치법규** (있다면):

    * `위임자치법규일련번호`, `위임자치법규제목` 및 링크텍스트/라인텍스트/조항호목

## 영문법령 관련 API

국가법령정보에서는 주요 법령의 **영문 번역본**을 제공하며, 별도의 target 값 `elaw`를 사용합니다.

### 영문법령 목록 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=elaw`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): 서비스 대상 (`elaw`)
  * `search` (int): 검색범위 (`1`=법령명(기본), `2`=본문검색)
  * `query` (string): 검색어 (기본값 `*`로 전체 조회)
  * `display` (int): 결과 개수 (기본 20, 최대 100)
  * `page` (int): 페이지 번호 (기본 1)
  * `sort` (string): 정렬옵션 (기본 `lasc`: 법령명 오름차순)

    * `ldes`, `dasc`, `ddes`, `nasc`, `ndes`, `efasc`, `efdes` (동일 의미)
  * 기타 필터: `date`, `efYd`, `ancYd`, `ancNo`, `rrClsCd`, `nb`, `org`, `knd`, `gana`, `type`, `popYn` 등이 사용 가능.

    * `type`: 출력 형태 (`HTML`/`XML`/`JSON`) - **영문법령 목록은 기본적으로 XML/JSON 형식으로 활용**

* **샘플 요청:**

  1. 영문법령 **XML** 전체 목록:
     `.../lawSearch.do?OC=test&target=elaw&type=XML`
  2. 영문법령 **HTML** 전체 목록:
     `.../lawSearch.do?OC=test&target=elaw&type=HTML`
  3. 영문법령 검색 – 한글 질의 (*가정폭력방지*):
     `.../lawSearch.do?OC=test&target=elaw&type=XML&query=가정폭력방지`
  4. 영문법령 검색 – 영문 질의 (*insurance*):
     `.../lawSearch.do?OC=test&target=elaw&type=XML&query=insurance`

* **응답 필드:**

  * `target` (string): 검색 대상 (`elaw`)
  * `키워드` (string): 검색어
  * `section` (string): 검색범위 (Law Name 또는 Contents)
  * `totalCnt` (int): 총 건수
  * `page` (int): 페이지 번호
  * 각 결과 항목:

    * `law id` (int): 결과 번호
    * `법령일련번호` (int)
    * `현행연혁코드` (string)
    * `법령명한글` (string)
    * `법령명영문` (string): 법령명 (영문)
    * `법령ID` (int)
    * `공포일자` (int)
    * `공포번호` (int)
    * `제개정구분명` (string)
    * `소관부처명` (string)
    * `법령구분명` (string)
    * `시행일자` (int)
    * `자법타법여부` (string)
    * `법령상세링크` (string): 영문법령 상세 링크

### 영문법령 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=elaw`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): `elaw`
  * **법령 지정:** `ID` 또는 `MST` (필수, 하나 선택)

    * `ID` (char): 법령 ID (영문법령의 ID)
    * `MST` (char): 법령 마스터 번호 (`lsi_seq`)
  * `LM`, `LD`, `LN`: (옵션) 법령명, 공포일자, 공포번호로 특정 버전 지정 (ID/MST 대신 사용 가능)
  * `type` (char): 출력 형태 (`HTML`/`XML`/`JSON`)

* **샘플 요청:**

  1. **표준시법** (표준시에 관한 법률) 영문 본문 HTML 조회 (ID 이용):
     `.../lawService.do?OC=test&target=elaw&ID=000744&type=HTML`
  2. **상호저축은행법 시행령** 영문 본문 HTML 조회 (MST 이용):
     `.../lawService.do?OC=test&target=elaw&MST=127280&type=HTML`

* **응답:** 영문법령의 본문 내용이 **한글법령 본문 조회 API**와 유사한 구조로 반환됩니다. (단, 조문 내용은 영문이며, 한글명과 영문명이 함께 표시될 수 있습니다.) 주요 필드는 한글 본문과 거의 동일하나, `법령명영문`, `조문내용영문` 등의 필드를 포함할 수 있습니다.

  *(예: 영문법령 본문 XML에는 한글명과 영문명이 모두 제공되며, 조문별 영문 내용이 `<ParagraphContentEng>` 등의 태그로 표현됨)*

## 부가서비스 관련 API

**부가서비스**란, 법령 본문 이외에 법령체계도, 신구법 비교, 3단 비교, 법령 약칭, 삭제데이터, 한눈보기 등 추가 정보를 제공하는 API입니다. 이들 API는 **일반 법령 서비스 신청자에게 기본 제공**되며, 특별한 추가 신청 없이 이용 가능합니다.

### 법령 체계도 목록 조회 API

(법령의 **조문 체계도**를 검색)

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=lsStmd`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): `lsStmd` (law Structure Map Data)
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`)
  * `query` (string): 법령명 질의 (특정 법령명 또는 키워드)
  * `display`, `page`: 결과 개수, 페이지
  * `sort`: 정렬옵션 (기본 `lasc` 법령명 오름차순; `ldes`, `dasc`, `ddes`, `nasc`, `ndes`, `efasc`, `efdes` 지원)
  * 기타 필터: `efYd`, `ancYd`, `date`, `nb`, `ancNo`, `rrClsCd`, `org`, `knd`, `gana`, `popYn` 등 **현행법령 목록 조회와 동일**.

* **샘플 요청:**

  1. *자동차관리법* **법령체계도 HTML** 조회:
     `.../lawSearch.do?OC=test&target=lsStmd&type=HTML&query=자동차관리법`
  2. '**ㄱ**'으로 시작하는 법령 체계도 HTML 조회:
     `.../lawSearch.do?OC=test&target=lsStmd&type=HTML&gana=ga`
  3. 법령체계도 **XML** 전체 조회:
     `.../lawSearch.do?OC=test&target=lsStmd&type=XML`
  4. 법령체계도 **JSON** 전체 조회:
     `.../lawSearch.do?OC=test&target=lsStmd&type=JSON`

* **응답 필드:**

  * `target`, `키워드`, `section`, `totalCnt`, `page`, `numOfRows` 등 검색 메타데이터
  * `resultCode`, `resultMsg`: 조회 성공여부 (`00`/`01`, success/fail)
  * 각 결과 항목:

    * `law id` (int): 결과 순번
    * `법령 일련번호` (int)
    * `법령명` (string)
    * `법령ID` (int)
    * `공포일자` (int)
    * `공포번호` (int)
    * `제개정구분명` (string)
    * `소관부처코드` (int) / `소관부처명` (string)
    * `법령구분명` (string)
    * `시행일자` (int)
    * `본문 상세링크` (string): **법령 체계도** 본문 조회 링크

  위 결과의 **상세링크**를 통해 해당 법령의 체계도 구조 (편/장/절/관/조 항목 트리)이 제공됩니다. **법령 체계도 본문 조회 API**를 통해 취득할 수 있습니다.

### 법령 체계도 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=lsStmd`
* **요청 변수:**

  * `OC` (string, 필수), `target=lsStmd`, `type` (HTML/XML/JSON) 등은 **본문 목록 조회와 동일**.
  * **법령 지정:** `ID` 또는 `MST` 필수 (특정 법령 식별)
* **내용:** 지정한 법령의 **조문 체계 구조**를 반환합니다. 편/장/절 등 계층 구조와 각 조문의 제목이 포함됩니다.
* **응답:** 법령의 목차와 구조를 계층화하여 제공 (예: XML로 편명, 장명, 조문제목 등을 트리 형태로 출력).

*(※ 자세한 필드 명세는 법령 체계도 목록 조회 결과의 상세링크 응답으로 확인 가능)*.

### 신구법 목록 조회 API

(법령의 신구조문 대비표 목록 조회)

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=lsRvs` (추정)
* **요청 변수:** 현행법령 목록 조회와 유사하게, `query`로 법령명을 지정하면 해당 법령의 **신구법 비교표** 목록을 조회 가능. (법령 개정 시 구법-신법 조문 대응표)
* 일반적으로, 신구법 목록 조회 결과에서 각 개정차수별 **비교표 상세 링크**를 얻을 수 있으며, 이를 통해 **신구법 본문 조회 API**로 접근.

### 신구법 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=lsRvs` (추정)
* **요청 변수:** `ID` 또는 `MST` (특정 개정차수 식별자) 등을 사용.
* **내용:** 해당 법령의 특정 개정에 대한 **조문 신구 대비표**를 반환. (주로 HTML 형태)
* **응답:** 개정 전 조문 vs 개정 후 조문이 나란히 비교된 표 형태의 데이터.

*(신구법 관련 API는 데이터 포털에 *법제처 신구법 목록/본문 조회*로도 소개되어 있으며, 요청/응답 구조는 법령ID와 개정차수 정보를 활용함)*.

### 3단 비교 목록 조회 API / 3단 비교 본문 조회 API

* **3단 비교**는 구법-현행-개정안을 3단으로 비교하는 표입니다.
* 사용 방식은 **신구법 API와 유사**하며, `target=ls3d` (추정)로 목록 조회 및 본문 조회가 제공됩니다.
* **목록 API**: 특정 법령의 3단비교 가능한 개정안 목록 조회.
* **본문 API**: 특정 3단비교표 상세 조회 (ID 또는 MST 지정).
* **응답:** 3단 비교표 (이전법/현행법/개정안) HTML 또는 XML.

### 법률명 약칭 조회 API

* 법률의 **약칭**(별칭)을 조회하는 API.
* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=lawabbr` (target 추정)
* **요청 변수:** `query`에 법률 정식 명칭 입력 시, 약칭 반환.
* **응답:** 입력한 정식명칭에 대응하는 약칭 (예: \*\*「청소년 보호법」\*\*의 약칭 **"청보법"** 등) 목록을 제공.
* 이 API는 **목록 조회형**이며, 별도의 본문 조회는 제공되지 않습니다 (테이블상 본문 조회란에 `-` 표기).

### 삭제 법령 목록 조회 API

* **삭제된 법령 데이터** 목록을 조회.
* target 추정: `lsAbrogated` 또는 유사.
* **응답:** 폐지되거나 삭제된 법령들의 목록 (법령명, ID, 삭제일 등). 본문 조회는 제공 안 함.

### 한눈보기 목록/본문 조회 API

* **한눈보기**는 법령의 중요한 조문을 발췌하여 개요를 보여주는 서비스입니다.
* **목록 조회 API:** 특정 법령의 한눈보기 제공 목록 (대상 법령명 검색)
* **본문 조회 API:** 해당 법령의 한눈보기 내용을 반환 (주요 내용 요약본).
* target 추정: `lsGlance` 등.
* **응답:** 법령의 목적, 주요 조항 요약 등이 HTML로 제공.

以上은 주요 **법령 및 부가서비스 관련 API**를 정리한 것입니다.

## 판례 / 결정례 / 해석례 / 심판례 관련 API

국가법령정보센터는 **법원 판례**, **헌법재판소 결정례**, **법령해석례**, **행정심판례** 등의 데이터를 OPEN API로 제공합니다. 이들은 **목록 조회 API**와 **본문 조회 API**로 나뉘며, 각 서비스 대상에 맞는 `target` 값을 사용합니다.

### 판례 목록 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=prec`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): `prec` (판례)
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`)
  * `search` (int): 검색범위 (`1`=사건명(기본), `2`=본문)
  * `query` (string): 검색어 (해당 검색범위에서 찾을 질의어)

    * *(예: 사건명에 "자동차" 포함 검색은 query="자동차")*
  * `display` (int): 결과 건수 (기본 20, 최대 100)
  * `page` (int): 페이지 번호 (기본 1)
  * **판례 전용 필터:**

    * `org` (string): **법원종류** 필터 (`400201`=대법원, `400202`=하급심 법원)
    * `curt` (string): **법원명** (예: `대법원`, `서울고등법원`, `인천지방법원` 등)
    * `JO` (string): **참조법령명** (판례에 언급된 법령명, 예: `형법`, `민법`)
    * `gana` (string): 사전식 검색 (ㄱ,ㄴ,ㄷ 등 입력)
    * `sort` (string): 정렬옵션 (기본 사건명 오름차순 `lasc`)

      * `ldes`: 사건명 내림차순
      * `dasc`: 선고일자 오름차순 / `ddes`: 선고일자 내림차순 (기본)
      * `nasc`: 법원명 오름차순 / `ndes`: 법원명 내림차순
    * `date` (int): 판례 **선고일자** (YYYYMMDD) 검색
    * `prncYd` (string): 선고일자 범위 (예: `20090101~20090130`)
    * `nb` (string): **판례 사건번호** (예: `2009도1234`)
    * `datSrcNm` (string): **데이터출처명** (예: `대법원`, `국세법령정보시스템`, `근로복지공단산재판례` 등)
    * `popYn` (string): 상세화면 팝업 여부 (`Y`=팝업 화면 용)

* **샘플 요청:**

  1. 사건명에 '**담보권**' 포함 **XML** 검색:
     `.../lawSearch.do?OC=test&target=prec&type=XML&query=담보권`
  2. 사건명 '**담보권**' + **법원=대법원** **HTML** 검색:
     `.../lawSearch.do?OC=test&target=prec&type=HTML&query=담보권&curt=대법원`
  3. **사건번호** `'2009느합133,2010느합21'` **HTML** 검색:
     `.../lawSearch.do?OC=test&target=prec&type=HTML&nb=2009느합133,2010느합21`
  4. **데이터출처**가 '*근로복지공단산재판례*' 인 판례 **JSON** 검색:
     `.../lawSearch.do?OC=test&target=prec&type=JSON&datSrcNm=근로복지공단산재판례`

* **응답 필드:**

  * `target` (string): 검색 대상 (prec)
  * `공포번호` (string): (*판례의 공포번호는 의미 없음, 빈 값*)
  * `키워드` (string): 검색어
  * `section` (string): 검색범위 (`EvtNm`: 판례명 / `bdyText`: 본문)
  * `totalCnt` (int): 결과 건수
  * `page` (int): 출력 페이지
  * 각 판례 결과 항목:

    * `prec id` (int): 결과 순번
    * `판례일련번호` (int): 판례 일련번호
    * `사건명` (string)
    * `사건번호` (string)
    * `선고일자` (string)
    * `법원명` (string)
    * `법원종류코드` (int): 400201 또는 400202 등
    * `사건종류명` (string)
    * `사건종류코드` (int)
    * `판결유형` (string)
    * `선고` (string) (ex: "파기환송")
    * `데이터출처명` (string)
    * `판례상세링크` (string)

### 판례 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=prec`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): `prec`
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`/`JSON`)

    * *국세청 판례의 경우 HTML만 지원* (특이사항)
  * `ID` (char, 필수): **판례 일련번호**
  * `LM` (string): 판례명 (옵션)

* **샘플 요청:**

  1. 판례일련번호 **228541**의 판례 **HTML** 조회:
     `.../lawService.do?OC=test&target=prec&ID=228541&type=HTML`

* **응답 필드:**

  * `판례정보일련번호` (int)
  * `사건명` (string)
  * `사건번호` (string)
  * `선고일자` (int)
  * `선고` (string)
  * `법원명` (string)
  * `법원종류코드` (int)
  * `사건종류명` (string)
  * `사건종류코드` (int)
  * `판결유형` (string)
  * `판시사항` (string)
  * `판결요지` (string)
  * `참조조문` (string)
  * `참조판례` (string)
  * `판례내용` (string)
    *(판례의 본문, 판시사항, 결정요지 등 주요 내용 필드가 모두 제공됨)*

### 헌재결정례 목록 조회 API

* **요청 URL:** `.../lawSearch.do?target=cons` (추정, Constitution)
* **요청 변수:** 판례와 유사하게 `search`, `query` 등 사용.
* **특이사항:** `target=cons`나 `target=const`로 추정되며, 응답 필드 등은 판례와 비슷한 구조로 **헌법재판소 결정** 정보를 제공.

### 헌재결정례 본문 조회 API

* **요청 URL:** `.../lawService.do?target=cons` (추정)
* **요청 변수:** `ID`(결정례 일련번호) 등.
* **응답:** 결정문 전문 (합헌/위헌 결정의 주문, 이유 등).

*(헌재 API도 data.go.kr에 **헌재결정례 목록/본문 조회**로 제공됨)*.

### 법령해석례 목록 조회 API

* **요청 URL:** `.../lawSearch.do?target=expc` (예상, "explanation case")
* **요청 변수:** 판례와 유사 (`query`로 안건명 등 검색).
* **특이사항:** 법령해석 사례는 각 부처의 법령해석 회신 사례. `target=expc` 사용.
* **응답:** 안건명, 법령명, 요청기관 등 포함.

### 법령해석례 본문 조회 API

* **요청 URL:** `.../lawService.do?target=expc`
* **요청 변수:** `ID`(해석례 일련번호).
* **응답:** 해당 해석 사례의 질문, 회답 요지, 회답 전문 등.

### 행정심판례 목록 조회 API

* **요청 URL:** `.../lawSearch.do?target=admr` (Administrative remedy)
* **요청 변수:** 사건명/번호 등 검색 가능.
* **응답:** 행정심판 재결례 목록.

### 행정심판례 본문 조회 API

* **요청 URL:** `.../lawService.do?target=admr`
* **요청 변수:** `ID`(심판례 일련번호).
* **응답:** 재결 주문, 이유 등 전문.

*(행정심판 API 상세 명세는 국가법령정보센터 가이드에 포함되어 있으며, `target=admr`로 추정됩니다.)*

## 위원회 결정문 관련 API

다양한 행정위원회의 **결정문**(의결서 등) 역시 API로 제공됩니다. 각 위원회별로 **목록 조회 API**와 **본문 조회 API**가 있으며, `target` 값으로 구분합니다.

**위원회별 target 코드:**

* **공정거래위원회** 결정문: `target=ftc`
* **국민권익위원회** (ACRC) 결정문: `target=acr`
* **개인정보보호위원회** 결정문: `target=ppc`
* **금융위원회** 결정문: `target=fsc` (추정)
* **고용보험심사위원회**: (target 미확정, 예: `eic` 등 추정)
* **노동위원회**: (target 예: `nlc` 추정)
* **방송통신위원회**: (target 예: `kcc` 추정)
* **산업재해보상보험재심사위원회**: (target 예: `iac` 추정)
* **중앙토지수용위원회**: (target 예: `land` 추정)
* **중앙환경분쟁조정위원회**: (target 예: `envc` 추정)
* **증권선물위원회**: (target 예: `sfc` 추정)
* **국가인권위원회**: `target=nhrck`

각 기관의 목록/본문 조회 형식이 유사하므로, 대표적인 위원회인 공정거래위, 권익위, 개인정보위, 인권위의 사례로 설명합니다.

### 공정거래위원회 결정문 목록 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=ftc`&#x20;

* **요청 변수:**

  * `OC` (string, 필수): 이메일 ID
  * `target` (string, 필수): `ftc` (공정거래위원회)
  * `type` (char, 필수): 출력 형태 (`HTML`/`XML`) *(JSON 제공여부는 문서상 언급 없음)*
  * `search` (int): 검색범위 (`1`=사건명(기본), `2`=본문검색)
  * `query` (string): 검색어 (사건명 또는 본문) *(IE 사용 시 UTF-8 인코딩 필요)*
  * `display`, `page`: 결과 건수 (기본 20) 및 페이지
  * `gana` (string): 사전식 검색 (ga, na, da, ...)
  * `sort` (string): 정렬옵션 (기본 사건명 오름차순 `lasc`)

    * `ldes`: 사건명 내림차순
    * `dasc`: 의결일자 오름차순 / `ddes`: 의결일자 내림차순
    * `nasc`: 사건번호 오름차순 / `ndes`: 사건번호 내림차순
  * `popYn` (string): 팝업 출력 여부 (`Y`=팝업용)

* **샘플 요청:**

  1. 공정거래위 결정문 **HTML 목록** 조회:
     `.../lawSearch.do?OC=test&target=ftc&type=HTML`
  2. 공정거래위 결정문 **XML 목록** 조회:
     `.../lawSearch.do?OC=test&target=ftc&type=XML`

* **응답 필드:**

  * `target` (string): 검색 대상
  * `키워드` (string): 검색 단어
  * `section` (string): 검색범위
  * `totalCnt` (int): 검색 건수
  * `page` (int): 페이지 번호
  * `기관명` (string): 위원회명 (공정거래위원회)
  * `ftc id` (int): 결과 순번
  * `결정문 일련번호` (int)
  * `사건명` (string)
  * `사건번호` (string)
  * `회의종류` (string)
  * `결정번호` (string)
  * `결정일자` (string)
  * `결정문 상세링크` (string)

### 공정거래위원회 결정문 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=ftc`
* **요청 변수:** (`법제처 가이드 페이지 참조`)

  * `OC` (string, 필수), `target=ftc`, `type` (HTML/XML/JSON)
  * `ID` (char, 필수): **결정문 일련번호**
  * 기타: 위원회 결정문 종류에 따라 `문서유형`(의결서/시정권고서 등)이나 `사건번호` 등 추가 필터가 있을 수 있음.
* **응답:** 결정문 본문(의결서 전문) 또는 시정권고서 등이 포함. 필드 예시: 사건명, 사건번호, 의결일자, 주문, 이유, 위원명단, 결정요지, 판단요지, 신청인/피신청인 등.

*(공정거래위 본문 API 세부 명세는 인터넷 자료에서 발췌 가능하며, 권익위/인권위 사례와 유사 구조일 것)*.

### 국민권익위원회 결정문 목록 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=acr`&#x20;

* **요청 변수:**

  * `OC`, `target=acr`, `type` (HTML/XML)
  * `search` (int): 검색범위 (`1`=민원표시(기본), `2`=본문검색)
  * `query` (string): 검색어 (민원표시명 등)
  * `display`, `page`, `gana`, `sort` 등: 공정거래위와 유사

    * `sort`: 기본 `lasc` (민원표시 오름차순) / `ldes` (내림차순) / `dasc` (의결일 오름) / `ddes` (의결일 내림) / `nasc` (의안번호 오름) / `ndes` (의안번호 내림)
  * 기타: `popYn` 지원

* **샘플 요청:**

  1. 권익위 결정문 **HTML 목록** 조회:
     `.../lawSearch.do?OC=test&target=acr&type=HTML`
  2. 권익위 결정문 **XML 목록** 조회:
     `.../lawSearch.do?OC=test&target=acr&type=XML`

* **응답 필드:**

  * `target`, `키워드`, `section`, `totalCnt`, `page` 등
  * `기관명` (string): 기관명 (국민권익위원회)
  * `acr id` (int): 결과 순번
  * `결정문 일련번호` (int)
  * `민원표시` (string)
  * `의안번호` (string)
  * `회의종류` (string)
  * `결정구분` (string)
  * `의결일` (string)
  * `결정문 상세링크` (string)

### 국민권익위원회 결정문 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=acr` (ACRC)

* **요청 변수:**

  * `OC`, `target=acr`, `type` (HTML/XML/JSON)
  * `ID` (char, 필수): 결정문 일련번호
  * `LM` (char): 결정문명 (옵션)
  * `fields` (string): 응답항목 옵션 (콤마로 필요한 항목만 요청 가능, HTML 출력에는 적용 안 됨)

    * 예: `fields=사건명,사건번호,의결일자` 등. 빈 값 또는 미지정 시 전체 항목 출력

* **샘플 요청:**

  1. 권익위 결정문 일련번호 **331** HTML 조회:
     `.../lawService.do?OC=test&target=acr&ID=331&type=HTML`
  2. 권익위 결정문 일련번호 **335** XML 조회:
     `.../lawService.do?OC=test&target=acr&ID=335&type=XML`

* **응답 필드:** (권익위 결정문 - 의결서 기준)

  * `결정문일련번호` (int)
  * `기관명` (string) / `위원회명` (string)
  * `사건명` (string)
  * `사건번호` (string)
  * `의결일자` (string)
  * `주문` (string)
  * `이유` (string)
  * `위원정보` (string): 참여 위원 명단 및 직책
  * `별지` (string): 별지 첨부 여부/내용
  * `결정요지` (string)
  * `판단요지` (string)
  * `주문요지` (string)
  * `분류명` (string)
  * `결정유형` (string)
  * `신청인` (string) / `피신청인` (string)
  * `피해자` (string) / `피조사자` (string) (해당하는 경우)
  * `원본다운로드URL` (string)
  * `바로보기URL` (string)
  * `결정례전문` (string): 결정문 전문 (텍스트)
  * `데이터기준일시` (string): 데이터 기준 시각

### 개인정보보호위원회 결정문 목록 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawSearch.do?target=ppc`&#x20;

* **요청 변수:** (개인정보위는 **안건명** 기준)

  * `OC`, `target=ppc`, `type` (HTML/XML)
  * `search` (`1`=안건명, `2`=본문검색)
  * `query` (string): 검색어 (안건명 등)
  * `display`, `page`, `gana`, `sort` (기본 `lasc`: 안건명 오름차순)

    * `ldes`: 안건명 내림차순
    * `dasc`: 의결일자 오름차순 / `ddes`: 의결일자 내림차순
    * `nasc`: 의안번호 오름차순 / `ndes`: 의안번호 내림차순
  * `popYn` 지원

* **샘플 요청:**

  1. 개인정보위 결정문 **HTML 목록** 조회:
     `.../lawSearch.do?OC=test&target=ppc&type=HTML`
  2. 개인정보위 결정문 **XML 목록** 조회:
     `.../lawSearch.do?OC=test&target=ppc&type=XML`

* **응답 필드:**

  * 기본 구조는 권익위와 유사하나, 항목명이 약간 다름:
  * `기관명` (위원회명)
  * `ppc id` (결과 순번)
  * `결정문 일련번호`
  * `안건명` (string)
  * `의안번호` (string)
  * `회의종류`, `결정구분`, `의결일` (string)
  * `결정문 상세링크`

### 개인정보보호위원회 결정문 본문 조회 API

* **요청 URL:** `http://www.law.go.kr/DRF/lawService.do?target=ppc`
* **요청 변수:** `ID` (결정문 일련번호) 등.
* **응답:** 개인정보위 결정문 전문 (안건 내용, 결정 요지 등).

### 국가인권위원회 결정문 목록/본문 조회 API

* **목록 조회 URL:** `.../lawSearch.do?target=nhrck` (인권위)
* **본문 조회 URL:** `.../lawService.do?target=nhrck`
* 사용법은 개인정보위와 유사하나, **목록 검색 기본 필드**가 명시되어 있지 않아 추정컨대 `search=1`(사건명)으로 동작.
* **본문 조회**는 앞서 **국가인권위원회 결정문 본문 조회 API** 예시에서 다룬 대로 `ID`로 결정문 전문을 조회합니다.

인권위 결정문의 응답 필드는 권익위와 유사한 구조이며, **의결서** 형태의 결정문을 반환합니다 (주문, 이유, 결정요지 등).

## 그 밖의 데이터셋 API

**조약, 별표·서식, 학칙/공단/공공기관, 법령용어, 맞춤형 서비스** 등에 대한 API도 제공됩니다:

* **조약 목록 조회 / 본문 조회 API:** 국제조약의 목록 및 전문 제공 (`target=treaty` 등 추정).

* **별표·서식 목록 조회 API:** 법령/행정규칙/자치법규의 별표 및 서식 목록 (`target=att` 등; 본문은 없음).

* **학칙·공단·공공기관 법규 목록/본문 API:** 각 대학 학칙이나 공공기관 규정 등의 목록/본문 (`target=orglaw` 등).

* **법령용어 조회 API:** 법령상 용어 정의 조회 (`target=lawterm`).

* **일상용어 조회 API:** 일반 생활용어로 대응되는 법령용어 조회 (`target=commonterm`).

* **용어 간 관계 조회 API:** 법령용어와 일상용어의 연계 관계 (`target=termlink`).

* **조문-용어 연계 조회 API:** 특정 용어가 등장하는 조문 목록.

* **관련법령 조회 API:** 법령 간 관계 (상호참조 등) 조회.

* **맞춤형 법령/행정규칙/자치법규 목록/조문 조회 API:** 특정 기관이나 이용자 설정에 따른 맞춤형 목록 제공 (`target=custLsList`, `custLsJoList` 등).

  * 예: 맞춤형 법령 목록 조회 (`target=custLs`)는 제공자가 설정한 범위의 법령만 목록화.
  * 맞춤형 법령 조문 목록 (`custLsJo`) 등도 있음.

각 API는 **target 파라미터**로 구분되며, 요청/응답 구조는 위에 소개된 일반 법령/판례 API와 유사하게 구성되어 있습니다.

---

以上의 내용을 통해 OPEN API에서 활용 가능한 엔드포인트와 세부 설정값들을 모두 살펴보았습니다. 필요한 API의 **요청 URL과 파라미터를 정확히 설정**하여 호출하면, 국가법령정보센터의 다양한 법령정보 데이터를 프로그램으로 활용할 수 있습니다.&#x20;
