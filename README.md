# ImageViewer

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**ImageViewer**는 Python과 PySide6(Qt)로 만든 가볍고 미니멀한 이미지 뷰어입니다. [MinimalPlayer](https://github.com/YuHyungmin1226/MinimalPlayer)와 동일한 UI 형태 — 테두리 없는(frameless) 창, 커스텀 다크 타이틀바, 하단 컨트롤바, 전체 화면 자동 숨김 — 를 따릅니다.

## ✨ 주요 기능

### 🖼️ 이미지 지원
- **지원 형식**: JPG, JPEG, PNG, GIF, BMP, WebP, TIFF, TIF
- **고품질 렌더링**: LANCZOS 리샘플링으로 창 크기에 맞춰 선명하게 표시
- **폴더 탐색**: 이미지를 열면 같은 폴더의 다른 이미지를 파일명 자연 정렬(`img2` → `img10`) 순서로 탐색

### 🎨 미니멀 다크 UI (MinimalPlayer 스타일)
- **프레임리스 창**: OS 기본 창틀 대신 커스텀 다크 타이틀바(`-`/`x` 버튼)와 하단 컨트롤바
- **드래그로 창 이동**: 타이틀바나 이미지 영역을 클릭한 채로 드래그하면 창이 이동
- **가장자리 드래그로 크기 조절**: 창 테두리(상하좌우 및 모서리) 근처에서 커서가 리사이즈 모양으로 바뀌며, 클릭한 채로 드래그하면 창 크기가 조절됨 (최소 크기 이하로는 줄어들지 않음)
- **전체 화면 자동 숨김**: 전체 화면에서 마우스를 3초간 움직이지 않으면 타이틀/컨트롤 바가 부드럽게 페이드아웃되고, 움직이면 다시 페이드인
- **더블클릭 / Enter**: 이미지 영역 더블클릭 또는 `Enter` 키로 전체 화면 전환

### 🎮 조작
- **하단 버튼**: `Open`(파일 열기), `|<`/`>|`(이전/다음), `Delete`(현재 이미지 삭제)
- **드래그 앤 드롭**: Qt 네이티브 드래그 앤 드롭으로 이미지 파일을 창에 끌어다 놓기 (빌드된 실행 파일에서도 동일하게 동작)
- **우클릭 메뉴**: Open, Delete, Clear Cache, Memory Info, (Windows) Set as Default Image Viewer, Debug Info, Exit

### 💾 메모리 관리
- **비동기 로딩**: `QThreadPool` 백그라운드 스레드에서 이미지를 로드·리사이즈해 UI가 멈추지 않음
- **2단계 캐시**: 원본 디코딩 캐시(개수+메모리 제한)와 창 크기별 리사이즈 캐시를 분리 운용
- **요청 취소**: 이미지를 빠르게 넘기면 오래된 로드 결과는 폐기되고 최신 이미지만 반영

### 🔗 파일 연결 (Windows)
- **기본 프로그램 등록**: 우클릭 메뉴 → `Set as Default Image Viewer`
- **권한 불필요**: `HKEY_CURRENT_USER`에만 기록하므로 관리자 권한 없이 동작
- Windows 정책상 등록 후에는 설정 앱의 '기본 앱'에서 사용자가 직접 선택해야 적용됩니다.

## 🚀 설치 및 실행

```bash
git clone https://github.com/YuHyungmin1226/imageviewer.git
cd imageviewer

python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt

python main.py
# 특정 이미지로 시작
python main.py "path/to/image.jpg"
```

## ⌨️ 단축키

| 단축키 | 기능 |
|--------|------|
| `Ctrl+O` (macOS: `Cmd+O`) | 이미지 파일 열기 |
| `←` / `→` | 이전 / 다음 이미지 |
| `Enter` / 이미지 영역 더블클릭 | 전체 화면 전환 |
| `Space` / `Esc` | 프로그램 종료 |
| `Ctrl+R` (macOS: `Cmd+R`) | 캐시 정리 |
| `Ctrl+M` (macOS: `Cmd+M`) | 메모리 정보 표시 |
| `Delete` / `Backspace` | 현재 이미지 파일 삭제 (확인 후 진행, 되돌릴 수 없음) |

> macOS에서는 Qt가 `Ctrl` 표기를 자동으로 `Cmd` 키에 매핑하므로 별도 처리가 필요 없습니다.

## 🛠 빌드

```bash
python build.py
```

Windows에서는 단일 실행 파일(`dist/ImageViewer.exe`), macOS에서는 `.app` 번들(`dist/ImageViewer.app`)이 생성됩니다.

## 📦 프로젝트 구조

```
constants.py           앱 이름, 확장자, 캐시 크기 등 상수
utils.py                파일 정렬/시그니처/필터링 유틸리티
image_cache.py           원본 이미지 LRU 캐시
file_association.py      Windows 파일 연결 등록 (레지스트리)
image_viewer_window.py   메인 창 UI 및 이미지 로딩/탐색 로직
main.py                  진입점, macOS 파일 열기 이벤트 라우팅
build.py                 PyInstaller 빌드 스크립트
```

## 🔧 알려진 제약

- **GIF 애니메이션**: 첫 프레임만 정지 이미지로 표시합니다 (원본 tkinter 버전과 동일한 동작).

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

**개발자**: [YuHyungmin1226](https://github.com/YuHyungmin1226)
