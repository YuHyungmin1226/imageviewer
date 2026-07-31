#!/usr/bin/env python3
"""ImageViewer를 독립 실행형 파일로 빌드하는 스크립트.

Windows에서는 단일 실행 파일(.exe), macOS에서는 .app 번들을 생성한다.
"""

import sys
import shutil
from pathlib import Path

import PyInstaller.__main__

APP_NAME = "ImageViewer"
ENTRY_POINT = "main.py"
BUNDLE_IDENTIFIER = "com.yuhyungmin.imageviewer"

IS_WINDOWS = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"


def print_with_color(message: str, color_code: int = 36) -> None:
    print(f"\033[{color_code}m{message}\033[0m")


def build() -> bool:
    script_dir = Path(__file__).parent
    dist_dir = script_dir / "dist"
    build_dir = script_dir / "build"

    print_with_color(f"=== {APP_NAME} 빌드 시작 ({sys.platform}) ===", 33)

    try:
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        if build_dir.exists():
            shutil.rmtree(build_dir)
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
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        # Pillow의 PIL.ImageQt는 설치된 Qt 바인딩을 런타임에 탐지하며, 이 조건부 임포트를
        # PyInstaller가 정적 분석만으로 못 찾는 경우가 있어 명시적으로 포함시킨다.
        "--hidden-import=PIL.ImageQt",
    ]

    if IS_WINDOWS:
        params.append("--onefile")
    elif IS_MAC:
        params.append(f"--osx-bundle-identifier={BUNDLE_IDENTIFIER}")

    try:
        PyInstaller.__main__.run(params)
    except SystemExit as e:
        if e.code:
            print_with_color("=== 빌드 실패 ===", 31)
            return False

    if IS_MAC:
        out = dist_dir / f"{APP_NAME}.app"
    elif IS_WINDOWS:
        out = dist_dir / f"{APP_NAME}.exe"
    else:
        out = dist_dir / APP_NAME

    if not out.exists():
        print_with_color(f"오류: 결과물이 생성되지 않았습니다: {out}", 31)
        return False

    print_with_color("=== 빌드 성공! ===", 32)
    print(f"결과물 경로: {out}")
    return True


if __name__ == "__main__":
    if not build():
        sys.exit(1)
