# Joya 글로벌 키즈 교육 동화 - 자동 조판 시스템 설계

## 프로젝트 개요

8개 국어 대응 글로벌 키즈 교육 동화 "Joya"의 맞춤형 자동 조판 시스템.
사용자가 선택한 4개 언어(메인 1 + 서브 3)와 개인화 데이터(이름, 날짜)를 서버 측에서 실시간 매핑하여,
상업 인쇄용 고해상도 PDF(300dpi, CMYK, Bleed 포함)를 생성하는 엔진 구축.

- **예산**: 2,500만원 (VAT 별도)
- **개발 기간**: 3개월
- **산출물**: 입찰 제안서 + 동작하는 MVP 프로토타입

---

## 1. 시스템 아키텍처

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│   Next.js (Vercel)  │────>│  FastAPI (Railway)    │────>│ PostgreSQL  │
│   관리자 UI          │ API │  PDF 생성 엔진         │     │ (Supabase)  │
│                     │<────│  ReportLab            │     │             │
└─────────────────────┘     └──────────┬───────────┘     └─────────────┘
                                       │
                                       v
                            ┌──────────────────────┐
                            │  S3 / R2 (PDF 저장)   │
                            └──────────────────────┘
```

### 3개 레이어

- **프론트엔드**: Next.js App Router -- 관리자 대시보드, 도서/원고 CRUD, 주문 관리
- **백엔드 API**: FastAPI -- 다국어 텍스트 매핑, 개인화 치환, PDF 생성 오케스트레이션
- **PDF 엔진**: ReportLab (FastAPI 내부) -- 300dpi CMYK PDF 직접 생성, 폰트 임베딩
- **저장소**: PostgreSQL (원고/주문 데이터) + S3 호환 스토리지 (생성된 PDF)

### 데이터 흐름

1. 관리자가 도서/페이지/언어별 원고 데이터 입력
2. 사용자(또는 관리자 시뮬레이션)가 이름/날짜/언어 4종 선택
3. FastAPI가 DB에서 해당 언어 텍스트 조회 + {NAME}/{DATE} 치환
4. ReportLab이 페이지별 레이아웃에 텍스트/이미지 배치 -> PDF 생성
5. 생성된 PDF를 S3에 저장하고 다운로드 URL 반환

---

## 2. 데이터 모델

### 핵심 테이블 5개

| 테이블 | 역할 |
|--------|------|
| **Book** | 도서 메타정보. 페이지 규격(8.5x11"), 도련(bleed) 설정 |
| **Page** | 페이지별 정보. 배경 이미지, 텍스트 영역 좌표, 개인화 여부(표지/오프닝/클로징) |
| **PageContent** | 페이지x언어별 실제 텍스트. {NAME}, {DATE} 플레이스홀더 포함 |
| **FontPreset** | 언어별 폰트 설정. TTF/OTF 파일 경로, 자간, 행간 (베트남어 행간 별도 설정) |
| **Order** | 주문 이력. 선택 언어 4종, 개인화 데이터(이름/날짜), 생성된 PDF URL, 상태 |

### 스키마

```
Book
  id, title, page_size, bleed_mm, created_at

Page
  id, book_id (FK), page_number, page_type (enum: cover/opening/story/closing),
  bg_image_url, text_area_x, text_area_y, text_area_w, text_area_h, is_personalizable

PageContent
  id, page_id (FK), language (enum: ko/en/vi/fr), text_content, font_preset_id (FK)

FontPreset
  id, language (enum), font_family, font_file_url, font_size,
  letter_spacing, line_height, created_at

Order
  id, book_id (FK), main_language, sub_languages[], person_name,
  person_date, status (enum: pending/processing/completed/failed/timeout),
  pdf_url, created_at
```

---

## 3. PDF 생성 엔진 (ReportLab)

### 생성 파이프라인

1. **데이터 조회** -- DB에서 해당 언어 텍스트 + 폰트 프리셋 로드
2. **텍스트 치환** -- {NAME}, {DATE}를 실제 값으로 치환 (cover/opening/closing만)
3. **텍스트 처리** -- 언어별 자동 줄바꿈 계산 (텍스트 영역 w/h 기준)
   - 베트남어: line_height 가변 보정
   - auto-shrink 없음 (줄바꿈만 적용)
4. **페이지 렌더링** -- ReportLab Canvas에 페이지별 구성
   - 배경 이미지 배치 (300dpi)
   - 텍스트 영역에 4개 언어 텍스트 배치
   - Bleed 영역 포함 (8.5x11" + 3mm 도련)
5. **PDF 출력** -- CMYK 컬러 모드 + 폰트 풀 임베딩 + PDF/X 규격 메타데이터

### 핵심 처리 로직

| 기능 | 구현 방식 |
|------|----------|
| **CMYK 컬러** | ReportLab `CMYKColor` 네이티브 사용 |
| **300dpi** | Canvas 크기를 포인트 단위로 계산 (8.5x11" = 612x792pt), 이미지는 300dpi 원본 삽입 |
| **Bleed** | 페이지 크기에 도련(3mm = ~8.5pt) 추가. TrimBox/BleedBox 메타데이터 설정 |
| **폰트 임베딩** | `pdfmetrics.registerFont(TTFont(...))` TTF/OTF 풀 임베딩 |
| **다국어 줄바꿈** | 텍스트 영역 너비 기준 `Paragraph` + `ParagraphStyle`로 자동 줄바꿈 |
| **베트남어 성조** | FontPreset에서 베트남어 전용 line_height 값 별도 적용 |
| **개인화 치환** | Python `str.replace()`로 {NAME}, {DATE} 서버 측 치환 |

---

## 4. 관리자 UI (Next.js)

### 페이지 구성

```
/admin
  /dashboard        -- 대시보드 (최근 주문, 통계 요약)
  /books            -- 도서 목록
  /books/[id]       -- 도서 상세 (페이지 목록 + 편집)
  /books/[id]/pages/[pageId] -- 페이지별 언어 원고 편집
  /fonts            -- 언어별 폰트 프리셋 관리
  /orders           -- 주문 이력 목록
  /orders/[id]      -- 주문 상세 + PDF 다운로드/재생성
  /generate         -- PDF 생성 시뮬레이션 (데모용)
```

### 주요 화면별 기능

| 화면 | 기능 |
|------|------|
| **도서 관리** | 도서 CRUD. 페이지 규격/도련 설정 |
| **페이지 편집** | 배경 이미지 업로드, 텍스트 영역 좌표 설정, 개인화 여부 토글 |
| **원고 편집** | 페이지x언어별 텍스트 입력. {NAME}, {DATE} 플레이스홀더 삽입 버튼 |
| **폰트 프리셋** | 언어별 TTF/OTF 업로드, 폰트 크기/자간/행간 설정 |
| **주문 이력** | 주문 목록 조회, 상태 필터, PDF 다운로드, 재생성 버튼 |
| **PDF 생성** | 이름/날짜 입력 + 언어 4종 선택 -> PDF 생성 -> 미리보기/다운로드 |

### 기술 스택

- Next.js 15 App Router + TypeScript
- Tailwind CSS + shadcn/ui
- SWR (데이터 페칭/캐싱)
- FastAPI와 REST API 통신

---

## 5. 에러 처리 및 엣지 케이스

### 다국어 텍스트 처리

| 엣지 케이스 | 대응 방식 |
|------------|----------|
| 베트남어 성조 | UTF-8 정규화(NFC) 적용. 베트남어 전용 line_height 1.4~1.6배 |
| 프랑스어 악센트 | TTF 폰트에 글리프 포함 검증. 누락 시 관리자 경고 |
| 텍스트 영역 초과 | 자동 줄바꿈. 초과 시 Order에 warning 플래그 + 관리자 알림 |
| {NAME} 치환 후 길이 증가 | 줄바꿈 적용. auto-shrink 미적용 |
| 폰트 글리프 누락 | 폰트 등록 시 언어별 필수 문자셋 검증 API |

### PDF 생성 실패 처리

- 성공 -> status: "completed", pdf_url 저장
- 이미지 로드 실패 -> status: "failed", 관리자에 알림
- 폰트 로드 실패 -> status: "failed", 폰트 프리셋 확인 안내
- 타임아웃 (30초) -> status: "timeout", 재생성 가능

### 동시 요청 처리

- 프로토타입: FastAPI `BackgroundTasks`
- 본격 운영: AWS SQS + Lambda (제안서에 기술)

---

## 6. 프로토타입 범위

### 포함

- ReportLab CMYK PDF 생성, 폰트 임베딩
- 4개 언어 (한/영/베트남/불어)
- 개인화 치환, 자동 줄바꿈
- 관리자 UI 전체 (도서 CRUD, 원고 편집, 폰트 프리셋, 주문 이력, PDF 생성)
- 더미 동화 콘텐츠 3~5페이지
- Vercel + Railway + Supabase 배포

### 제외 (제안서에만 기술)

- PDF/X 완전 규격 인증, 8개 언어 전체
- 사용자 인증/권한, 대시보드 통계
- AWS 본격 구성 (SQS, Lambda)
- 실제 Joya 콘텐츠

---

## 7. 테스트 전략

### PDF 엔진 테스트 (pytest)

- 4개 언어 텍스트 정확 출력 (pdfplumber 추출 비교)
- 특수문자 무결성 (베트남어 성조, 프랑스어 악센트)
- {NAME}/{DATE} 치환 정확성
- 폰트 풀 임베딩 검증 (pikepdf)
- 페이지 규격 (8.5x11" + bleed 3mm)
- 텍스트 영역 초과 시 줄바꿈

### 관리자 UI 테스트 (vitest + Playwright)

- 도서 CRUD 정상 동작
- 원고 편집 저장/로드
- PDF 생성 E2E (언어 선택 -> 이름 입력 -> 생성 -> 다운로드)

### 도구

- Python 백엔드: pytest + httpx
- PDF 검증: pdfplumber, pikepdf
- Next.js UI: vitest + React Testing Library
- E2E: Playwright

---

## 제안서 목차

1. 프로젝트 이해 (요구사항 분석)
2. 기술 제안 (아키텍처, PDF 엔진, 다국어 처리, 개인화)
3. 관리자 시스템 설계 (화면 구성, 와이어프레임)
4. 인프라 및 배포 전략 (AWS 아키텍처, 부하 분산)
5. 개발 일정 (3개월, 3단계)
6. 견적 (2,500만원 내 항목별 비용)
7. 프로토타입 데모 (라이브 URL + 스크린샷)
