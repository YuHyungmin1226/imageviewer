# Workspace 프로젝트 안내

이 저장소에는 다음과 같은 Python 기반 웹 프로젝트가 포함되어 있습니다.

---

## 1. web_timetable_app

- **설명:**
  - 전국 초·중·고등학교의 시간표를 NEIS Open API로 조회할 수 있는 Streamlit 기반 웹앱입니다.
- **실행 방법:**
  1. 필요한 패키지 설치
     ```bash
     pip install -r web_timetable_app/requirements.txt
     ```
  2. 웹앱 실행
     ```bash
     streamlit run web_timetable_app/streamlit_timetable.py
     ```
  3. 브라우저에서 `http://localhost:8501` 접속
- **주요 기능:**
  - 학교 검색 및 선택
  - 학년/반/주차별 시간표 조회
  - 과목 하이라이트 기능

---

## 2. personal_sns_app

- **설명:**
  - Streamlit 기반의 개인 SNS 웹앱입니다.
  - 텍스트, 이미지, 동영상, 오디오 파일 첨부 게시글 작성 가능
- **실행 방법:**
  1. 필요한 패키지 설치
     ```bash
     pip install -r personal_sns_app/requirements.txt
     ```
  2. Supabase 설정 (선택사항)
     - `.streamlit/secrets.toml` 파일에 Supabase URL과 API 키 설정
     - `supabase_schema.sql`을 Supabase SQL 편집기에서 실행
  3. 앱 실행
     ```bash
     cd personal_sns_app
     streamlit run app.py
     ```
  4. 브라우저에서 `http://localhost:8501` 접속
- **주요 기능:**
  - 게시글 CRUD(생성, 삭제, 댓글, 좋아요)
  - 파일 업로드 및 미리보기
  - 사용자 계정 관리 (회원가입/로그인)
  - 관리자 기능 (사용자 관리, 전체 게시글 관리)
  - Supabase 클라우드 데이터베이스 연동
  - 세션 지속성 (새로고침 후에도 로그인 유지)
- **기본 계정:**
  - **관리자**: `admin` / `admin123` (첫 로그인 시 비밀번호 변경 필요)
- **배포:**
  - Streamlit Cloud 배포 지원
  - 자세한 배포 가이드는 `personal_sns_app/DEPLOYMENT_GUIDE.md` 참조

---

## 폴더 구조 예시

```
Workspace/
├── personal_sns_app/
│   ├── app.py
│   ├── requirements.txt
│   ├── .streamlit/
│   │   └── secrets.toml
│   ├── uploads/
│   └── supabase_schema.sql
├── web_timetable_app/
│   ├── streamlit_timetable.py
│   └── requirements.txt
├── README.md
└── requirements.txt (전체 의존성 목록, 선택)
```

---

> 각 프로젝트별 상세 설명 및 사용법은 각 폴더의 README.md 또는 주석을 참고하세요.
