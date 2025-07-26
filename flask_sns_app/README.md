# Flask SNS 애플리케이션

Flask 기반의 소셜 네트워킹 서비스 애플리케이션입니다.

## 📁 프로젝트 구조

```
flask_sns_app/
├── app.py                 # 메인 애플리케이션 파일
├── run.py                 # 애플리케이션 실행 스크립트
├── requirements.txt       # Python 의존성 패키지
├── templates/            # HTML 템플릿 파일들
├── instance/             # 데이터베이스 파일 (자동 생성)
├── uploads/              # 업로드된 파일들 (자동 생성)
│
├── docker/               # Docker 관련 파일들
│   ├── Dockerfile        # Docker 이미지 설정
│   ├── docker-compose.yml # 컨테이너 오케스트레이션
│   └── .dockerignore     # Docker 빌드 제외 파일
│
├── scripts/              # 실행 스크립트들
│   ├── start.bat         # Windows 실행 스크립트
│   ├── start.sh          # macOS/Linux 실행 스크립트
│   ├── cleanup.bat       # Windows 정리 스크립트
│   └── cleanup.sh        # macOS/Linux 정리 스크립트
│
├── docs/                 # 문서 파일들
│   ├── README.md         # 상세한 사용법 가이드
│   ├── README_PORTABLE.md # 포터블 버전 사용법
│   └── USB_GUIDE.md      # USB 사용 간단 가이드
│
├── utils/                # 유틸리티 모듈들
│   ├── __init__.py       # 패키지 초기화 파일
│   ├── file_utils.py     # 파일 처리 유틸리티
│   └── url_utils.py      # URL 처리 유틸리티
│
├── tests/                # 테스트 파일들
│   └── test_upload.py    # 파일 업로드 테스트
│
└── config/               # 설정 파일들
    └── production.py     # 프로덕션 환경 설정
```

## 🚀 빠른 시작

### 일반 실행 (로컬 환경)
```bash
python3 run.py
```

### Docker 실행 (포터블)
```bash
# Windows
scripts/start.bat

# macOS/Linux
./scripts/start.sh
```

## 📋 주요 기능

- ✅ 사용자 등록/로그인/로그아웃
- ✅ 게시물 작성/조회/삭제
- ✅ 댓글 작성
- ✅ 파일 업로드 및 미디어 미리보기
- ✅ URL 미리보기 생성
- ✅ 관리자 기능
- ✅ 반응형 웹 디자인

## 🔑 기본 계정

- **관리자**: `admin` / `admin123`

## 📖 상세 문서

- [상세 사용법](docs/README.md)
- [포터블 버전 사용법](docs/README_PORTABLE.md)
- [USB 사용 가이드](docs/USB_GUIDE.md)

## 🛠️ 개발 환경

- Python 3.11+
- Flask 2.3.3
- SQLite 데이터베이스
- Docker (포터블 버전)

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다. 