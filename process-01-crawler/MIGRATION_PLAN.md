# Process-01 파일 정리 및 마이그레이션 계획

## 📋 현재 파일 현황

| 파일명 | 크기 | 특징 | 생성 시기 |
|--------|------|------|-----------|
| process-01-law-api.py | 10.7KB | 기본형 (자동 실행) | 초기 버전 |
| process-01-law-api-interactive.py | 11.9KB | 대화형 (사용자 입력) | v2 |
| process-01-law-api-advanced.py | 22.3KB | 고급형 (메뉴 시스템) | v3 |
| process-01-law-api-json.py | 17.2KB | JSON 전용 (최신) | v4 |

## 🎯 최종본 선정 계획

### Option 1: JSON 버전을 최종본으로 (권장) ✅
```
process-01-law-api-json.py → process-01-law-api.py (최종본)
```

**장점:**
- 가장 최신 기술 (JSON 파싱)
- 데이터 처리가 가장 효율적
- 구조화된 데이터 저장
- 미래 지향적

**통합 내용:**
- JSON 기본 + XML 호환성
- 대화형 모드 옵션 추가
- 고급 기능 선택적 포함

### Option 2: 통합 버전 생성 (대안)
```
새로운 process-01-law-api.py 생성 (모든 기능 통합)
```

**구조:**
```python
# process-01-law-api.py (통합 버전)
class LawAPIClient:
    def __init__(self, mode='auto'):
        # mode: 'auto', 'interactive', 'advanced'
        
    def run(self):
        if self.mode == 'auto':
            self.run_auto()
        elif self.mode == 'interactive':
            self.run_interactive()
        elif self.mode == 'advanced':
            self.run_advanced()
```

## 📦 버전별 보관 계획

### 1단계: 버전 명칭 부여
```bash
# 기존 파일 → 버전 명칭
process-01-law-api.py              → process-01-law-api_v1.0.0_basic.py
process-01-law-api-interactive.py  → process-01-law-api_v2.0.0_interactive.py
process-01-law-api-advanced.py     → process-01-law-api_v3.0.0_advanced.py
process-01-law-api-json.py         → process-01-law-api_v4.0.0_json.py
```

### 2단계: _history 폴더 구조
```
_history/
├── process-01-law-api_v1.0.0_basic.py
├── process-01-law-api_v2.0.0_interactive.py
├── process-01-law-api_v3.0.0_advanced.py
└── VERSION_HISTORY.md  # 각 버전 설명
```

## 🚀 실행 계획

### Phase 1: 백업 생성
```bash
# 현재 파일들 백업
cp process-01-law-api*.py _backup_$(date +%Y%m%d)/
```

### Phase 2: 최종본 생성 (Option 1 기준)
```bash
# JSON 버전을 개선하여 최종본으로
cp process-01-law-api-json.py process-01-law-api-final.py
# 기능 추가 및 개선
# - XML 호환성 유지
# - 실행 모드 선택 옵션
# - 명령줄 인자 지원
```

### Phase 3: 기존 파일 이동
```bash
# 버전 명칭 부여 후 이동
mv process-01-law-api.py _history/process-01-law-api_v1.0.0_basic.py
mv process-01-law-api-interactive.py _history/process-01-law-api_v2.0.0_interactive.py
mv process-01-law-api-advanced.py _history/process-01-law-api_v3.0.0_advanced.py
mv process-01-law-api-json.py _history/process-01-law-api_v4.0.0_json.py
```

### Phase 4: 최종본 배치
```bash
# 최종본을 정식 이름으로
mv process-01-law-api-final.py process-01-law-api.py
```

## 📝 최종본 기능 명세

### process-01-law-api.py (최종 통합 버전)

#### 기본 기능
- [x] JSON 형식 우선 지원
- [x] XML 형식 호환성 유지
- [x] 민감정보 자동 제거
- [x] 세션별 폴더 구조

#### 실행 모드
```bash
# 자동 모드 (기본)
python process-01-law-api.py

# 대화형 모드
python process-01-law-api.py --interactive

# 고급 모드
python process-01-law-api.py --advanced

# 특정 법령 직접 다운로드
python process-01-law-api.py --law "법인세법"

# 형식 지정
python process-01-law-api.py --format json
python process-01-law-api.py --format xml
python process-01-law-api.py --format both
```

#### 통합 기능
1. **기본 모드**: 사전 정의된 법령 목록 자동 다운로드
2. **대화형 모드**: 검색어 입력 → 선택 → 다운로드
3. **고급 모드**: 메뉴 시스템, 조항별 조회
4. **직접 모드**: 명령줄에서 법령명 지정

## 🔄 마이그레이션 명령어 스크립트

```bash
#!/bin/bash
# migrate_process01.sh

# 1. 백업 디렉토리 생성
BACKUP_DIR="_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 2. 현재 파일 백업
cp process-01-law-api*.py "$BACKUP_DIR/"

# 3. _history 디렉토리 생성
mkdir -p _history

# 4. 버전 명칭 부여 및 이동
mv process-01-law-api.py _history/process-01-law-api_v1.0.0_basic.py
mv process-01-law-api-interactive.py _history/process-01-law-api_v2.0.0_interactive.py
mv process-01-law-api-advanced.py _history/process-01-law-api_v3.0.0_advanced.py

# 5. JSON 버전을 최종본으로 개선
cp process-01-law-api-json.py process-01-law-api.py

echo "✅ 마이그레이션 완료!"
echo "📁 백업 위치: $BACKUP_DIR"
echo "📁 이전 버전: _history/"
echo "📋 최종본: process-01-law-api.py"
```

## 📊 결정 필요 사항

### 질문 1: 최종본 선택
- [ ] **Option 1**: JSON 버전 기반 (권장)
- [ ] **Option 2**: 새로운 통합 버전 생성

### 질문 2: 기능 포함 범위
- [ ] 최소 기능 (JSON + 기본 다운로드)
- [ ] 중간 기능 (+ 대화형 모드)
- [ ] 전체 기능 (+ 고급 모드, 조항별 조회)

### 질문 3: 명령줄 인터페이스
- [ ] argparse 사용한 CLI 지원
- [ ] 환경변수 설정 지원
- [ ] 설정 파일 지원

## 🎯 권장 진행 방향

1. **JSON 버전을 기반으로 최종본 생성** (가장 현대적)
2. **대화형 모드를 옵션으로 추가** (사용성 향상)
3. **기존 파일들은 버전 명시하여 _history 보관** (참고용)
4. **README.md 업데이트** (새로운 사용법 문서화)

이 계획대로 진행하시겠습니까? 아니면 다른 방향을 선호하시나요?