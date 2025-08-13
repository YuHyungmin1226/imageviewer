# ImageViewer

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Type Hints](https://img.shields.io/badge/Type%20Hints-Enabled-blue.svg)

**ImageViewer**는 Python과 Tkinter로 개발된 강력하고 가벼운 이미지 뷰어 애플리케이션입니다. 다양한 이미지 형식을 지원하며, 직관적인 인터페이스와 고급 기능을 제공합니다. 최신 코드 최적화로 타입 힌트 지원과 향상된 성능을 제공합니다.

## ✨ 주요 기능

### 🖼️ 이미지 지원
- **지원 형식**: JPG, JPEG, PNG, GIF, BMP, WebP, TIFF, TIF
- **고품질 렌더링**: LANCZOS 리샘플링으로 선명한 이미지 표시
- **자동 리사이즈**: 창 크기에 맞춰 이미지 자동 조정

### 🎮 사용자 인터페이스
- **직관적인 UI**: 깔끔하고 현대적인 인터페이스
- **전체 화면 모드**: `Enter` 키로 전체 화면 전환
- **키보드 단축키**: 빠른 이미지 탐색 및 조작
- **드래그 앤 드롭**: 이미지 파일을 창에 드래그하여 열기

### 💾 메모리 관리
- **스마트 캐싱**: 최대 15개 이미지 캐시 (200MB 제한)
- **리사이즈 캐싱**: 창 크기별 리사이즈 결과 캐시 (최대 20개)
- **자동 메모리 정리**: 사용하지 않는 이미지 자동 제거
- **수동 캐시 정리**: `Ctrl+R`로 즉시 캐시 정리

### 🔗 파일 연결 (Windows)
- **기본 프로그램 등록**: 이미지 파일 형식을 ImageViewer와 연결
- **관리자 권한 지원**: 안전한 Windows 레지스트리 수정
- **일괄 등록/해제**: 모든 지원 형식 한 번에 처리
- **상태 확인**: 현재 등록 상태 실시간 확인

### ⚡ 성능
- **비동기 로딩**: 백그라운드 스레드를 사용하여 이미지를 로드하므로, 대용량 이미지 파일을 열 때도 UI가 멈추지 않습니다.
- **응답성 향상**: 이미지 로딩 중에도 사용자는 프로그램을 자유롭게 조작할 수 있습니다.

### 🔍 디버그 및 모니터링
- **메모리 정보**: `Ctrl+M`으로 실시간 메모리 상태 확인
- **디버그 정보**: 시스템 정보 및 캐시 상태 표시
- **로그 기능**: 디버그 로그 기능은 사용자 요청에 따라 비활성화됨

### 🚀 코드 품질
- **타입 힌트**: 모든 함수와 메서드에 타입 힌트 적용
- **상수 정의**: 매직 넘버 제거 및 상수화
- **성능 최적화**: 메모리 사용량 및 캐시 시스템 개선
- **코드 가독성**: 일관된 코딩 스타일 적용

## 🚀 설치 및 실행

### Python으로 실행
```bash
# 저장소 클론
git clone https://github.com/YuHyungmin1226/imageviewer.git
cd imageviewer

# 의존성 설치
pip install -r requirements.txt

# 실행
python imgViewer.py
```

### 실행 파일로 빌드 (Windows)
```bash
# 빌드 스크립트 실행
python build_imgviewer.py

# 또는 수동 빌드
pyinstaller --onefile --noconsole --name=ImageViewer --windowed --uac-admin imgViewer.py
```

## 🎮 사용법

### 기본 실행
```bash
# 빈 창으로 시작
python imgViewer.py

# 특정 이미지 파일 열기
python imgViewer.py "path/to/image.jpg"
```

### 단축키

| 단축키 | 기능 |
|--------|------|
| `Ctrl+O` | 이미지 파일 열기 |
| `←/→` | 이전/다음 이미지 |
| `Enter` | 전체 화면 전환 |
| `Space/ESC` | 프로그램 종료 |
| `Ctrl+R` | 캐시 정리 |
| `Ctrl+M` | 메모리 정보 표시 |

### Windows 파일 연결 설정

1. **관리자 권한으로 실행**
   - ImageViewer.exe를 우클릭
   - "관리자 권한으로 실행" 선택

2. **기본 프로그램 등록**
   - `Tools > Register as Default Image Viewer` 실행
   - 모든 지원 형식이 자동으로 등록됨

3. **등록 해제**
   - `Tools > Unregister as Default Image Viewer` 실행

## 🛠️ 시스템 요구사항

### 최소 요구사항
- **OS**: Windows 10/11, macOS 10.14+, Linux
- **Python**: 3.8 이상 (타입 힌트 지원)
- **메모리**: 512MB RAM
- **저장공간**: 50MB 이상

### 권장 사항
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.10 이상
- **메모리**: 2GB RAM 이상
- **저장공간**: 100MB 이상

## 📦 의존성

### 필수 패키지
```
Pillow>=9.0.0
```

### 개발 패키지 (빌드용)
```
pyinstaller>=5.0.0
```

### 타입 힌트 지원
- **Python 3.5+**: `typing` 모듈 기본 제공
- **개발 도구**: `mypy>=1.0.0` (선택사항)

## 🔧 빌드

### Windows 실행 파일 빌드
```bash
# 자동 빌드
python build_imgviewer.py

# 수동 빌드
pyinstaller --onefile --noconsole --name=ImageViewer --windowed --uac-admin imgViewer.py
```

### macOS 앱 번들 빌드
```bash
pyinstaller --windowed --name=ImageViewer imgViewer.py
```

### Linux 실행 파일 빌드
```bash
pyinstaller --onefile --name=ImageViewer imgViewer.py
```

## 🐛 문제 해결

### 일반적인 문제

#### 실행이 안 되는 경우
1. **Python 버전 확인**: Python 3.8 이상 필요
2. **의존성 설치**: `pip install -r requirements.txt` 실행
3. **권한 확인**: 파일 실행 권한 확인

#### 이미지가 안 열리는 경우
1. **파일 경로**: 한글이나 특수문자가 포함된 경로 확인
2. **파일 권한**: 파일 읽기 권한 확인
3. **파일 손상**: 이미지 파일이 손상되지 않았는지 확인

#### 메모리 부족 오류
1. **캐시 정리**: `Ctrl+R`로 캐시 정리
2. **다른 프로그램 종료**: 메모리 사용량이 많은 프로그램 종료
3. **재시작**: 프로그램 재시작

### Windows 특정 문제

#### 파일 연결이 안 되는 경우
1. **관리자 권한**: 관리자 권한으로 실행했는지 확인
2. **레지스트리 권한**: 레지스트리 쓰기 권한 확인
3. **다른 프로그램**: 다른 프로그램이 이미 등록되어 있는지 확인
4. **Windows 설정**: Windows 설정 > 앱 > 기본 앱에서 확인

#### UAC 권한 요청
- 파일 연결 기능 사용 시 Windows UAC(사용자 계정 컨트롤) 권한 요청이 표시됩니다
- 이는 정상적인 동작이며, 안전한 레지스트리 수정을 위한 것입니다

## 📊 성능 최적화

### 캐시 설정 조정
```python
# imgViewer.py에서 캐시 설정 변경
self.image_cache = ImageCache(max_size=20, max_memory_mb=300)  # 더 큰 캐시
```

### 메모리 사용량 모니터링
- `Ctrl+M`으로 실시간 메모리 상태 확인
- 로그 파일에서 메모리 사용량 추적

### 타입 힌트 검증
```bash
# mypy 설치 (선택사항)
pip install mypy

# 타입 검사 실행
mypy imgViewer.py
```

## 🔒 보안 정보

### Windows 레지스트리 수정
- **안전성**: 레지스트리 수정은 안전하게 설계됨
- **백업**: 기존 설정을 덮어쓰지 않음
- **권한**: 관리자 권한이 필요한 안전한 작업

### 로그 파일
- **위치**: `~/Desktop/imageviewer_debug.log`
- **내용**: 디버그 정보, 오류 메시지, 성능 데이터
- **개인정보**: 민감한 개인정보는 기록되지 않음

## 🤝 기여하기

1. **Fork** 저장소
2. **Feature branch** 생성 (`git checkout -b feature/AmazingFeature`)
3. **Commit** 변경사항 (`git commit -m 'Add some AmazingFeature'`)
4. **Push** 브랜치 (`git push origin feature/AmazingFeature`)
5. **Pull Request** 생성

### 개발 가이드라인
- **타입 힌트**: 모든 함수와 메서드에 타입 힌트 추가
- **상수 사용**: 매직 넘버 대신 상수 정의
- **에러 처리**: 적절한 예외 처리 구현
- **문서화**: 함수와 클래스에 docstring 추가

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

### 버그 리포트
문제가 발생하면 다음 정보와 함께 [Issues](https://github.com/YuHyungmin1226/imageviewer/issues)에 등록해주세요:
- 운영체제 및 버전
- Python 버전
- 오류 메시지
- 이미지 파일 형식
- 프로그램 실행 시 발생하는 오류 메시지

### 기능 요청
새로운 기능이나 개선사항은 [Issues](https://github.com/YuHyungmin1226/imageviewer/issues)에 등록해주세요.

## 🙏 감사의 말

- **Pillow**: 이미지 처리 라이브러리
- **Tkinter**: GUI 프레임워크
- **PyInstaller**: 실행 파일 빌드 도구
- **GitHub**: 프로젝트 호스팅

---

**ImageViewer**는 교육 목적으로 제작되었으며, 개인 및 상업적 용도로 자유롭게 사용할 수 있습니다.

**개발자**: [YuHyungmin1226](https://github.com/YuHyungmin1226) 