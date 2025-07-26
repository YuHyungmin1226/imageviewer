@echo off
echo ========================================
echo Flask SNS 애플리케이션 시작
echo ========================================
echo.

REM Docker가 설치되어 있는지 확인
docker --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Docker가 설치되지 않았습니다.
    echo Docker Desktop을 설치하고 실행한 후 다시 시도하세요.
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Docker가 실행 중인지 확인
docker info >nul 2>&1
if errorlevel 1 (
    echo 오류: Docker가 실행되지 않았습니다.
    echo Docker Desktop을 실행한 후 다시 시도하세요.
    pause
    exit /b 1
)

echo Docker 이미지를 빌드하고 애플리케이션을 시작합니다...
echo.

REM 기존 컨테이너가 있다면 중지
cd docker && docker-compose down

REM 이미지 빌드 및 컨테이너 시작
docker-compose up --build

echo.
echo 애플리케이션이 종료되었습니다.
pause 