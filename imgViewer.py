import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import platform
from tkinter import filedialog, messagebox
from PIL import UnidentifiedImageError
import time
import gc
import weakref
from collections import OrderedDict
import threading
import queue
import re
from typing import Optional, List, Dict, Tuple, Any

# 드래그 앤 드롭 지원 (선택적 의존성)
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# Windows 레지스트리 관련 import
if platform.system() == "Windows":
    import winreg
    import ctypes
    import subprocess

# 상수 정의
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif")
DEFAULT_WINDOW_SIZE = "800x600"
MIN_WINDOW_SIZE = (400, 300)
DEFAULT_CANVAS_SIZE = (640, 480)
MAX_CACHE_SIZE = 15
MAX_MEMORY_MB = 200
MAX_RESIZE_CACHE_SIZE = 20
RESULT_POLL_INTERVAL_MS = 30  # 워커 스레드 결과를 메인 스레드에서 폴링하는 주기

# OS 타입 확인
is_windows = platform.system() == "Windows"
is_macos = platform.system() == "Darwin"

# 디버깅용 로그 파일 (비활성화됨)
DEBUG_LOG = None

def log_debug(message: str) -> None:
    """디버그 메시지를 파일에 기록 (비활성화됨)"""
    # 로그 기능이 비활성화되어 있음
    pass

def natural_sort_key(path: str) -> List[Any]:
    """파일명을 자연 정렬(예: img2 < img10) 순서로 정렬하기 위한 키 생성"""
    name = os.path.basename(path).lower()
    return [int(chunk) if chunk.isdigit() else chunk
            for chunk in re.split(r"(\d+)", name)]

# 시작 시 로그 (비활성화됨)
# log_debug("===== 프로그램 시작 =====")
# log_debug(f"OS: {platform.system()}")
# log_debug(f"Python 버전: {sys.version}")
# log_debug(f"명령줄 인수: {sys.argv}")
# log_debug(f"현재 작업 디렉토리: {os.getcwd()}")

# macOS에서 앱 번들 내 위치 확인 (비활성화됨)
# if hasattr(sys, 'frozen') and getattr(sys, 'frozen'):
#     log_debug(f"앱 번들 경로: {sys.executable}")
#     log_debug(f"앱 리소스 경로: {getattr(sys, '_MEIPASS', 'Not available')}")

class WindowsFileAssociation:
    """Windows 파일 연결 관리 클래스"""
    
    def __init__(self):
        self.app_name = "ImageViewer"
        self.app_description = "HM Utils Image Viewer"
        self.supported_extensions = list(SUPPORTED_EXTENSIONS)
        
    def get_executable_path(self) -> str:
        """실행 파일 경로 반환"""
        if hasattr(sys, 'frozen') and getattr(sys, 'frozen'):
            # PyInstaller로 빌드된 실행 파일
            return sys.executable
        else:
            # Python 스크립트
            return sys.executable + ' "' + os.path.abspath(__file__) + '"'
    
    def register_file_association(self, extension: str) -> bool:
        """특정 확장자를 ImageViewer와 연결"""
        try:
            # 확장자 키 생성
            ext_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{extension}")
            
            # 기본값 설정
            winreg.SetValue(ext_key, "", winreg.REG_SZ, f"{self.app_name}{extension}")
            
            # 확장자별 키 생성
            app_ext_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{self.app_name}{extension}")
            winreg.SetValue(app_ext_key, "", winreg.REG_SZ, f"{self.app_description} - {extension.upper()} 파일")
            
            # shell 키 생성
            shell_key = winreg.CreateKey(app_ext_key, "shell")
            open_key = winreg.CreateKey(shell_key, "open")
            command_key = winreg.CreateKey(open_key, "command")
            
            # 명령어 설정
            exe_path = self.get_executable_path()
            command = f'"{exe_path}" "%1"'
            winreg.SetValue(command_key, "", winreg.REG_SZ, command)
            
            # 키 닫기
            winreg.CloseKey(command_key)
            winreg.CloseKey(open_key)
            winreg.CloseKey(shell_key)
            winreg.CloseKey(app_ext_key)
            winreg.CloseKey(ext_key)
            
            log_debug(f"파일 연결 등록 성공: {extension}")
            return True
            
        except Exception as e:
            log_debug(f"파일 연결 등록 실패: {extension} - {str(e)}")
            return False
    
    def unregister_file_association(self, extension: str) -> bool:
        """특정 확장자의 연결 해제"""
        try:
            # 확장자 키 삭제
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{extension}")
            except FileNotFoundError:
                pass
            
            # 앱별 확장자 키 삭제
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{self.app_name}{extension}")
            except FileNotFoundError:
                pass
            
            log_debug(f"파일 연결 해제 성공: {extension}")
            return True
            
        except Exception as e:
            log_debug(f"파일 연결 해제 실패: {extension} - {str(e)}")
            return False
    
    def notify_shell_change(self) -> None:
        """탐색기에 파일 연결 변경을 알려 아이콘/연결을 즉시 갱신"""
        try:
            # SHCNE_ASSOCCHANGED = 0x08000000, SHCNF_IDLIST = 0x0000
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            log_debug("탐색기 연결 변경 알림 전송")
        except Exception as e:
            log_debug(f"탐색기 알림 실패: {str(e)}")

    def register_all_extensions(self) -> int:
        """모든 지원 확장자를 등록"""
        success_count = 0
        for ext in self.supported_extensions:
            if self.register_file_association(ext):
                success_count += 1

        log_debug(f"전체 파일 연결 등록 완료: {success_count}/{len(self.supported_extensions)}")
        self.notify_shell_change()
        return success_count

    def unregister_all_extensions(self) -> int:
        """모든 지원 확장자의 연결 해제"""
        success_count = 0
        for ext in self.supported_extensions:
            if self.unregister_file_association(ext):
                success_count += 1

        log_debug(f"전체 파일 연결 해제 완료: {success_count}/{len(self.supported_extensions)}")
        self.notify_shell_change()
        return success_count
    
    def is_registered(self, extension: str) -> bool:
        """특정 확장자가 등록되어 있는지 확인"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{extension}")
            value, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            return value == f"{self.app_name}{extension}"
        except:
            return False
    
    def get_registration_status(self) -> Dict[str, bool]:
        """모든 확장자의 등록 상태 확인"""
        status = {}
        for ext in self.supported_extensions:
            status[ext] = self.is_registered(ext)
        return status

class ImageCache:
    """이미지 캐싱 시스템"""
    
    def __init__(self, max_size: int = 10, max_memory_mb: int = 100):
        self.max_size = max_size  # 최대 캐시 개수
        self.max_memory_mb = max_memory_mb  # 최대 메모리 사용량 (MB)
        self.cache: OrderedDict[str, Image.Image] = OrderedDict()  # LRU 캐시 구현
        self.memory_usage = 0  # 현재 메모리 사용량 (bytes)
        self.lock = threading.Lock()
        
    def _estimate_memory_usage(self, image: Image.Image) -> int:
        """이미지의 메모리 사용량 추정 (bytes)"""
        if hasattr(image, 'size') and hasattr(image, 'mode'):
            width, height = image.size
            # PIL 이미지의 메모리 사용량 추정
            if image.mode in ['RGB', 'RGBA']:
                bytes_per_pixel = 4  # RGBA 기준
            elif image.mode == 'L':
                bytes_per_pixel = 1  # 그레이스케일
            else:
                bytes_per_pixel = 3  # 기본 RGB
            return width * height * bytes_per_pixel
        return 0
    
    def get(self, key: str) -> Optional[Image.Image]:
        """캐시에서 이미지 가져오기"""
        with self.lock:
            if key in self.cache:
                # LRU 업데이트: 사용된 항목을 맨 뒤로 이동
                self.cache.move_to_end(key)
                log_debug(f"캐시 히트: {key}")
                return self.cache[key]
            log_debug(f"캐시 미스: {key}")
            return None
    
    def put(self, key: str, image: Image.Image) -> None:
        """캐시에 이미지 저장"""
        with self.lock:
            # 이미 존재하는 경우 제거
            if key in self.cache:
                old_image = self.cache[key]
                self.memory_usage -= self._estimate_memory_usage(old_image)
                del self.cache[key]
            
            # 새 이미지 메모리 사용량 계산
            new_memory = self._estimate_memory_usage(image)
            
            # 메모리 제한 확인
            while (len(self.cache) >= self.max_size or 
                   (self.memory_usage + new_memory) > self.max_memory_mb * 1024 * 1024):
                if not self.cache:
                    break
                # 가장 오래된 항목 제거
                oldest_key, oldest_image = self.cache.popitem(last=False)
                self.memory_usage -= self._estimate_memory_usage(oldest_image)
                log_debug(f"캐시에서 제거됨: {oldest_key}")
            
            # 새 이미지 추가
            self.cache[key] = image
            self.memory_usage += new_memory
            log_debug(f"캐시에 추가됨: {key} (메모리: {self.memory_usage / 1024 / 1024:.2f}MB)")
    
    def clear(self) -> None:
        """캐시 완전 정리"""
        with self.lock:
            self.cache.clear()
            self.memory_usage = 0
            log_debug("캐시 완전 정리됨")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage_mb': self.memory_usage / 1024 / 1024,
                'max_memory_mb': self.max_memory_mb
            }

class ImageViewer:
    def __init__(self, initial_file: Optional[str] = None):
        # 드래그 앤 드롭을 지원하려면 TkinterDnD 루트가 필요함
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.root.geometry(DEFAULT_WINDOW_SIZE)  # 기본 창 크기를 더 크게 설정
        self.root.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])  # 최소 창 크기 설정

        self.images: List[str] = []
        self.current_image_index: int = 0
        self.fullscreen: bool = False

        # 메모리 관리 및 캐싱 시스템 초기화
        self.image_cache = ImageCache(max_size=MAX_CACHE_SIZE, max_memory_mb=MAX_MEMORY_MB)
        self.current_photo: Optional[ImageTk.PhotoImage] = None
        self.current_image_path: Optional[str] = None
        self.resize_cache: Dict[str, Image.Image] = {}  # 리사이즈된 이미지 캐시
        self.resize_cache_lock = threading.Lock()  # 리사이즈 캐시 보호 (워커 스레드 접근)

        # 비동기 로딩 상태
        self._load_seq = 0  # 최신 로드 요청 식별용 시퀀스 (오래된 결과 무시)
        self._resize_job: Optional[str] = None  # 리사이즈 디바운스 타이머 ID
        # 워커 스레드 → 메인 스레드 결과 전달용 큐 (Tk는 스레드 안전하지 않으므로
        # 워커에서 위젯을 직접 건드리지 않고 큐에 넣은 뒤 메인 스레드가 폴링한다)
        self._result_queue: "queue.Queue[Tuple[Any, ...]]" = queue.Queue()

        # Windows 파일 연결 관리 초기화
        if is_windows:
            self.file_association = WindowsFileAssociation()

        # 배경색을 더 밝은 색상으로 변경
        self.canvas = tk.Canvas(self.root, bg="#f0f0f0")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 드래그 앤 드롭 등록
        if DND_AVAILABLE:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind("<<Drop>>", self.handle_drop)
            log_debug("드래그 앤 드롭 활성화됨")

        self.create_menu()
        self.setup_bindings()

        # 워커 결과 폴링 시작 (메인 스레드에서만 위젯 갱신)
        self.root.after(RESULT_POLL_INTERVAL_MS, self._poll_load_results)

        # macOS의 파일 오픈 이벤트 처리
        if is_macos:
            try:
                self.root.createcommand('::tk::mac::OpenDocument', self.handle_open_document)
                log_debug("macOS 파일 오픈 이벤트 핸들러 등록 성공")
            except Exception as e:
                log_debug(f"macOS 파일 오픈 이벤트 핸들러 등록 실패: {str(e)}")
        
        # 명령줄에서 또는 파일 연결로 파일을 열 경우 처리
        log_debug(f"초기 파일: {initial_file}")
        if initial_file and os.path.isfile(initial_file):
            log_debug(f"파일 열기 시도: {initial_file}")
            self.open_file(initial_file)

        # 메인 윈도우 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()
    
    def setup_bindings(self) -> None:
        """단축키 및 이벤트 바인딩 설정"""
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.bind("<Left>", lambda e: self.show_previous_image())
        self.root.bind("<Right>", lambda e: self.show_next_image())
        self.root.bind("<space>", lambda e: self.quit())  # Spacebar로 프로그램 종료
        self.root.bind("<Escape>", lambda e: self.quit())  # ESC로 종료
        self.root.bind("<Return>", lambda e: self.toggle_fullscreen())  # Enter로 전체 화면 전환
        self.root.bind("<Control-r>", lambda e: self.clear_cache())  # Ctrl+R로 캐시 정리
        self.root.bind("<Control-m>", lambda e: self.show_memory_info())  # Ctrl+M으로 메모리 정보
        self.root.bind("<Delete>", lambda e: self.delete_current_image())  # Delete 키로 현재 이미지 삭제
    
    def handle_open_document(self, *args: Any) -> None:
        """macOS의 파일 오픈 이벤트 처리"""
        log_debug(f"macOS 파일 오픈 이벤트: {args}")
        if args and os.path.isfile(args[0]):
            self.open_file(args[0])

    def handle_drop(self, event: Any) -> None:
        """드래그 앤 드롭으로 떨어진 파일 처리"""
        # tkinterdnd2는 경로를 공백으로 구분하고, 공백 포함 경로는 {중괄호}로 감쌈
        paths = re.findall(r"\{([^}]*)\}|(\S+)", event.data)
        files = [brace or plain for brace, plain in paths]
        log_debug(f"드롭된 파일: {files}")
        for path in files:
            if os.path.isfile(path) and self.is_image_file(path):
                self.open_file(path)
                return
        if files:
            self.show_error("지원되는 이미지 파일을 드롭해주세요.")

    def create_menu(self) -> None:
        """메뉴 생성"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # 파일 메뉴
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image...", command=self.select_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Esc / Space")
        
        # 보기 메뉴
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen, accelerator="Enter")
        view_menu.add_command(label="Next Image", command=self.show_next_image, accelerator="Right")
        view_menu.add_command(label="Previous Image", command=self.show_previous_image, accelerator="Left")
        
        # 도구 메뉴
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear Cache", command=self.clear_cache, accelerator="Ctrl+R")
        tools_menu.add_command(label="Memory Info", command=self.show_memory_info, accelerator="Ctrl+M")
        
        # Windows에서만 파일 연결 메뉴 추가
        if is_windows:
            tools_menu.add_separator()
            tools_menu.add_command(label="Register as Default Image Viewer", command=self.register_as_default)
            tools_menu.add_command(label="Unregister as Default Image Viewer", command=self.unregister_as_default)
            tools_menu.add_command(label="File Association Status", command=self.show_association_status)
        
        # 도움말 메뉴
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Debug Info", command=self.show_debug_info)
        
        # 단축키 바인딩
        self.root.bind("<Control-o>", lambda e: self.select_image())

    def register_as_default(self) -> None:
        """ImageViewer를 기본 이미지 뷰어로 등록"""
        if not is_windows:
            messagebox.showwarning("지원되지 않음", "이 기능은 Windows에서만 사용할 수 있습니다.")
            return
        
        try:
            # HKEY_CURRENT_USER\Software\Classes 에 기록하므로 관리자 권한이 필요 없음
            # (현재 사용자에 한해 연결되며, 시스템 전역 설정은 변경하지 않음)
            success_count = self.file_association.register_all_extensions()
            
            if success_count > 0:
                messagebox.showinfo("등록 완료", 
                    f"ImageViewer가 기본 이미지 뷰어로 등록되었습니다.\n\n"
                    f"등록된 확장자: {success_count}개\n"
                    f"이제 이미지 파일을 더블클릭하면 ImageViewer로 열립니다.")
                log_debug(f"기본 프로그램 등록 완료: {success_count}개 확장자")
            else:
                messagebox.showerror("등록 실패", "파일 연결 등록에 실패했습니다.")
                
        except Exception as e:
            error_msg = f"등록 중 오류 발생: {str(e)}"
            log_debug(error_msg)
            messagebox.showerror("오류", error_msg)

    def unregister_as_default(self) -> None:
        """ImageViewer의 기본 이미지 뷰어 등록 해제"""
        if not is_windows:
            messagebox.showwarning("지원되지 않음", "이 기능은 Windows에서만 사용할 수 있습니다.")
            return
        
        try:
            # HKEY_CURRENT_USER 기록이므로 관리자 권한이 필요 없음
            # 확인 대화상자
            result = messagebox.askyesno("등록 해제", 
                "ImageViewer의 기본 이미지 뷰어 등록을 해제하시겠습니까?\n\n"
                "이 작업은 되돌릴 수 없습니다.")
            
            if result:
                # 모든 확장자 해제
                success_count = self.file_association.unregister_all_extensions()
                
                if success_count > 0:
                    messagebox.showinfo("해제 완료", 
                        f"ImageViewer의 기본 이미지 뷰어 등록이 해제되었습니다.\n\n"
                        f"해제된 확장자: {success_count}개")
                    log_debug(f"기본 프로그램 해제 완료: {success_count}개 확장자")
                else:
                    messagebox.showerror("해제 실패", "파일 연결 해제에 실패했습니다.")
                    
        except Exception as e:
            error_msg = f"해제 중 오류 발생: {str(e)}"
            log_debug(error_msg)
            messagebox.showerror("오류", error_msg)

    def show_association_status(self) -> None:
        """파일 연결 상태 표시"""
        if not is_windows:
            messagebox.showwarning("지원되지 않음", "이 기능은 Windows에서만 사용할 수 있습니다.")
            return
        
        try:
            status = self.file_association.get_registration_status()
            
            info = "파일 연결 상태:\n\n"
            registered_count = 0
            
            for ext, is_registered in status.items():
                status_text = "등록됨" if is_registered else "미등록"
                info += f"{ext.upper()}: {status_text}\n"
                if is_registered:
                    registered_count += 1
            
            info += f"\n총 {len(status)}개 확장자 중 {registered_count}개 등록됨"
            
            messagebox.showinfo("파일 연결 상태", info)
            
        except Exception as e:
            error_msg = f"상태 확인 중 오류 발생: {str(e)}"
            log_debug(error_msg)
            messagebox.showerror("오류", error_msg)

    def select_image(self) -> None:
        """파일 선택 대화상자를 표시하고 선택한 이미지 열기"""
        file_path = filedialog.askopenfilename(
            title="이미지 파일 열기",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.tif"),
                ("JPEG 이미지", "*.jpg *.jpeg"),
                ("PNG 이미지", "*.png"),
                ("GIF 이미지", "*.gif"),
                ("모든 파일", "*.*")
            ]
        )
        if file_path:
            log_debug(f"사용자 선택 파일: {file_path}")
            self.open_file(file_path)

    def open_file(self, file_path: str):
        """파일 경로를 받아 이미지를 열고 표시합니다."""
        log_debug(f"open_file 호출됨: {file_path}")
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            error_msg = f"파일이 존재하지 않음: {file_path}"
            log_debug(error_msg)
            self.show_error(error_msg)
            return
            
        if self.is_image_file(file_path):
            try:
                directory = os.path.dirname(file_path)
                log_debug(f"디렉토리: {directory}")
                self.images = self.get_image_files_from_directory(directory)
                log_debug(f"발견된 이미지 파일: {len(self.images)}개")
                self.current_image_index = self.get_current_image_index(file_path)
                log_debug(f"현재 이미지 인덱스: {self.current_image_index}")
                self.show_image(self.current_image_index)
            except Exception as e:
                error_msg = f"파일 열기 오류: {str(e)}"
                log_debug(error_msg)
                self.show_error(error_msg)
        else:
            error_msg = f"지원되지 않는 파일 형식입니다: {file_path}"
            log_debug(error_msg)
            self.show_error(error_msg)

    def get_image_files_from_directory(self, directory: str) -> List[str]:
        try:
            all_files = os.listdir(directory)
            log_debug(f"디렉토리의 모든 파일: {len(all_files)}개")
            
            image_files = [os.path.join(directory, file) for file in all_files
                          if os.path.isfile(os.path.join(directory, file)) and self.is_image_file(os.path.join(directory, file))]
            image_files.sort(key=natural_sort_key)
            return image_files
        except Exception as e:
            log_debug(f"디렉토리 열기 오류: {str(e)}")
            return []

    def is_image_file(self, file_path: str) -> bool:
        """파일이 지원되는 이미지 형식인지 확인"""
        _, ext = os.path.splitext(file_path)
        result = ext.lower() in SUPPORTED_EXTENSIONS
        log_debug(f"파일 확인: {file_path} - 이미지 여부: {result}")
        return result

    def get_current_image_index(self, file_path: str) -> int:
        """주어진 파일 경로의 이미지 인덱스 반환"""
        file_path = os.path.abspath(file_path).lower()
        for i, image_path in enumerate(self.images):
            if os.path.abspath(image_path).lower() == file_path:
                return i
        return 0

    def load_image_from_cache_or_file(self, file_path: str) -> Image.Image:
        """캐시에서 이미지를 가져오거나 파일에서 로드"""
        # 캐시에서 먼저 확인
        cached_image = self.image_cache.get(file_path)
        if cached_image:
            return cached_image
        
        # 파일에서 로드
        try:
            image = Image.open(file_path)
            # 캐시에 저장
            self.image_cache.put(file_path, image)
            return image
        except Exception as e:
            log_debug(f"이미지 로드 실패: {file_path} - {str(e)}")
            raise

    def show_image(self, index: int):
        """주어진 인덱스의 이미지를 비동기로 로드하여 표시"""
        if not self.images:
            self.show_error("이미지가 없습니다.")
            return
        if index >= len(self.images):
            return

        file_path = self.images[index]
        log_debug(f"이미지 표시 시도: {file_path}")
        if not self.is_image_file(file_path):
            return

        # 캔버스 크기는 메인 스레드에서만 안전하게 읽을 수 있으므로 여기서 확보
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = DEFAULT_CANVAS_SIZE

        # 최신 요청만 화면에 반영하기 위한 시퀀스 토큰
        self._load_seq += 1
        seq = self._load_seq

        self.show_loading_indicator()

        worker = threading.Thread(
            target=self._load_image_worker,
            args=(seq, file_path, canvas_width, canvas_height),
            daemon=True,
        )
        worker.start()

    def _load_image_worker(self, seq: int, file_path: str,
                           canvas_width: int, canvas_height: int) -> None:
        """백그라운드 스레드: 디스크 로드 및 리사이즈 (Tk 위젯은 건드리지 않음).

        결과는 큐에 넣고, 실제 위젯 갱신은 메인 스레드의 _poll_load_results가 처리한다.
        """
        try:
            image = self.load_image_from_cache_or_file(file_path)
            resized_image = self.get_resized_image(image, file_path, canvas_width, canvas_height)
            self._result_queue.put(("ok", seq, file_path, resized_image))
        except (UnidentifiedImageError, OSError) as e:
            error_msg = f"이미지를 열 수 없습니다: {file_path}\n{str(e)}"
            log_debug(error_msg)
            self._result_queue.put(("err", seq, error_msg))
        except Exception as e:
            error_msg = f"이미지 표시 중 오류 발생: {str(e)}"
            log_debug(error_msg)
            self._result_queue.put(("err", seq, error_msg))

    def _poll_load_results(self) -> None:
        """메인 스레드: 워커가 큐에 넣은 결과를 주기적으로 처리"""
        try:
            while True:
                item = self._result_queue.get_nowait()
                kind = item[0]
                if kind == "ok":
                    _, seq, file_path, resized_image = item
                    self._apply_loaded_image(seq, file_path, resized_image)
                else:
                    _, seq, message = item
                    self._apply_load_error(seq, message)
        except queue.Empty:
            pass
        finally:
            # 다음 폴링 예약 (창이 살아있는 동안 계속).
            # 종료 후 root가 파괴되면 TclError가 발생하므로 무시한다.
            try:
                self.root.after(RESULT_POLL_INTERVAL_MS, self._poll_load_results)
            except tk.TclError:
                pass

    def _apply_loaded_image(self, seq: int, file_path: str,
                            resized_image: Image.Image) -> None:
        """메인 스레드: 로드 완료된 이미지를 화면에 반영"""
        if seq != self._load_seq:
            # 더 최신 요청이 진행 중이므로 이 결과는 폐기
            log_debug(f"오래된 로드 결과 무시: {file_path}")
            return
        self.cleanup_current_image()
        self.current_photo = ImageTk.PhotoImage(resized_image)
        self.current_image_path = file_path
        self.display_image()
        self.root.title(f"Image Viewer - {os.path.basename(file_path)}")
        log_debug("이미지 표시 성공")
        self.cleanup_memory()

    def _apply_load_error(self, seq: int, message: str) -> None:
        """메인 스레드: 로드 실패 처리"""
        if seq != self._load_seq:
            return
        self.show_error(message)

    def show_loading_indicator(self) -> None:
        """로딩 중 안내 문구를 캔버스 중앙에 표시"""
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = DEFAULT_CANVAS_SIZE
        self.canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text="로딩 중...", fill="#888888", font=("", 14),
        )

    def cleanup_current_image(self):
        """현재 이미지 메모리 정리"""
        if self.current_photo:
            # PhotoImage의 참조 제거
            self.current_photo = None
            self.current_image_path = None

    def cleanup_memory(self):
        """메모리 정리"""
        # 가비지 컬렉션 강제 실행
        gc.collect()
        log_debug("메모리 정리 완료")

    def get_resized_image(self, image: Image.Image, file_path: str,
                          canvas_width: int, canvas_height: int) -> Image.Image:
        """리사이즈된 이미지 가져오기 (캐시 활용, 워커 스레드에서 호출됨)"""
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = DEFAULT_CANVAS_SIZE

        # 캐시 키 생성
        cache_key = f"{file_path}_{canvas_width}x{canvas_height}"

        # 리사이즈 캐시에서 확인
        with self.resize_cache_lock:
            if cache_key in self.resize_cache:
                log_debug(f"리사이즈 캐시 히트: {cache_key}")
                return self.resize_cache[cache_key]

        # 새로 리사이즈 (락 밖에서 수행 — 시간이 오래 걸릴 수 있음)
        resized_image = self.resize_image(image, canvas_width, canvas_height)

        with self.resize_cache_lock:
            # 리사이즈 캐시 크기 제한
            if len(self.resize_cache) >= MAX_RESIZE_CACHE_SIZE and self.resize_cache:
                oldest_key = next(iter(self.resize_cache))
                del self.resize_cache[oldest_key]
            self.resize_cache[cache_key] = resized_image
            log_debug(f"리사이즈 캐시에 추가: {cache_key}")

        return resized_image

    def resize_image(self, image: Image.Image, canvas_width: int, canvas_height: int) -> Image.Image:
        """이미지를 캔버스 크기에 맞게 리사이즈"""
        image_ratio = image.width / image.height
        canvas_ratio = canvas_width / canvas_height
        
        if image_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / image_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * image_ratio)
            
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def display_image(self) -> None:
        """현재 이미지를 캔버스에 표시"""
        if not self.current_photo:
            return
            
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = DEFAULT_CANVAS_SIZE[0]
            canvas_height = DEFAULT_CANVAS_SIZE[1]
            
        x = (canvas_width - self.current_photo.width()) // 2
        y = (canvas_height - self.current_photo.height()) // 2
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.current_photo)

    def show_next_image(self) -> None:
        """다음 이미지 표시"""
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_image(self.current_image_index)

    def show_previous_image(self) -> None:
        """이전 이미지 표시"""
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.show_image(self.current_image_index)

    def on_window_resize(self, event: tk.Event) -> None:
        """윈도우 크기 변경 시 이미지 리사이즈 (디바운싱 적용)"""
        # <Configure> 이벤트는 드래그 중 매우 빈번하게 발생하므로,
        # 마지막 이벤트로부터 일정 시간이 지난 뒤 한 번만 리사이즈한다.
        if not (hasattr(self, 'current_photo') and self.current_photo):
            return
        # 캔버스 위젯이 아닌 이벤트는 무시 (메뉴/자식 위젯 Configure 노이즈 방지)
        if event.widget is not self.root:
            return
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(150, self._do_resize)

    def _do_resize(self) -> None:
        """디바운스 후 실제 리사이즈 수행"""
        self._resize_job = None
        with self.resize_cache_lock:
            self.resize_cache.clear()
        self.show_image(self.current_image_index)

    def toggle_fullscreen(self) -> None:
        """전체 화면 전환"""
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        
        if self.fullscreen:
            # 전체 화면에서 메뉴바 숨기기
            self.root.config(menu="")
            log_debug("전체 화면 모드: 메뉴바 숨김")
        else:
            # 일반 모드에서 메뉴바 복원
            self.root.config(menu=self.menubar)
            self.root.geometry(DEFAULT_WINDOW_SIZE)  # 전체화면 해제 시 기본 크기 변경
            log_debug("일반 모드: 메뉴바 복원")

    def _clear_resize_cache(self) -> None:
        """리사이즈 캐시를 스레드 안전하게 비움"""
        with self.resize_cache_lock:
            self.resize_cache.clear()

    def clear_cache(self) -> None:
        """캐시 정리"""
        self.image_cache.clear()
        self._clear_resize_cache()
        self.cleanup_memory()
        log_debug("모든 캐시 정리 완료")
        messagebox.showinfo("캐시 정리", "모든 캐시가 정리되었습니다.")

    def show_memory_info(self) -> None:
        """메모리 정보 표시"""
        cache_stats = self.image_cache.get_stats()
        info = f"이미지 캐시:\n"
        info += f"  - 캐시된 이미지: {cache_stats['size']}/{cache_stats['max_size']}\n"
        info += f"  - 메모리 사용량: {cache_stats['memory_usage_mb']:.2f}MB/{cache_stats['max_memory_mb']}MB\n"
        info += f"리사이즈 캐시:\n"
        info += f"  - 캐시된 리사이즈: {len(self.resize_cache)}/{MAX_RESIZE_CACHE_SIZE}\n"
        
        messagebox.showinfo("메모리 정보", info)

    def quit(self) -> None:
        """프로그램 종료"""
        log_debug("프로그램 종료")
        # 메모리 정리
        self.cleanup_current_image()
        self.image_cache.clear()
        self._clear_resize_cache()
        self.cleanup_memory()
        self.root.quit()

    def delete_current_image(self) -> None:
        """현재 보고 있는 이미지를 삭제합니다."""
        if not self.current_image_path:
            messagebox.showinfo("삭제 불가", "삭제할 이미지가 없습니다.")
            return

        file_to_delete = self.current_image_path
        file_name = os.path.basename(file_to_delete)

        if messagebox.askyesno("이미지 삭제 확인", f"'{file_name}' 파일을 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다."):
            try:
                os.remove(file_to_delete)
                log_debug(f"파일 삭제 성공: {file_to_delete}")
                messagebox.showinfo("삭제 완료", f"'{file_name}' 파일이 성공적으로 삭제되었습니다.")

                # 이미지 목록에서 삭제된 파일 제거
                if file_to_delete in self.images:
                    self.images.remove(file_to_delete)

                # 캐시에서도 제거
                self.image_cache.clear() # 전체 캐시를 비우는 것이 가장 안전
                self._clear_resize_cache()

                # 다음 이미지 표시 또는 빈 화면
                if self.images:
                    # 현재 인덱스가 목록의 끝을 넘어가지 않도록 조정
                    if self.current_image_index >= len(self.images):
                        self.current_image_index = len(self.images) - 1
                    # 현재 인덱스가 음수가 되지 않도록 조정 (모든 이미지가 삭제된 경우)
                    if self.current_image_index < 0:
                        self.current_image_index = 0
                    self.show_image(self.current_image_index)
                else:
                    self.canvas.delete("all")
                    self.root.title("Image Viewer")
                    self.current_photo = None
                    self.current_image_path = None
                    messagebox.showinfo("알림", "더 이상 표시할 이미지가 없습니다.")

            except OSError as e:
                error_msg = f"파일 삭제 실패: {file_name}\n{str(e)}\n\n파일이 사용 중이거나 권한이 없을 수 있습니다."
                log_debug(error_msg)
                messagebox.showerror("삭제 오류", error_msg)
            except Exception as e:
                error_msg = f"예상치 못한 오류 발생: {file_name}\n{str(e)}"
                log_debug(error_msg)
                messagebox.showerror("삭제 오류", error_msg)

    def show_error(self, message: str) -> None:
        """오류 메시지 표시"""
        messagebox.showerror("오류", message)

    def show_debug_info(self) -> None:
        """디버그 정보 표시"""
        cache_stats = self.image_cache.get_stats()
        info = f"OS: {platform.system()}\n"
        info += f"Python 버전: {sys.version}\n"
        info += f"현재 작업 디렉토리: {os.getcwd()}\n"
        info += f"이미지 파일 수: {len(self.images)}\n"
        info += f"현재 이미지 인덱스: {self.current_image_index}\n"
        info += f"캐시된 이미지: {cache_stats['size']}/{cache_stats['max_size']}\n"
        info += f"메모리 사용량: {cache_stats['memory_usage_mb']:.2f}MB\n"
        info += f"리사이즈 캐시: {len(self.resize_cache)}/{MAX_RESIZE_CACHE_SIZE}\n"
        
        # Windows 파일 연결 상태 추가
        if is_windows and hasattr(self, 'file_association'):
            status = self.file_association.get_registration_status()
            registered_count = sum(1 for is_registered in status.values() if is_registered)
            info += f"파일 연결: {registered_count}/{len(status)}개 등록됨\n"
        
        if self.images and self.current_image_index < len(self.images):
            info += f"현재 이미지: {self.images[self.current_image_index]}\n"
        messagebox.showinfo("디버그 정보", info)

if __name__ == "__main__":
    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    ImageViewer(initial_file)
