# Personal SNS App

Flask 기반의 개인 SNS 웹앱입니다.

## 주요 기능
- 게시글/댓글 작성, 좋아요
- 첨부파일 업로드(이미지, 동영상, 오디오만 지원)
- 대화명(닉네임) 설정 및 유지(localStorage)
- 본인 글 삭제(삭제 버튼)
- 대화명 클릭 시 멘션 자동 입력
- 게시글 내 URL 자동 하이퍼링크 및 링크 미리보기(썸네일, 제목, 설명)
- 입력창 자동 높이 조절, shift+enter 줄바꿈, enter로 바로 게시
- 업로드 파일 다운로드/스트리밍 지원

## 폴더 구조
- `app.py` : 백엔드(Flask)
- `templates/index.html` : 프론트엔드(HTML+JS)
- `uploads/` : 첨부파일 저장 폴더
- `posts.json` : 게시글/댓글 데이터 저장

## 실행 방법
1. Python 3.8+ 및 가상환경(.venv) 활성화
2. 필요한 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```
3. 서버 실행
   ```bash
   python app.py
   ```
4. 브라우저에서 http://localhost:5001 접속

## 의존성
- Flask
- requests
- beautifulsoup4
- python-dotenv

## 기타
- 문서 업로드 기능은 제거됨
- uploads 폴더는 personal_sns_app 내부만 사용 