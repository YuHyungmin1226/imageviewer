from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any, Dict, Optional

from PIL import Image


class ImageCache:
    """원본(디코딩된) 이미지를 위한 스레드 세이프 LRU 캐시.

    개수 제한과 메모리 제한을 동시에 적용해, 큰 이미지 몇 장으로 캐시가
    과도한 메모리를 차지하는 것을 막는다.
    """

    def __init__(self, max_size: int = 10, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self._cache: "OrderedDict[str, Image.Image]" = OrderedDict()
        self._memory_usage = 0
        self._lock = threading.Lock()

    @staticmethod
    def _estimate_memory_usage(image: Image.Image) -> int:
        width, height = image.size
        bytes_per_pixel = {"RGB": 3, "RGBA": 4, "L": 1}.get(image.mode, 4)
        return width * height * bytes_per_pixel

    def get(self, key: str) -> Optional[Image.Image]:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            return None

    def put(self, key: str, image: Image.Image) -> None:
        with self._lock:
            if key in self._cache:
                self._memory_usage -= self._estimate_memory_usage(self._cache.pop(key))

            new_memory = self._estimate_memory_usage(image)
            while self._cache and (
                len(self._cache) >= self.max_size
                or (self._memory_usage + new_memory) > self.max_memory_mb * 1024 * 1024
            ):
                _, oldest_image = self._cache.popitem(last=False)
                self._memory_usage -= self._estimate_memory_usage(oldest_image)

            self._cache[key] = image
            self._memory_usage += new_memory

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._memory_usage = 0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "memory_usage_mb": self._memory_usage / 1024 / 1024,
                "max_memory_mb": self.max_memory_mb,
            }
