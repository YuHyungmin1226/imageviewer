import hashlib
import json
import os
from typing import Any, Dict, List
import streamlit as st
from config import Config

def hash_password(password: str) -> str:
    """비밀번호를 SHA-256으로 해싱"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def safe_load_json(path: str, default: Any) -> Any:
    """JSON 파일을 안전하게 로드"""
    try:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default

def safe_save_json(path: str, data: Any) -> None:
    """JSON 파일을 안전하게 저장"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"파일 저장 오류: {e}")

def validate_file_type(filename: str) -> bool:
    """파일 타입 검증"""
    if not filename:
        return False
    file_ext = filename.split('.')[-1].lower()
    return file_ext in Config.get_allowed_file_types()

def validate_file_size(file_size: int) -> bool:
    """파일 크기 검증"""
    return file_size <= Config.MAX_FILE_SIZE

def format_file_size(size_bytes: int) -> str:
    """파일 크기를 읽기 쉬운 형태로 변환"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """파일명 정리 (특수문자 제거)"""
    import re
    # 특수문자 제거, 공백을 언더스코어로 변경
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    sanitized = re.sub(r'[-\s]+', '_', sanitized)
    return sanitized.strip('_')

def create_upload_directory() -> str:
    """업로드 디렉토리 생성"""
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), Config.UPLOAD_FOLDER)
    try:
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    except Exception:
        # Streamlit Cloud에서는 파일 시스템 쓰기 권한이 제한적
        return upload_dir 