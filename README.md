# Personal SNS App

Streamlit 기반의 개인 SNS 웹앱입니다.

## 주요 기능
- 게시글/댓글 작성, 좋아요
- 첨부파일 업로드(이미지, 동영상, 오디오 지원)
- 사용자 계정 관리 (회원가입/로그인)
- 본인 글 삭제 및 공개/비공개 설정
- 관리자 기능 (사용자 관리, 전체 게시글 관리)
- Supabase 클라우드 데이터베이스 연동
- 세션 지속성 (새로고침 후에도 로그인 유지)

## 폴더 구조
- `app.py` : 메인 Streamlit 애플리케이션
- `uploads/` : 첨부파일 저장 폴더
- `posts.json` : 로컬 백업용 게시글 데이터
- `users.json` : 로컬 백업용 사용자 데이터
- `session.json` : 세션 지속성 데이터
- `.streamlit/secrets.toml` : Supabase API 키 설정
- `supabase_schema.sql` : 데이터베이스 스키마

## 실행 방법
1. Python 3.8+ 및 가상환경(.venv) 활성화
2. 필요한 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```
3. Supabase 설정 (선택사항)
   - `.streamlit/secrets.toml` 파일에 Supabase URL과 API 키 설정
   - `supabase_schema.sql`을 Supabase SQL 편집기에서 실행
4. 서버 실행
   ```bash
   streamlit run app.py
   ```
5. 브라우저에서 http://localhost:8501 접속

## 의존성
- streamlit
- pillow (이미지 처리)
- supabase (클라우드 데이터베이스)

## 기본 계정
- **관리자**: `admin` / `admin123` (첫 로그인 시 비밀번호 변경 필요)

## 배포
- Streamlit Cloud 배포 지원
- Supabase 클라우드 데이터베이스 연동
- 자세한 배포 가이드는 `DEPLOYMENT_GUIDE.md` 참조 