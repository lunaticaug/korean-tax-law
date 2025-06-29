Q7. 2025-06-29 (Sun) 04:33

````markdown
# 이번 세션 대화 요약

## 1. LangChain PromptTemplate 기초
- **PromptTemplate**: `{variable}` 자리표시자를 가진 문자열 템플릿, `.format()`으로 값 삽입  
- **ChatPromptTemplate**: system/human/ai 역할을 리스트로 구성해 챗용 멀티턴 템플릿 생성  
- 부분 고정 (`partial`), 템플릿 저장 · 로드, few-shot 템플릿 등 확장 기능 소개

---

## 2. 법조문 Skeleton + Keyword Pair 분석 방법
- 반복 구문을 Skeleton으로 추출하고 `{X},{Y}` 등의 **가변 키워드**만 테이블화  
- 예시① **국세기본법 §45(수정신고) vs §45-2(경정청구)**  
  - Skeleton: “과세표준신고서 … {X}에 {Y} 때”  
  - Case·Keys 테이블로 “과세표준·세액/미치지 못할 ↔ 초과할” 등 차이만 표시  
- 예시② **X〈If ΔX〉→ Y〈then〉** 구조(재무관리 기출)에도 동일 기법 적용

---

## 3. 세법 내 유사 조문쌍 확장 분석
| Pair | Skeleton 공통부 | 변수·차이점 |
|------|----------------|-------------|
|A|국기법 §45/§45-2|Target, Cond|
|B|부가가치세법 §18/§19|Period, Due|
|C|소득세법 §70 vs 법인세법 §60|Taxpayer, Period, Limit|

---

## 4. RDBMS 스키마 제안
```text
laws ─┐
articles ─┬─ cases ─┬─ keyword_values
skeletons ─┘         └─ variables
functions / func_steps (다단 함수식 저장)
````

* Skeleton ↔ Article N\:M, 다중 키워드 행(`kv_order`) 지원
* 함수형 조합(X→Y→Z) 저장 테이블 분리
* 효력기간(eff\_start/eff\_end)로 개정 추적

---

## 5. 공인회계사법 §21 & 시행령 §14 분석

* Skeleton S1: “공인회계사는 **{Target}** … 직무를 행할 수 없다”
* “대통령령으로 정하는 자” Placeholder를 시행령에서 다섯 세부값으로 확장
* LangChain 코드 한 줄로 법·령 문장 모두 재생성
* `links_act_decr` 테이블로 법↔령 조문 매핑

---

## 6. 중첩 “다만” 예외 → 합성 PromptTemplate

```
Prohibit(Target)
  ∘ Except₁(Exception₁,
        Except₂(Exception₂_list))
```

* 함수 합성 / 재귀로 ‘다만’이 몇 단계든 대응
* DB `clauses(parent_id)` 트리 설계 → 본칙-예외 계층 관리

---

## 7. 활용 아이디어

* **수험·교육**: Skeleton + 테이블로 빈칸·OX·객관식 자동 생성
* **컴플라이언스/RPA**: ERP 데이터와 변수값 비교·알림
* **법령 모니터링**: Skeleton 변동·예외 추가만 diff 추적
* **LLM Ops**: Few-Shot PromptTemplate 저장 → 새 조문 입력 시 자동 요약

```
```
