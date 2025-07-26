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

# Windows 레지스트리 관련 import
if platform.system() == "Windows":
    import winreg
    import subprocess

# OS 타입 확인
is_windows = platform.system() == "Windows"
is_macos = platform.system() == "Darwin"

# 디버깅용 로그 파일
DEBUG_LOG = os.path.expanduser("~/Desktop/imageviewer_debug.log")

def log_debug(message):
    """디버그 메시지를 파일에 기록"""
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"로그 기록 실패: {e}")

# 시작 시 로그
log_debug("===== 프로그램 시작 =====")
log_debug(f"OS: {platform.system()}")
log_debug(f"Python 버전: {sys.version}")
log_debug(f"명령줄 인수: {sys.argv}")
log_debug(f"현재 작업 디렉토리: {os.getcwd()}")

# macOS에서 앱 번들 내 위치 확인
if hasattr(sys, 'frozen') and getattr(sys, 'frozen'):
    log_debug(f"앱 번들 경로: {sys.executable}")
    log_debug(f"앱 리소스 경로: {getattr(sys, '_MEIPASS', 'Not available')}")

class WindowsFileAssociation:
    """Windows 파일 연결 관리 클래스"""
    
    def __init__(self):
        self.app_name = "ImageViewer"
        self.app_description = "HM Utils Image Viewer"
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']
        
    def get_executable_path(self):
        """실행 파일 경로 반환"""
        if hasattr(sys, 'frozen') and getattr(sys, 'frozen'):
            # PyInstaller로 빌드된 실행 파일
            return sys.executable
        else:
            # Python 스크립트
            return sys.executable + ' "' + os.path.abspath(__file__) + '"'
    
    def register_file_association(self, extension):
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
    
    def unregister_file_association(self, extension):
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
    
    def register_all_extensions(self):
        """모든 지원 확장자를 등록"""
        success_count = 0
        for ext in self.supported_extensions:
            if self.register_file_association(ext):
                success_count += 1
        
        log_debug(f"전체 파일 연결 등록 완료: {success_count}/{len(self.supported_extensions)}")
        return success_count
    
    def unregister_all_extensions(self):
        """모든 지원 확장자의 연결 해제"""
        success_count = 0
        for ext in self.supported_extensions:
            if self.unregister_file_association(ext):
                success_count += 1
        
        log_debug(f"전체 파일 연결 해제 완료: {success_count}/{len(self.supported_extensions)}")
        return success_count
    
    def is_registered(self, extension):
        """특정 확장자가 등록되어 있는지 확인"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{extension}")
            value, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            return value == f"{self.app_name}{extension}"
        except:
            return False
    
    def get_registration_status(self):
        """모든 확장자의 등록 상태 확인"""
        status = {}
        for ext in self.supported_extensions:
            status[ext] = self.is_registered(ext)
        return status

class ImageCache:
    """이미지 캐싱 시스템"""
    
    def __init__(self, max_size=10, max_memory_mb=100):
        self.max_size = max_size  # 최대 캐시 개수
        self.max_memory_mb = max_memory_mb  # 최대 메모리 사용량 (MB)
        self.cache = OrderedDict()  # LRU 캐시 구현
        self.memory_usage = 0  # 현재 메모리 사용량 (bytes)
        self.lock = threading.Lock()
        
    def _estimate_memory_usage(self, image):
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
    
    def get(self, key):
        """캐시에서 이미지 가져오기"""
        with self.lock:
            if key in self.cache:
                # LRU 업데이트: 사용된 항목을 맨 뒤로 이동
                self.cache.move_to_end(key)
                log_debug(f"캐시 히트: {key}")
                return self.cache[key]
            log_debug(f"캐시 미스: {key}")
            return None
    
    def put(self, key, image):
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
    
    def clear(self):
        """캐시 완전 정리"""
        with self.lock:
            self.cache.clear()
            self.memory_usage = 0
            log_debug("캐시 완전 정리됨")
    
    def get_stats(self):
        """캐시 통계 반환"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage_mb': self.memory_usage / 1024 / 1024,
                'max_memory_mb': self.max_memory_mb
            }

class ImageViewer:
    def __init__(self, initial_file=None):
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.root.geometry("800x600")  # 기본 창 크기를 더 크게 설정
        self.root.minsize(400, 300)  # 최소 창 크기 설정

        self.images = []
        self.current_image_index = 0
        self.fullscreen = False
        
        # 메모리 관리 및 캐싱 시스템 초기화
        self.image_cache = ImageCache(max_size=15, max_memory_mb=200)
        self.current_photo = None
        self.current_image_path = None
        self.resize_cache = {}  # 리사이즈된 이미지 캐시
        
        # Windows 파일 연결 관리 초기화
        if is_windows:
            self.file_association = WindowsFileAssociation()
        
        # 배경색을 더 밝은 색상으로 변경
        self.canvas = tk.Canvas(self.root, bg="#f0f0f0")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.create_menu()
        self.setup_bindings()

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
    
    def setup_bindings(self):
        """단축키 및 이벤트 바인딩 설정"""
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.bind("<Left>", lambda e: self.show_previous_image())
        self.root.bind("<Right>", lambda e: self.show_next_image())
        self.root.bind("<space>", lambda e: self.quit())  # Spacebar로 프로그램 종료
        self.root.bind("<Escape>", lambda e: self.quit())  # ESC로 종료
        self.root.bind("<Return>", lambda e: self.toggle_fullscreen())  # Enter로 전체 화면 전환
        self.root.bind("<Control-r>", lambda e: self.clear_cache())  # Ctrl+R로 캐시 정리
        self.root.bind("<Control-m>", lambda e: self.show_memory_info())  # Ctrl+M으로 메모리 정보
    
    def handle_open_document(self, *args):
        """macOS의 파일 오픈 이벤트 처리"""
        log_debug(f"macOS 파일 오픈 이벤트: {args}")
        if args and os.path.isfile(args[0]):
            self.open_file(args[0])

    def create_menu(self):
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

    def register_as_default(self):
        """ImageViewer를 기본 이미지 뷰어로 등록"""
        if not is_windows:
            messagebox.showwarning("지원되지 않음", "이 기능은 Windows에서만 사용할 수 있습니다.")
            return
        
        try:
            # 관리자 권한 확인
            if not self.check_admin_privileges():
                messagebox.showwarning("권한 필요", "파일 연결을 등록하려면 관리자 권한이 필요합니다.\n\n관리자 권한으로 프로그램을 다시 실행해주세요.")
                return
            
            # 모든 확장자 등록
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

    def unregister_as_default(self):
        """ImageViewer의 기본 이미지 뷰어 등록 해제"""
        if not is_windows:
            messagebox.showwarning("지원되지 않음", "이 기능은 Windows에서만 사용할 수 있습니다.")
            return
        
        try:
            # 관리자 권한 확인
            if not self.check_admin_privileges():
                messagebox.showwarning("권한 필요", "파일 연결을 해제하려면 관리자 권한이 필요합니다.\n\n관리자 권한으로 프로그램을 다시 실행해주세요.")
                return
            
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

    def show_association_status(self):
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

    def check_admin_privileges(self):
        """관리자 권한 확인"""
        try:
            # 레지스트리 쓰기 권한 테스트
            test_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\ImageViewerTest")
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, "Software\\ImageViewerTest")
            return True
        except:
            return False

    def select_image(self):
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

    def open_file(self, file_path):
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

    def get_image_files_from_directory(self, directory):
        try:
            all_files = os.listdir(directory)
            log_debug(f"디렉토리의 모든 파일: {len(all_files)}개")
            
            image_files = [os.path.join(directory, file) for file in all_files
                          if os.path.isfile(os.path.join(directory, file)) and self.is_image_file(os.path.join(directory, file))]
            image_files.sort()
            return image_files
        except Exception as e:
            log_debug(f"디렉토리 열기 오류: {str(e)}")
            return []

    def is_image_file(self, file_path):
        """파일이 지원되는 이미지 형식인지 확인"""
        _, ext = os.path.splitext(file_path)
        result = ext.lower() in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif")
        log_debug(f"파일 확인: {file_path} - 이미지 여부: {result}")
        return result

    def get_current_image_index(self, file_path):
        """주어진 파일 경로의 이미지 인덱스 반환"""
        file_path = os.path.abspath(file_path).lower()
        for i, image_path in enumerate(self.images):
            if os.path.abspath(image_path).lower() == file_path:
                return i
        return 0

    def load_image_from_cache_or_file(self, file_path):
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

    def show_image(self, index):
        """주어진 인덱스의 이미지 표시"""
        if not self.images:
            self.show_error("이미지가 없습니다.")
            return
            
        try:
            if index < len(self.images):
                file_path = self.images[index]
                log_debug(f"이미지 표시 시도: {file_path}")
                
                if self.is_image_file(file_path):
                    try:
                        # 이전 이미지 메모리 정리
                        self.cleanup_current_image()
                        
                        # 새 이미지 로드
                        image = self.load_image_from_cache_or_file(file_path)
                        log_debug(f"이미지 크기: {image.size}, 형식: {image.format}")
                        
                        # 리사이즈된 이미지 생성
                        resized_image = self.get_resized_image(image, file_path)
                        log_debug(f"리사이즈된 이미지 크기: {resized_image.size}")
                        
                        # PhotoImage 생성 및 표시
                        self.current_photo = ImageTk.PhotoImage(resized_image)
                        self.current_image_path = file_path
                        self.display_image()
                        self.root.title(f"Image Viewer - {os.path.basename(file_path)}")
                        log_debug("이미지 표시 성공")
                        
                        # 메모리 정리
                        self.cleanup_memory()
                        
                    except (UnidentifiedImageError, OSError) as e:
                        error_msg = f"이미지를 열 수 없습니다: {file_path}\n{str(e)}"
                        log_debug(error_msg)
                        self.show_error(error_msg)
        except Exception as e:
            error_msg = f"이미지 표시 중 오류 발생: {str(e)}"
            log_debug(error_msg)
            self.show_error(error_msg)

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

    def get_resized_image(self, image, file_path):
        """리사이즈된 이미지 가져오기 (캐시 활용)"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 640
            canvas_height = 480
        
        # 캐시 키 생성
        cache_key = f"{file_path}_{canvas_width}x{canvas_height}"
        
        # 리사이즈 캐시에서 확인
        if cache_key in self.resize_cache:
            log_debug(f"리사이즈 캐시 히트: {cache_key}")
            return self.resize_cache[cache_key]
        
        # 새로 리사이즈
        resized_image = self.resize_image(image, canvas_width, canvas_height)
        
        # 리사이즈 캐시 크기 제한 (최대 20개)
        if len(self.resize_cache) >= 20:
            # 가장 오래된 항목 제거
            oldest_key = next(iter(self.resize_cache))
            del self.resize_cache[oldest_key]
        
        # 캐시에 저장
        self.resize_cache[cache_key] = resized_image
        log_debug(f"리사이즈 캐시에 추가: {cache_key}")
        
        return resized_image

    def resize_image(self, image, canvas_width, canvas_height):
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

    def display_image(self):
        """현재 이미지를 캔버스에 표시"""
        if not self.current_photo:
            return
            
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 640
            canvas_height = 480
            
        x = (canvas_width - self.current_photo.width()) // 2
        y = (canvas_height - self.current_photo.height()) // 2
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.current_photo)

    def show_next_image(self):
        """다음 이미지 표시"""
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_image(self.current_image_index)

    def show_previous_image(self):
        """이전 이미지 표시"""
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.show_image(self.current_image_index)

    def on_window_resize(self, event):
        """윈도우 크기 변경 시 이미지 리사이즈"""
        if hasattr(self, 'current_photo') and self.current_photo:
            # 리사이즈 캐시 클리어 (창 크기가 변경되었으므로)
            self.resize_cache.clear()
            self.show_image(self.current_image_index)

    def toggle_fullscreen(self):
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
            self.root.geometry("800x600")  # 전체화면 해제 시 기본 크기 변경
            log_debug("일반 모드: 메뉴바 복원")

    def clear_cache(self):
        """캐시 정리"""
        self.image_cache.clear()
        self.resize_cache.clear()
        self.cleanup_memory()
        log_debug("모든 캐시 정리 완료")
        messagebox.showinfo("캐시 정리", "모든 캐시가 정리되었습니다.")

    def show_memory_info(self):
        """메모리 정보 표시"""
        cache_stats = self.image_cache.get_stats()
        info = f"이미지 캐시:\n"
        info += f"  - 캐시된 이미지: {cache_stats['size']}/{cache_stats['max_size']}\n"
        info += f"  - 메모리 사용량: {cache_stats['memory_usage_mb']:.2f}MB/{cache_stats['max_memory_mb']}MB\n"
        info += f"리사이즈 캐시:\n"
        info += f"  - 캐시된 리사이즈: {len(self.resize_cache)}/20\n"
        
        messagebox.showinfo("메모리 정보", info)

    def quit(self):
        """프로그램 종료"""
        log_debug("프로그램 종료")
        # 메모리 정리
        self.cleanup_current_image()
        self.image_cache.clear()
        self.resize_cache.clear()
        self.cleanup_memory()
        self.root.quit()

    def show_error(self, message):
        """오류 메시지 표시"""
        messagebox.showerror("오류", message)

    def show_debug_info(self):
        """디버그 정보 표시"""
        cache_stats = self.image_cache.get_stats()
        info = f"OS: {platform.system()}\n"
        info += f"Python 버전: {sys.version}\n"
        info += f"현재 작업 디렉토리: {os.getcwd()}\n"
        info += f"이미지 파일 수: {len(self.images)}\n"
        info += f"현재 이미지 인덱스: {self.current_image_index}\n"
        info += f"캐시된 이미지: {cache_stats['size']}/{cache_stats['max_size']}\n"
        info += f"메모리 사용량: {cache_stats['memory_usage_mb']:.2f}MB\n"
        info += f"리사이즈 캐시: {len(self.resize_cache)}/20\n"
        
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
