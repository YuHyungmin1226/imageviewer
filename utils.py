from __future__ import annotations

import os
import re
import sys
from typing import Any, List, Optional, Tuple

from constants import SUPPORTED_EXTENSIONS

_NATURAL_CHUNK_RE = re.compile(r"(\d+)")


def resource_path(relative_path: str) -> str:
    """개발 실행과 PyInstaller 번들 실행 모두에서 동작하는 리소스 경로를 반환.

    PyInstaller로 빌드하면 데이터 파일이 sys._MEIPASS 아래 임시 폴더에 풀리므로,
    개발 중 경로(이 파일 기준 상대 경로)와 분기해야 한다.
    """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def natural_sort_key(path: str) -> tuple:
    """파일명을 탐색기/Finder와 비슷한 자연 정렬 순서로 비교하기 위한 키.

    숫자 구간은 정수로 비교하므로 "img2 < img10"이 성립하고, 문자 구간은
    대소문자를 무시한다. 마지막에 원본 이름을 붙여 키가 같은 파일도 결정적인
    순서를 갖도록 한다.
    """
    name = os.path.basename(path).casefold()
    parts = _NATURAL_CHUNK_RE.split(name)
    key = [(0, int(part), "") if index % 2 else (1, 0, part) for index, part in enumerate(parts)]
    return (tuple(key), name)


def file_signature(path: str) -> Optional[Tuple[int, int]]:
    """파일의 mtime+size로 캐시 무효화 판단용 서명을 생성.

    캐시 키에 이 서명을 포함시키면, 외부에서 같은 경로의 파일이 교체/수정돼도
    자동으로 캐시 미스가 나 예전 내용을 계속 보여주는 문제를 막는다.
    """
    try:
        st = os.stat(path)
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def is_image_file(path: str) -> bool:
    """파일이 지원되는 이미지 형식인지 확인."""
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS


def get_image_files_from_directory(directory: str) -> List[str]:
    """디렉토리 안의 지원 이미지 파일 경로를 자연 정렬 순서로 반환."""
    try:
        entries = os.listdir(directory)
    except OSError:
        return []
    files = [
        os.path.join(directory, name)
        for name in entries
        if is_image_file(name) and os.path.isfile(os.path.join(directory, name))
    ]
    files.sort(key=natural_sort_key)
    return files


def get_current_image_index(images: List[str], file_path: str) -> int:
    """주어진 파일 경로가 목록에서 몇 번째인지 반환."""
    target = os.path.abspath(file_path)
    for index, image_path in enumerate(images):
        if os.path.abspath(image_path) == target:
            return index
    # 대소문자를 구분하지 않는 파일시스템(Windows, 기본 macOS)을 위한 재시도
    target_lower = target.lower()
    for index, image_path in enumerate(images):
        if os.path.abspath(image_path).lower() == target_lower:
            return index
    return 0
