#!/bin/bash

echo "웹 시간표 애플리케이션을 시작합니다..."

# 웹 시간표 앱 디렉토리로 이동
cd web_timetable_repo

# 가상환경 활성화 (있는 경우)
if [ -d "../.venv" ]; then
    echo "가상환경을 활성화합니다..."
    source ../.venv/bin/activate
fi

# 필요한 패키지 설치
echo "패키지를 설치합니다..."
pip install -r requirements.txt

echo "웹 시간표 앱을 실행합니다..."
echo "브라우저에서 http://localhost:8501 으로 접속하세요."
echo "종료하려면 Ctrl+C를 누르세요."

# 앱 실행
streamlit run streamlit_timetable.py 