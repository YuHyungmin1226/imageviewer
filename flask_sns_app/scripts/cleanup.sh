#!/bin/bash

echo "========================================"
echo "Flask SNS 애플리케이션 정리"
echo "========================================"
echo

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Docker 컨테이너를 중지하고 정리합니다...${NC}"
cd docker && docker-compose down

echo -e "${YELLOW}Docker 이미지를 삭제합니다...${NC}"
docker rmi flask-sns-app 2>/dev/null || true
docker rmi flask_sns_app-flask-sns-app 2>/dev/null || true

echo -e "${GREEN}정리 완료!${NC}" 