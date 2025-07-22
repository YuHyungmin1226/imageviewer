#!/bin/bash

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Personal SNS 앱을 시작합니다..."

# 가상환경 생성 (없는 경우)
if [ ! -d ".venv" ]; then
    echo "가상환경을 생성합니다..."
    python3 -m venv .venv
fi

# 가상환경 활성화 및 패키지 설치
echo "패키지를 설치합니다..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# 업로드 폴더 생성
mkdir -p uploads

echo "SNS 앱을 실행합니다..."
echo "브라우저에서 http://localhost:5001 으로 접속하세요."
echo "종료하려면 Ctrl+C를 누르세요."

# 앱 실행 (에러는 로그 파일로 리다이렉트)
exec .venv/bin/python app.py 2>sns_error.log 