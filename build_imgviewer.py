#!/usr/bin/env python3
"""
imgViewer.py 빌드 스크립트

이 스크립트는 imgViewer.py를 독립 실행형 exe 파일로 빌드합니다.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_with_color(message, color_code=36):
    """색상이 있는 메시지 출력"""
    print(f"\033[{color_code}m{message}\033[0m")

def build_imgviewer():
    """imgViewer.py를 실행 파일로 빌드"""
    
    # 현재 스크립트 경로
    script_dir = Path(__file__).parent
    imgviewer_path = script_dir / "imgViewer.py"
    
    # 빌드 출력 디렉토리
    dist_dir = script_dir / "dist"
    build_dir = script_dir / "build"
    
    print_with_color("=== imgViewer 빌드 시작 ===", 33)
    print_with_color(f"빌드 대상: {imgviewer_path}", 36)
    
    # 기존 빌드 파일 정리
    if dist_dir.exists():
        print_with_color("기존 dist 폴더 정리 중...", 33)
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print_with_color("기존 build 폴더 정리 중...", 33)
        shutil.rmtree(build_dir)
    
    # PyInstaller 명령어 구성
    cmd = [
        "pyinstaller",
        "--onefile",                    # 단일 실행 파일 생성
        "--noconsole",                  # 콘솔 창 숨기기
        "--name=ImageViewer",           # 실행 파일 이름
        "--distpath", str(dist_dir),    # 출력 디렉토리
        "--workpath", str(build_dir),   # 작업 디렉토리
        "--clean",                      # 빌드 전 정리
        "--windowed",                   # GUI 애플리케이션으로 설정
        "--uac-admin",                  # 관리자 권한 요청
        str(imgviewer_path)             # 빌드할 Python 파일
    ]
    
    print_with_color("PyInstaller 명령어:", 36)
    print(" ".join(cmd))
    print()
    
    try:
        # PyInstaller 실행
        print_with_color("빌드 진행 중...", 33)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print_with_color("=== 빌드 성공! ===", 32)
            
            # 빌드 결과 확인
            exe_path = dist_dir / "ImageViewer.exe"
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print_with_color(f"실행 파일 생성됨: {exe_path}", 32)
                print_with_color(f"파일 크기: {file_size:.2f} MB", 36)
                
                # 실행 파일 정보 출력
                print_with_color("\n=== 빌드 정보 ===", 33)
                print(f"실행 파일 경로: {exe_path}")
                print(f"파일 크기: {file_size:.2f} MB")
                print(f"빌드 디렉토리: {build_dir}")
                print(f"출력 디렉토리: {dist_dir}")
                
                # 사용법 안내
                print_with_color("\n=== 사용법 ===", 33)
                print("1. 더블클릭으로 실행")
                print("2. 명령줄에서 실행: ImageViewer.exe [이미지파일경로]")
                print("3. 이미지 파일을 드래그 앤 드롭으로 열기")
                print("4. 기본 프로그램 등록: Tools > Register as Default Image Viewer")
                
                # 관리자 권한 안내
                print_with_color("\n=== 관리자 권한 ===", 33)
                print("파일 연결 기능을 사용하려면 관리자 권한으로 실행하세요:")
                print("1. ImageViewer.exe를 우클릭")
                print("2. '관리자 권한으로 실행' 선택")
                print("3. Tools > Register as Default Image Viewer 실행")
                
            else:
                print_with_color("오류: 실행 파일이 생성되지 않았습니다.", 31)
                return False
                
        else:
            print_with_color("=== 빌드 실패 ===", 31)
            print_with_color("오류 출력:", 31)
            print(result.stderr)
            return False
            
    except Exception as e:
        print_with_color(f"빌드 중 오류 발생: {e}", 31)
        return False
    
    return True

def cleanup_build_files():
    """빌드 임시 파일 정리"""
    script_dir = Path(__file__).parent
    build_dir = script_dir / "build"
    spec_file = script_dir / "ImageViewer.spec"
    
    print_with_color("\n=== 빌드 파일 정리 ===", 33)
    
    # build 폴더 정리
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            print_with_color("build 폴더 정리 완료", 32)
        except Exception as e:
            print_with_color(f"build 폴더 정리 실패: {e}", 31)
    
    # .spec 파일 정리
    if spec_file.exists():
        try:
            spec_file.unlink()
            print_with_color(".spec 파일 정리 완료", 32)
        except Exception as e:
            print_with_color(f".spec 파일 정리 실패: {e}", 31)

if __name__ == "__main__":
    print_with_color("imgViewer 빌드 스크립트", 35)
    print_with_color("=" * 50, 35)
    
    # 빌드 실행
    success = build_imgviewer()
    
    if success:
        # 빌드 성공 시 임시 파일 정리
        cleanup_build_files()
        print_with_color("\n빌드가 완료되었습니다!", 32)
    else:
        print_with_color("\n빌드에 실패했습니다.", 31)
        sys.exit(1) 