# 🏠 개인/소규모 조직용 SNS 플랫폼

개인, 가정, 소규모 조직을 위한 **설치형 소셜 네트워크 서비스**입니다. Streamlit 기반으로 제작되어 간편하게 배포하고 사용할 수 있습니다.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 주요 기능

### 🔐 사용자 관리
- **회원가입/로그인** - 보안 세션 관리
- **관리자 패널** - 사용자 관리 및 삭제
- **비밀번호 변경** - 계정 보안 강화

### 📝 게시물 시스템
- **텍스트 게시물** 작성
- **공개/비공개** 설정
- **URL 자동 감지** 및 미리보기
- **YouTube 링크** 특별 지원

### 📎 파일 첨부
- (현재 버전에서는 파일 첨부/업로드/미리보기/다운로드 기능이 지원되지 않습니다.)

### 💬 댓글 시스템
- 게시물별 **댓글 작성/표시**
- **실시간 업데이트**
- 카드 내 통합 UI

### 🎨 UI/UX
- **다크모드/라이트모드** 자동 지원
- **반응형 디자인**
- **모던한 카드 레이아웃**
- **직관적인 인터페이스**

### 🌐 배포 옵션
- **로컬 파일 시스템** - 단독 실행
- **Supabase 연동** - 클라우드 백엔드
- **Streamlit Cloud** - 무료 웹 배포

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/YuHyungmin1226/HMYU.git
cd HMYU/personal_sns_app
```

### 2. 종속성 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## ⚙️ 설정

### 로컬 모드 (기본)
별도 설정 없이 바로 사용 가능합니다. 데이터는 로컬 JSON 파일에 저장됩니다.

### Supabase 클라우드 모드
1. [Supabase](https://supabase.com)에서 프로젝트 생성
2. `supabase_schema.sql` 실행하여 테이블 생성
3. Streamlit 설정 파일 생성:

**로컬 개발용** (`~/.streamlit/secrets.toml`):
```toml
supabase_url = "your-supabase-url"
supabase_key = "your-supabase-anon-key"
```

**Streamlit Cloud 배포용**:
앱 설정에서 Secrets 섹션에 추가:
```
supabase_url = "your-supabase-url"
supabase_key = "your-supabase-anon-key"
```

## 📁 프로젝트 구조

```
personal_sns_app/
├── app.py                      # 메인 애플리케이션
├── secure_auth.py              # 사용자 인증 시스템
├── session_manager.py          # 세션 관리
├── enhanced_url_utils.py       # URL 미리보기 생성
├── supabase_schema.sql         # 데이터베이스 스키마
├── requirements.txt            # Python 종속성
├── DEPLOYMENT_GUIDE.md         # 배포 가이드
└── uploads/                    # 업로드된 파일 (로컬 모드)
```

## 🛠️ 기술 스택

### 프론트엔드
- **Streamlit** - 웹 애플리케이션 프레임워크
- **HTML/CSS** - 커스텀 스타일링
- **JavaScript** - 동적 UI 요소

### 백엔드
- **Python 3.8+** - 핵심 로직
- **JSON** - 로컬 데이터 저장
- **Supabase** - 클라우드 PostgreSQL 데이터베이스

### 보안
- **SHA-256** - 비밀번호 해싱
- **UUID** - 고유 식별자
- **세션 관리** - 로그인 상태 유지
- **HTML Escape** - XSS 방지

### 파일 처리
- **Base64 인코딩** - 미디어 파일 임베딩
- **Pathlib** - 파일 경로 관리
- **MIME 타입** - 파일 형식 감지

## 👤 기본 계정

- **관리자 계정**: `admin` / `admin123`
- 첫 로그인 시 비밀번호 변경 권장

## 🔧 고급 설정

### 파일 업로드 제한
- 개별 파일 크기: Streamlit 기본 제한 (200MB)
- 지원 형식: `requirements.txt`에서 확인

### 보안 설정
- 세션 만료: 24시간
- 로그인 시도 제한: 5회 (15분 잠금)
- 비밀번호 정책: 자유 형식 (권장: 8자 이상)

### 성능 최적화
- 이미지 자동 리사이즈: 600x600px
- URL 미리보기 캐싱
- 세션 상태 최적화

## 🌐 배포 가이드

### Streamlit Cloud (권장)
1. GitHub에 코드 업로드
2. [share.streamlit.io](https://share.streamlit.io)에서 앱 생성
3. Supabase 설정을 Secrets에 추가
4. 배포 완료!

### 기타 플랫폼
- **Heroku**: `requirements.txt` 포함
- **Docker**: Streamlit 기반 컨테이너
- **VPS**: systemd 서비스로 실행

자세한 배포 방법은 `DEPLOYMENT_GUIDE.md`를 참고하세요.

## 🤝 사용 사례

### 개인/가정용
- **가족 소통** - 사진, 근황 공유
- **개인 블로그** - 일상 기록
- **취미 공유** - 관심사 중심 소통

### 소규모 조직
- **팀 내부 소통** - 업무 관련 공지
- **프로젝트 진행상황** 공유
- **지식 공유** - 문서, 링크 아카이브

### 교육 기관
- **학급 커뮤니티** - 학생-교사 소통
- **과제 제출** - 파일 첨부 기능 활용
- **공지사항** - 중요 정보 전달

## 📝 개발 로그

### v1.0.0 (현재)
- ✅ 기본 SNS 기능 완성
- ✅ 파일 첨부 시스템
- ✅ 댓글 시스템
- ✅ 다크모드 지원
- ✅ Supabase 연동
- ✅ URL 미리보기

### 향후 계획
- 🔄 알림 시스템
- 🔄 좋아요/반응 기능
- 🔄 태그 시스템
- 🔄 검색 기능

## ⚠️ 제한사항

- **Streamlit Cloud**: 파일 저장 제한 (재시작 시 삭제)
- **동시 사용자**: Streamlit 특성상 소규모 권장
- **실시간 업데이트**: 페이지 새로고침 필요
- **파일 첨부/업로드/미리보기/다운로드 기능 미지원**

## 🐛 문제 해결

### 앱이 실행되지 않을 때
1. Python 버전 확인 (3.8+)
2. 종속성 재설치: `pip install -r requirements.txt`
3. 포트 충돌 확인: `streamlit run app.py --server.port 8502`

### 파일 업로드 오류
1. 파일 크기 확인 (200MB 이하)
2. 지원 형식 확인
3. 브라우저 캐시 삭제 후 재시도

### Supabase 연결 오류
1. URL/Key 정확성 확인
2. 네트워크 연결 상태 확인
3. 로컬 모드로 대체 실행

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 🙋‍♂️ 지원

문제가 있거나 기능 요청이 있으시면 GitHub Issues를 통해 연락주세요.

---

**💡 Tip**: 소규모 조직이나 가정에서 사용하기에 최적화된 SNS입니다. 복잡한 설정 없이 바로 시작하세요! 