#!/bin/bash

echo "========================================"
echo "Flask SNS 애플리케이션 시작"
echo "========================================"
echo

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Docker가 설치되어 있는지 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}오류: Docker가 설치되지 않았습니다.${NC}"
    echo "Docker Desktop을 설치하고 실행한 후 다시 시도하세요."
    echo "https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Docker가 실행 중인지 확인
if ! docker info &> /dev/null; then
    echo -e "${RED}오류: Docker가 실행되지 않았습니다.${NC}"
    echo "Docker Desktop을 실행한 후 다시 시도하세요."
    exit 1
fi

echo -e "${GREEN}Docker 이미지를 빌드하고 애플리케이션을 시작합니다...${NC}"
echo

# 기존 컨테이너가 있다면 중지
echo -e "${YELLOW}기존 컨테이너를 중지합니다...${NC}"
cd docker && docker-compose down

# 이미지 빌드 및 컨테이너 시작
echo -e "${YELLOW}이미지를 빌드하고 컨테이너를 시작합니다...${NC}"
docker-compose up --build

echo
echo -e "${GREEN}애플리케이션이 종료되었습니다.${NC}" 