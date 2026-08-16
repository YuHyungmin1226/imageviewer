#!/usr/bin/env python3
"""ImageViewer를 독립 실행형 파일로 빌드하는 스크립트.

Windows에서는 단일 실행 파일(.exe), macOS에서는 .app 번들을 생성한다.
빌드가 끝나면 결과물을 release/ 폴더로 복사하고 zip 배포판을 만든 뒤,
build/dist/.spec 등 빌드 과정에서 생긴 중간 산출물은 모두 정리한다.
"""

import os
import platform
import sys
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import PyInstaller.__main__

APP_NAME = "ImageViewer"
ENTRY_POINT = "main.py"
BUNDLE_IDENTIFIER = "com.yuhyungmin.imageviewer"
ICON_ICO = "assets/icon.ico"
ICON_ICNS = "assets/icon.icns"
SYSTEM_NAME = platform.system()

IS_WINDOWS = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"

SCRIPT_DIR = Path(__file__).parent
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"
RELEASE_DIR = SCRIPT_DIR / "release"


def print_with_color(message: str, color_code: int = 36) -> None:
    print(f"\033[{color_code}m{message}\033[0m")


def clean_build_dirs() -> None:
    """빌드 중간 산출물(build/, dist/, __pycache__, .spec)을 정리한다."""
    for directory in (BUILD_DIR, DIST_DIR, SCRIPT_DIR / "__pycache__"):
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)
    for spec_file in SCRIPT_DIR.glob("*.spec"):
        spec_file.unlink(missing_ok=True)


def build() -> bool:
    print_with_color(f"=== {APP_NAME} 빌드 시작 ({sys.platform}) ===", 33)

    try:
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
    except OSError as e:
        print_with_color(f"이전 빌드 파일을 삭제할 수 없습니다: {e}", 31)
        print_with_color(f"{APP_NAME}가 실행 중이면 종료 후 다시 시도하세요.", 31)
        return False

    params = [
        ENTRY_POINT,
        f"--name={APP_NAME}",
        "--windowed",   # 콘솔 숨김 / macOS에서는 .app 번들 생성
        "--noconfirm",
        "--clean",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        # Pillow의 PIL.ImageQt는 설치된 Qt 바인딩을 런타임에 탐지하며, 이 조건부 임포트를
        # PyInstaller가 정적 분석만으로 못 찾는 경우가 있어 명시적으로 포함시킨다.
        "--hidden-import=PIL.ImageQt",
        # QApplication.setWindowIcon()이 런타임에 읽도록 아이콘 PNG를 데이터로 동봉
        # (--icon은 실행 파일 메타데이터에만 반영될 뿐 앱에서 로드 가능한 파일이 아님).
        f"--add-data=assets/icon.png{os.pathsep}assets",
    ]

    if IS_WINDOWS:
        params.append("--onefile")
        params.append(f"--icon={ICON_ICO}")
    elif IS_MAC:
        params.append(f"--osx-bundle-identifier={BUNDLE_IDENTIFIER}")
        params.append(f"--icon={ICON_ICNS}")

    try:
        PyInstaller.__main__.run(params)
    except SystemExit as e:
        if e.code:
            print_with_color("=== 빌드 실패 ===", 31)
            return False

    if not get_build_artifact():
        print_with_color("오류: 결과물이 생성되지 않았습니다.", 31)
        return False

    print_with_color("=== 빌드 성공! ===", 32)
    return True


def get_build_artifact():
    """PyInstaller가 생성한 배포 산출물을 반환한다."""
    if IS_MAC:
        artifact = DIST_DIR / f"{APP_NAME}.app"
    elif IS_WINDOWS:
        artifact = DIST_DIR / f"{APP_NAME}.exe"
    else:
        artifact = DIST_DIR / APP_NAME
    return artifact if artifact.exists() else None


def get_path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file() and not p.is_symlink())


def copy_to_release():
    """빌드된 파일을 release 디렉토리로 복사한다."""
    artifact = get_build_artifact()
    if not artifact:
        print_with_color("빌드된 실행 파일을 찾을 수 없습니다.", 31)
        return None

    RELEASE_DIR.mkdir(exist_ok=True)
    release_artifact = RELEASE_DIR / artifact.name
    if release_artifact.exists():
        print(f"기존 산출물 교체: {release_artifact}")
        if release_artifact.is_dir():
            shutil.rmtree(release_artifact)
        else:
            release_artifact.unlink()

    print("release 디렉토리로 복사 중...")
    if artifact.is_dir():
        shutil.copytree(str(artifact), str(release_artifact), symlinks=True)
    else:
        shutil.copy2(str(artifact), str(release_artifact))

    file_size = get_path_size(release_artifact) / (1024 * 1024)
    print(f"복사 완료! 파일 크기: {file_size:.1f} MB")
    return release_artifact


def sync_release_docs() -> None:
    RELEASE_DIR.mkdir(exist_ok=True)
    for file_name in ("README.md", "requirements.txt"):
        source = SCRIPT_DIR / file_name
        if source.exists():
            shutil.copy2(source, RELEASE_DIR / file_name)


def create_zip_package(release_artifact: Path):
    """배포용 ZIP 패키지를 생성한다."""
    print("ZIP 패키지 생성 중...")

    version = datetime.now().strftime("%Y.%m.%d")
    platform_label = {"Windows": "Windows", "Darwin": "macOS", "Linux": "Linux"}.get(
        SYSTEM_NAME, SYSTEM_NAME or "Unknown"
    )
    zip_path = RELEASE_DIR / f"{APP_NAME}_v{version}_{platform_label}.zip"

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            if release_artifact.is_dir():
                for file_path in release_artifact.rglob("*"):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(RELEASE_DIR))
            else:
                zipf.write(release_artifact, release_artifact.name)

            for file_name in ("README.md", "requirements.txt"):
                source = SCRIPT_DIR / file_name
                if source.exists():
                    zipf.write(source, file_name)

        zip_size = zip_path.stat().st_size / (1024 * 1024)
        print(f"ZIP 패키지 생성 완료: {zip_path} ({zip_size:.1f} MB)")
        return zip_path
    except Exception as e:
        print_with_color(f"ZIP 패키지 생성 실패: {e}", 31)
        return None


def main() -> bool:
    if not build():
        clean_build_dirs()
        return False

    release_artifact = copy_to_release()
    if not release_artifact:
        clean_build_dirs()
        return False

    sync_release_docs()
    zip_path = create_zip_package(release_artifact)

    print("최종 정리 중 (빌드 임시 파일 제거)...")
    clean_build_dirs()

    print_with_color("=== 빌드 프로세스 완료! ===", 32)
    print(f"결과물: {release_artifact}")
    if zip_path:
        print(f"배포 패키지: {zip_path}")

    return True


if __name__ == "__main__":
    if not main():
        sys.exit(1)
