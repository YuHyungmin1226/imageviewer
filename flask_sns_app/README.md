# 🏠 Flask 기반 개인 SNS 플랫폼

Streamlit에서 Flask로 변경된 **개인/소규모 조직용 SNS 플랫폼**입니다. 로컬 SQLite 데이터베이스를 사용하여 외부 클라우드 서비스 없이도 독립적으로 운영할 수 있습니다.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 주요 변경사항

### 🔄 Streamlit → Flask 변경
- **웹 프레임워크**: Streamlit → Flask
- **데이터베이스**: Supabase → SQLite (로컬)
- **배포**: 클라우드 의존성 제거
- **UI**: Bootstrap 기반 반응형 웹 인터페이스

### 🎯 새로운 특징
- **완전 로컬 운영**: 외부 서비스 없이 독립 실행
- **SQLite 데이터베이스**: 단일 파일로 데이터 관리
- **Bootstrap UI**: 모던하고 반응형인 웹 인터페이스
- **다크모드 지원**: 사용자 선호도에 따른 테마 변경
- **실시간 URL 미리보기**: YouTube 및 일반 웹사이트 지원

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/YuHyungmin1226/HMYU.git
cd HMYU/flask_sns_app
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 종속성 설치
```bash
pip install -r requirements.txt
```

### 4. 앱 실행
```bash
python run.py
```

브라우저에서 `http://localhost:5000`으로 접속하세요.

## 🔑 기본 계정

- **관리자 계정**: `admin` / `admin123`
- 첫 로그인 시 비밀번호 변경 권장

## 📁 프로젝트 구조

```
flask_sns_app/
├── app.py                 # 메인 Flask 애플리케이션
├── url_utils.py           # URL 미리보기 생성
├── run.py                 # 실행 스크립트
├── requirements.txt       # Python 종속성
├── templates/             # HTML 템플릿
│   ├── base.html         # 기본 레이아웃
│   ├── login.html        # 로그인 페이지
│   ├── register.html     # 회원가입 페이지
│   ├── index.html        # 메인 페이지
│   ├── new_post.html     # 새 글 작성
│   ├── view_post.html    # 게시글 상세보기
│   ├── profile.html      # 사용자 프로필
│   └── admin.html        # 관리자 패널
└── sns.db                # SQLite 데이터베이스 (자동 생성)
```

## 🛠️ 기술 스택

### 백엔드
- **Flask 2.3+** - 웹 프레임워크
- **Flask-SQLAlchemy** - ORM
- **Flask-Login** - 사용자 인증
- **SQLite** - 로컬 데이터베이스
- **Werkzeug** - 보안 (비밀번호 해싱)

### 프론트엔드
- **Bootstrap 5** - CSS 프레임워크
- **Bootstrap Icons** - 아이콘
- **JavaScript** - 동적 기능

### 기타
- **BeautifulSoup4** - 웹 스크래핑 (URL 미리보기)
- **Requests** - HTTP 요청
- **Pillow** - 이미지 처리

## ✨ 주요 기능

### 🔐 사용자 관리
- **회원가입/로그인** - 보안 세션 관리
- **계정 잠금** - 로그인 시도 제한 (5회 실패 시 15분 잠금)
- **관리자 패널** - 사용자 관리 및 삭제
- **프로필 관리** - 개인 게시글 목록

### 📝 게시물 시스템
- **텍스트 게시물** 작성
- **공개/비공개** 설정
- **URL 자동 감지** 및 미리보기
- **YouTube 링크** 특별 지원
- **게시글 삭제** (작성자만)

### 💬 댓글 시스템
- 게시물별 **댓글 작성/표시**
- **실시간 업데이트**
- 카드 내 통합 UI

### 🎨 UI/UX
- **다크모드/라이트모드** 자동 지원
- **반응형 디자인** (모바일/데스크톱)
- **모던한 카드 레이아웃**
- **직관적인 인터페이스**
- **플래시 메시지** 알림

### 🔧 관리자 기능
- **사용자 관리** - 목록, 삭제
- **게시글 관리** - 목록, 상세보기
- **통계 대시보드** - 사용자/게시글 수

## 🌐 배포 옵션

### 로컬 실행 (권장)
```bash
python run.py
```

### 프로덕션 배포
```bash
# Gunicorn 사용 (Linux/macOS)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Windows 서비스로 등록
# 또는 Docker 컨테이너로 배포
```

### Docker 배포
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## 🔒 보안 기능

- **SHA-256 비밀번호 해싱**
- **계정 잠금 시스템** (5회 실패 시 15분)
- **세션 관리** (Flask-Login)
- **CSRF 보호** (Flask-WTF)
- **XSS 방지** (HTML 이스케이프)
- **SQL 인젝션 방지** (SQLAlchemy ORM)

## 📊 데이터베이스 스키마

### Users 테이블
- `id`: 고유 식별자
- `username`: 사용자명 (고유)
- `password_hash`: 해시된 비밀번호
- `created_at`: 가입일
- `last_login`: 마지막 로그인
- `login_attempts`: 로그인 시도 횟수
- `locked_until`: 계정 잠금 해제 시간

### Posts 테이블
- `id`: 고유 식별자
- `content`: 게시글 내용
- `author_id`: 작성자 ID (외래키)
- `created_at`: 작성일
- `updated_at`: 수정일
- `is_public`: 공개 여부
- `url_previews`: URL 미리보기 JSON

### Comments 테이블
- `id`: 고유 식별자
- `content`: 댓글 내용
- `author_id`: 작성자 ID (외래키)
- `post_id`: 게시글 ID (외래키)
- `created_at`: 작성일

## 🐛 문제 해결

### 앱이 실행되지 않을 때
1. Python 버전 확인 (3.8+)
2. 종속성 재설치: `pip install -r requirements.txt`
3. 포트 충돌 확인: 다른 포트 사용
4. 가상환경 활성화 확인

### 데이터베이스 오류
1. `sns.db` 파일 삭제 후 재생성
2. 권한 문제 확인 (쓰기 권한)
3. 디스크 공간 확인

### URL 미리보기 오류
1. 네트워크 연결 확인
2. 방화벽 설정 확인
3. 일시적인 서버 오류일 수 있음

## 🔄 기존 Streamlit 버전과의 차이점

| 기능 | Streamlit 버전 | Flask 버전 |
|------|----------------|------------|
| 프레임워크 | Streamlit | Flask |
| 데이터베이스 | Supabase (클라우드) | SQLite (로컬) |
| 배포 | Streamlit Cloud | 로컬/서버 |
| UI | Streamlit 컴포넌트 | Bootstrap |
| 실시간 업데이트 | 제한적 | 완전 지원 |
| 커스터마이징 | 제한적 | 자유로운 커스터마이징 |
| 확장성 | 제한적 | 높음 |

## 📝 개발 로그

### v2.0.0 (Flask 버전)
- ✅ Streamlit → Flask 마이그레이션
- ✅ Supabase → SQLite 변경
- ✅ Bootstrap UI 구현
- ✅ 다크모드 지원
- ✅ 관리자 패널 추가
- ✅ 보안 기능 강화

### 향후 계획
- 🔄 파일 업로드 기능
- 🔄 알림 시스템
- 🔄 좋아요/반응 기능
- 🔄 태그 시스템
- 🔄 검색 기능

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 🙋‍♂️ 지원

문제가 있거나 기능 요청이 있으시면 GitHub Issues를 통해 연락주세요.

---

**💡 Tip**: 이제 외부 서비스 없이도 완전히 독립적으로 SNS를 운영할 수 있습니다! 