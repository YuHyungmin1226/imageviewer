# 🚀 Streamlit Cloud 배포 가이드

## 📋 사전 준비

### 1. Supabase 프로젝트 생성
1. [Supabase](https://supabase.com)에 가입
2. 새 프로젝트 생성
3. 프로젝트 URL과 API 키 확인

### 2. 데이터베이스 설정
1. Supabase 대시보드 → SQL 편집기
2. `supabase_schema.sql` 파일의 내용을 복사하여 실행
3. 테이블이 정상적으로 생성되었는지 확인

## 🔧 로컬 개발 설정

### 1. Supabase 패키지 설치
```bash
pip install supabase
```

### 2. 환경 변수 설정
`.streamlit/secrets.toml` 파일을 수정:
```toml
supabase_url = "your-actual-supabase-url"
supabase_key = "your-actual-supabase-anon-key"
```

### 3. 로컬 테스트
```bash
streamlit run app.py
```

## 🌐 Streamlit Cloud 배포

### 1. GitHub에 코드 업로드
```bash
git add .
git commit -m "Add Supabase integration"
git push origin main
```

### 2. Streamlit Cloud 설정
1. [Streamlit Cloud](https://share.streamlit.io)에 로그인
2. "New app" 클릭
3. GitHub 저장소 연결
4. 앱 설정:
   - **Main file path**: `personal_sns_app/app.py`
   - **Python version**: 3.9+

### 3. Secrets 설정
Streamlit Cloud 대시보드에서:
1. 앱 → Settings → Secrets
2. 다음 내용 추가:
```toml
supabase_url = "your-actual-supabase-url"
supabase_key = "your-actual-supabase-anon-key"
```

## ✅ 배포 확인

### 1. 기능 테스트
- [ ] 회원가입/로그인
- [ ] 게시글 작성
- [ ] 좋아요/댓글
- [ ] 공개/비공개 설정
- [ ] 파일 업로드 (로컬에서만)

### 2. 데이터베이스 확인
- Supabase 대시보드에서 데이터 확인
- 사용자, 게시글 테이블 정상 작동 확인

## 🔒 보안 설정

### 1. Supabase RLS 정책
- 기본 RLS 정책이 적용됨
- 필요시 추가 보안 정책 설정

### 2. API 키 보안
- `.streamlit/secrets.toml` 파일을 Git에 업로드하지 않음
- Streamlit Cloud Secrets에만 설정

## 🐛 문제 해결

### 1. Supabase 연결 오류
- URL과 API 키 확인
- 네트워크 연결 상태 확인

### 2. 데이터베이스 오류
- 테이블 스키마 확인
- RLS 정책 확인

### 3. 파일 업로드 오류
- Streamlit Cloud에서는 파일 업로드 기능 제한
- 로컬 개발 환경에서만 사용 가능

## 📞 지원

문제가 발생하면:
1. 로그 확인
2. Supabase 대시보드 확인
3. Streamlit Cloud 로그 확인 