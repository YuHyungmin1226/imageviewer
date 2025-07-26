# HMYU 워크스페이스

이 저장소는 Python 기반 웹 프로젝트들의 모음입니다. 각 프로젝트는 독립적인 Git 저장소로 관리됩니다.

---

## 📁 프로젝트 구조

### 1. Flask SNS 애플리케이션
- **저장소:** `flask_sns_repo/`
- **설명:** Flask 기반의 소셜 네트워킹 서비스 애플리케이션
- **기술 스택:** Flask, SQLAlchemy, SQLite, HTML/CSS/JavaScript
- **주요 기능:** 사용자 인증, 게시물 CRUD, 댓글, 파일 업로드, 관리자 기능

### 2. 웹 시간표 애플리케이션
- **저장소:** `web_timetable_repo/`
- **설명:** Streamlit 기반의 학교 시간표 조회 웹앱
- **기술 스택:** Streamlit, NEIS Open API
- **주요 기능:** 학교 검색, 시간표 조회, 과목 하이라이트

---

## 🚀 각 프로젝트 실행 방법

### Flask SNS 앱 실행
```bash
cd flask_sns_repo
python3 run.py
```

### 웹 시간표 앱 실행
```bash
cd web_timetable_repo
streamlit run streamlit_timetable.py
```

---

## 📋 현재 디렉토리 구조

```
HMYU/
├── flask_sns_repo/          # Flask SNS 애플리케이션 (독립 저장소)
├── web_timetable_repo/      # 웹 시간표 애플리케이션 (독립 저장소)
├── .venv/                   # Python 가상환경
├── .devcontainer/           # VS Code Dev Container 설정
├── run.sh                   # 실행 스크립트
├── README.md                # 이 파일
└── .gitignore              # Git 제외 파일 설정
```

---

## 🔧 개발 환경

- **Python:** 3.11+
- **가상환경:** `.venv/`
- **Dev Container:** VS Code 개발 환경 자동 설정

---

## 📄 라이선스

이 프로젝트들은 교육 목적으로 제작되었습니다.

---

> 각 프로젝트의 상세한 설명과 사용법은 해당 저장소의 README.md를 참고하세요.
