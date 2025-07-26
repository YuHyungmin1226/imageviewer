@echo off
echo ========================================
echo Flask SNS 애플리케이션 정리
echo ========================================
echo.

echo Docker 컨테이너를 중지하고 정리합니다...
cd docker && docker-compose down

echo Docker 이미지를 삭제합니다...
docker rmi flask-sns-app 2>nul
docker rmi flask_sns_app-flask-sns-app 2>nul

echo 정리 완료!
pause 