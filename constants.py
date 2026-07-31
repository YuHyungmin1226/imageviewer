APP_NAME = "ImageViewer"
APP_DISPLAY_NAME = "Minimal Image Viewer"
ORG_NAME = "ImageViewer"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}

DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700
INITIAL_WINDOW_SCREEN_RATIO = 0.75  # 초기 창 크기를 화면 크기의 비율로 계산
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 300

MAX_CACHE_SIZE = 15          # 원본 이미지 캐시 최대 개수
MAX_MEMORY_MB = 200          # 원본 이미지 캐시 최대 메모리(MB)
MAX_RESIZE_CACHE_SIZE = 20   # 창 크기별 리사이즈 결과 캐시 최대 개수

RESIZE_DEBOUNCE_MS = 150     # 창 크기 변경 시 리사이즈를 재실행하기까지의 디바운스 간격
CONTROL_FADE_DURATION_MS = 210
FULLSCREEN_IDLE_HIDE_MS = 3000

FRAME_RESIZE_MARGIN = 8      # 프레임리스 창 가장자리에서 크기 조절을 감지하는 폭(px)
