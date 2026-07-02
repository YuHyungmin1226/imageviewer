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
- **드래그 앤 드롭**: 이미지 파일을 창에 드래그하여 열기 (`tkinterdnd2` 설치 시 활성화)

### 💾 메모리 관리
- **스마트 캐싱**: 최대 15개 이미지 캐시 (200MB 제한)
- **리사이즈 캐싱**: 창 크기별 리사이즈 결과 캐시 (최대 20개)
- **자동 메모리 정리**: 사용하지 않는 이미지 자동 제거
- **수동 캐시 정리**: `Ctrl+R`로 즉시 캐시 정리

### 🔗 파일 연결 (Windows)
- **기본 프로그램 등록**: 이미지 파일 형식을 ImageViewer와 연결
- **권한 불필요**: 현재 사용자(`HKEY_CURRENT_USER`)에만 등록하므로 관리자 권한 없이 동작
- **즉시 반영**: 등록/해제 후 탐색기에 변경 사항을 자동 통지 (`SHChangeNotify`)
- **일괄 등록/해제**: 모든 지원 형식 한 번에 처리
- **상태 확인**: 현재 등록 상태 실시간 확인

### ⚡ 성능
- **비동기 로딩**: 백그라운드 스레드에서 이미지를 로드·리사이즈하므로, 대용량 이미지 파일을 열 때도 UI가 멈추지 않습니다. 로딩 중에는 "로딩 중..." 안내가 표시됩니다.
- **요청 취소**: 이미지를 빠르게 넘길 경우 이전 로드 결과는 폐기되고 최신 이미지만 표시됩니다.
- **응답성 향상**: 이미지 로딩 중에도 사용자는 프로그램을 자유롭게 조작할 수 있습니다.

### 🔍 디버그 및 모니터링
- **메모리 정보**: `Ctrl+M`으로 실시간 메모리 상태 확인
- **디버그 정보**: 시스템 정보 및 캐시 상태 표시
- **로그 기능**: 디버그 로그는 기본적으로 비활성화되어 있어 별도의 로그 파일을 생성하지 않습니다.

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
pyinstaller --onefile --noconsole --name=ImageViewer --windowed imgViewer.py
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
| `Delete` / `Backspace` | 현재 이미지 파일 삭제 (확인 후 진행, 되돌릴 수 없음) |

> macOS 노트북 키보드에는 순방향 `Delete` 키가 없는 경우가 많아 `Backspace`(⌫)로도 삭제할 수 있습니다.

### Windows 파일 연결 설정

> 현재 사용자 영역(`HKEY_CURRENT_USER`)에만 등록하므로 **관리자 권한이 필요 없습니다.**

1. **기본 프로그램 등록**
   - `Tools > Register as Default Image Viewer` 실행
   - 모든 지원 형식이 자동으로 등록되고, 탐색기에 즉시 반영됨

2. **등록 해제**
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

### 선택 패키지 (드래그 앤 드롭)
```
tkinterdnd2>=0.3.0
```
> 미설치 시 드래그 앤 드롭만 비활성화되며, 그 외 기능은 정상 동작합니다.

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
pyinstaller --onefile --noconsole --name=ImageViewer --windowed imgViewer.py
```

### macOS 앱 번들 빌드
```bash
# 자동 빌드 (build/dist 폴더 정리 및 .app 생성까지 처리)
python build_imgviewer_mac.py

# 또는 수동 빌드
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
1. **다른 프로그램**: 다른 프로그램이 이미 기본 앱으로 등록되어 있는지 확인
2. **Windows 설정**: Windows 설정 > 앱 > 기본 앱에서 확인 및 변경
3. **재로그인**: 변경이 즉시 반영되지 않으면 탐색기를 재시작하거나 다시 로그인

> 파일 연결은 `HKEY_CURRENT_USER`에만 기록하므로 관리자 권한이나 UAC 승인이 필요하지 않습니다.

### macOS 특정 문제

#### 전체 화면에서 메뉴 바가 계속 보이는 경우
- macOS는 애플리케이션마다 별도의 메뉴 바가 아니라 화면 상단에 하나의 전역 메뉴 바를 사용합니다. Tk/Python 버전에 따라 전체 화면 전환 시 메뉴 바가 자동으로 숨겨지지 않을 수 있으며, 이는 알려진 Tkinter 제약사항으로 프로그램 동작에는 영향이 없습니다.

#### `Delete` 키로 이미지가 삭제되지 않는 경우
- 대부분의 맥북 키보드에는 순방향 삭제 키가 없습니다. `Backspace`(⌫) 키를 사용하면 동일하게 현재 이미지를 삭제할 수 있습니다.

## 📊 성능 최적화

### 캐시 설정 조정
```python
# imgViewer.py에서 캐시 설정 변경
self.image_cache = ImageCache(max_size=20, max_memory_mb=300)  # 더 큰 캐시
```

### 메모리 사용량 모니터링
- `Ctrl+M`으로 실시간 메모리 상태 확인
- `Help > Debug Info`로 캐시/메모리 상세 정보 확인

### 타입 힌트 검증
```bash
# mypy 설치 (선택사항)
pip install mypy

# 타입 검사 실행
mypy imgViewer.py
```

## 🔒 보안 정보

### Windows 레지스트리 수정
- **범위**: `HKEY_CURRENT_USER\Software\Classes`에만 기록 (시스템 전역 설정 미변경)
- **권한**: 관리자 권한 불필요 — 현재 사용자에 한해 적용
- **복원**: `Unregister as Default Image Viewer`로 언제든 등록 해제 가능

### 로그 파일
- 디버그 로그는 기본적으로 **비활성화**되어 있어 로그 파일을 생성하지 않습니다.
- 따라서 디스크에 사용 기록이나 개인정보가 남지 않습니다.

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