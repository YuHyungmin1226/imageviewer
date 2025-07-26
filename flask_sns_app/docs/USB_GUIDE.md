# 🚀 USB 포터블 Flask SNS 애플리케이션 사용법

## 📋 USB 준비

1. **USB 메모리 준비**: 최소 1GB 이상의 여유 공간이 있는 USB 메모리
2. **전체 폴더 복사**: `flask_sns_app` 폴더 전체를 USB에 복사

## 🔧 사용 방법

### Windows 사용자
1. USB를 컴퓨터에 연결
2. USB 내의 `flask_sns_app` 폴더로 이동
3. `start.bat` 파일을 더블클릭
4. 브라우저에서 `http://localhost:5001` 접속

### macOS/Linux 사용자
1. USB를 컴퓨터에 연결
2. 터미널에서 USB의 `flask_sns_app` 폴더로 이동
3. `./start.sh` 실행
4. 브라우저에서 `http://localhost:5001` 접속

## ⚠️ 주의사항

- **Docker Desktop 필수**: 사용하기 전에 Docker Desktop을 설치해야 합니다
- **관리자 권한**: 일부 시스템에서는 관리자 권한이 필요할 수 있습니다
- **방화벽**: 방화벽에서 포트 5001을 허용해야 할 수 있습니다

## 🛠️ 문제 해결

### Docker가 설치되지 않은 경우
```
오류: Docker가 설치되지 않았습니다.
```
**해결방법**: Docker Desktop을 설치하세요
- Windows/macOS: https://www.docker.com/products/docker-desktop
- Linux: https://docs.docker.com/engine/install/

### 포트가 사용 중인 경우
```
Error: Port 5001 is already in use
```
**해결방법**: 
1. `cleanup.bat` 또는 `./cleanup.sh` 실행
2. 다시 `start.bat` 또는 `./start.sh` 실행

### 권한 오류 (Linux/macOS)
```
Permission denied: ./start.sh
```
**해결방법**: 
```bash
chmod +x start.sh
chmod +x cleanup.sh
```

## 📞 지원

문제가 발생하면:
1. Docker Desktop이 실행 중인지 확인
2. 포트 5001이 사용 가능한지 확인
3. 방화벽 설정 확인
4. 관리자 권한으로 실행

## 🔑 기본 계정
- **관리자**: `admin` / `admin123`
- **권장**: 첫 로그인 시 비밀번호 변경

---
**이 애플리케이션은 USB에 담아 어디서든 실행할 수 있습니다!** 🎉 