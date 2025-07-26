# Flask SNS 애플리케이션 - 포터블 버전

이 프로젝트는 USB에 담아 어디서든 실행할 수 있는 Flask SNS 애플리케이션입니다.

## 🚀 빠른 시작

### Windows 사용자
1. `start.bat` 파일을 더블클릭하여 실행
2. 브라우저에서 `http://localhost:5000` 접속

### macOS/Linux 사용자
1. 터미널에서 `./start.sh` 실행
2. 브라우저에서 `http://localhost:5000` 접속

## 📋 사전 요구사항

- **Docker Desktop**이 설치되어 있어야 합니다
  - Windows: https://www.docker.com/products/docker-desktop
  - macOS: https://www.docker.com/products/docker-desktop
  - Linux: https://docs.docker.com/engine/install/

## 🔧 설치 및 실행

### 1. Docker Desktop 설치
- 위 링크에서 운영체제에 맞는 Docker Desktop을 다운로드하여 설치
- 설치 후 Docker Desktop을 실행

### 2. 애플리케이션 실행
- USB를 컴퓨터에 연결
- USB 내의 `flask_sns_app` 폴더로 이동
- 운영체제에 맞는 실행 스크립트 실행

### 3. 웹 브라우저 접속
- 브라우저에서 `http://localhost:5000` 접속
- 기본 관리자 계정: `admin` / `admin123`

## 📁 프로젝트 구조

```
flask_sns_app/
├── app.py                 # 메인 애플리케이션 파일
├── run.py                 # 실행 스크립트
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 이미지 설정
├── docker-compose.yml    # Docker Compose 설정
├── start.bat            # Windows 실행 스크립트
├── start.sh             # macOS/Linux 실행 스크립트
├── templates/           # HTML 템플릿
├── instance/           # 데이터베이스 파일 (자동 생성)
└── uploads/            # 업로드된 파일 (자동 생성)
```

## 🔑 기본 계정 정보

- **관리자 계정**: `admin` / `admin123`
- **권장사항**: 첫 로그인 시 비밀번호 변경

## 🛠️ 문제 해결

### Docker가 설치되지 않은 경우
1. Docker Desktop을 설치
2. Docker Desktop을 실행
3. 다시 실행 스크립트 실행

### 포트 5000이 사용 중인 경우
- 다른 애플리케이션이 포트 5000을 사용하고 있을 수 있습니다
- Docker Compose가 자동으로 포트를 관리하므로 일반적으로 문제없습니다

### 데이터베이스 오류
- `instance` 폴더를 삭제하고 다시 시작하면 초기화됩니다
- 모든 데이터가 삭제되므로 주의하세요

## 📝 주요 기능

- ✅ 사용자 등록/로그인
- ✅ 게시물 작성/조회
- ✅ 파일 업로드
- ✅ 관리자 기능
- ✅ 반응형 웹 디자인

## 🔒 보안 주의사항

- 기본 비밀번호는 반드시 변경하세요
- 공용 네트워크에서는 방화벽 설정을 확인하세요
- 중요한 데이터는 정기적으로 백업하세요

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Docker Desktop이 실행 중인지 확인
2. 포트 5000이 사용 가능한지 확인
3. 방화벽 설정 확인

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다. 