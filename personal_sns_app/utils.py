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

def sanitize_filename(filename: str) -> str:
    """파일명 정리 (특수문자 제거)"""
    import re
    # 특수문자 제거, 공백을 언더스코어로 변경
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    sanitized = re.sub(r'[-\s]+', '_', sanitized)
    return sanitized.strip('_') 