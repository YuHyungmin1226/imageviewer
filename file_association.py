from __future__ import annotations

import os
import sys

from constants import APP_DISPLAY_NAME, APP_NAME, SUPPORTED_EXTENSIONS


def register_file_associations(silent: bool = False) -> bool:
    """ImageViewer를 Windows의 '기본 프로그램 선택' 목록에 등록.

    HKEY_CURRENT_USER에만 기록하므로 관리자 권한이 필요 없다. 등록 후에는
    Windows의 정책상 사용자가 설정 앱에서 직접 기본 앱으로 선택해야 적용된다.
    """
    if os.name != "nt":
        return False

    import ctypes
    import winreg

    if getattr(sys, "frozen", False):
        exe_path = os.path.abspath(sys.executable)
        cmd = f'"{exe_path}" "%1"'
    else:
        python_exe = os.path.abspath(sys.executable)
        script_path = os.path.abspath(sys.argv[0])
        cmd = f'"{python_exe}" "{script_path}" "%1"'
        exe_path = python_exe

    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{APP_NAME}") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, APP_DISPLAY_NAME)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{APP_NAME}\shell\open\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, cmd)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{APP_NAME}\DefaultIcon") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"{exe_path},0")

        capabilities_path = rf"Software\{APP_NAME}\Capabilities"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, capabilities_path) as key:
            winreg.SetValueEx(key, "ApplicationName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "ApplicationDescription", 0, winreg.REG_SZ, "Minimal Image Viewer")

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{capabilities_path}\FileAssociations") as key:
            for ext in sorted(SUPPORTED_EXTENSIONS):
                winreg.SetValueEx(key, ext, 0, winreg.REG_SZ, APP_NAME)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\RegisteredApplications") as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, capabilities_path)

        for ext in sorted(SUPPORTED_EXTENSIONS):
            assoc_path = rf"Software\Classes\{ext}\OpenWithProgids"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, assoc_path) as key:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_NONE, b"")

        try:
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
        except Exception as shell_err:
            if not silent:
                print(f"Failed to send Shell notification: {shell_err}")

        return True
    except Exception as e:
        if not silent:
            print(f"Registry registration failed: {e}")
        return False
