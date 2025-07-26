#!/usr/bin/env python3
"""
파일 업로드 테스트 스크립트
"""

import os
import sys
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# 현재 디렉터리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_utils import create_upload_folder, generate_unique_filename

def test_file_upload():
    """파일 업로드 테스트"""
    print("=== 파일 업로드 테스트 시작 ===")
    
    # 1. 업로드 폴더 생성 테스트
    print("1. 업로드 폴더 생성...")
    try:
        create_upload_folder()
        print("✅ 업로드 폴더 생성 성공")
    except Exception as e:
        print(f"❌ 업로드 폴더 생성 실패: {e}")
        return
    
    # 2. 테스트 파일 생성
    print("2. 테스트 파일 생성...")
    test_content = "This is a test file for upload testing."
    test_filename = "test.txt"
    
    try:
        with open(test_filename, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✅ 테스트 파일 생성 성공: {test_filename}")
    except Exception as e:
        print(f"❌ 테스트 파일 생성 실패: {e}")
        return
    
    # 3. 파일명 생성 테스트
    print("3. 고유 파일명 생성...")
    try:
        unique_filename = generate_unique_filename(test_filename)
        print(f"✅ 고유 파일명 생성: {unique_filename}")
    except Exception as e:
        print(f"❌ 고유 파일명 생성 실패: {e}")
        return
    
    # 4. 파일 복사 테스트
    print("4. 파일 복사 테스트...")
    try:
        import shutil
        upload_path = os.path.join('uploads', unique_filename)
        shutil.copy2(test_filename, upload_path)
        print(f"✅ 파일 복사 성공: {upload_path}")
        
        # 파일 존재 확인
        if os.path.exists(upload_path):
            file_size = os.path.getsize(upload_path)
            print(f"✅ 파일 존재 확인: {file_size} bytes")
        else:
            print("❌ 파일이 존재하지 않음")
            
    except Exception as e:
        print(f"❌ 파일 복사 실패: {e}")
        return
    
    # 5. 정리
    print("5. 정리...")
    try:
        os.remove(test_filename)
        print("✅ 테스트 파일 삭제 완료")
    except:
        pass
    
    print("=== 파일 업로드 테스트 완료 ===")

if __name__ == '__main__':
    test_file_upload() 