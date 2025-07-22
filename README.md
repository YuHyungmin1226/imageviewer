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
  - Flask 기반의 간단한 개인 SNS(게시판) 웹앱입니다.
  - 텍스트, 이미지, 동영상, 오디오 파일 첨부 게시글 작성 가능
- **실행 방법:**
  1. 필요한 패키지 설치
     ```bash
     pip install -r personal_sns_app/requirements.txt
     ```
  2. 앱 실행
     ```bash
     cd personal_sns_app
     python app.py
     ```
  3. 브라우저에서 `http://localhost:5001` 접속
- **주요 기능:**
  - 게시글 CRUD(생성, 삭제, 댓글, 좋아요)
  - 파일 업로드 및 미리보기
  - URL 미리보기(og 태그 파싱)

---

## 폴더 구조 예시

```
Workspace/
├── personal_sns_app/
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   └── uploads/
├── web_timetable_app/
│   ├── streamlit_timetable.py
│   └── requirements.txt
├── README.md
└── requirements.txt (전체 의존성 목록, 선택)
```

---

> 각 프로젝트별 상세 설명 및 사용법은 각 폴더의 README.md 또는 주석을 참고하세요.
