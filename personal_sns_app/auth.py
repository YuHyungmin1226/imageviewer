from typing import Dict, Optional
from datetime import datetime
import streamlit as st
from utils import hash_password, safe_load_json, safe_save_json
from config import Config

class AuthManager:
    """인증 관리 클래스"""
    
    def __init__(self, users_path: str, session_path: str):
        self.users_path = users_path
        self.session_path = session_path
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, str]:
        """사용자 데이터 로드"""
        return safe_load_json(self.users_path, {"admin": hash_password("admin123")})
    
    def validate_login(self, username: str, password: str) -> bool:
        """로그인 검증"""
        if not username or not password:
            return False
        if username not in self.users:
            return False
        return self.users[username] == hash_password(password)
    
    def register_user(self, username: str, password: str) -> bool:
        """사용자 등록"""
        if not username or not password:
            return False
        if username in self.users:
            return False
        
        password_hash = hash_password(password)
        self.users[username] = password_hash
        safe_save_json(self.users_path, self.users)
        return True
    
    def change_password(self, username: str, new_password: str) -> bool:
        """비밀번호 변경"""
        if not username or not new_password:
            return False
        if username not in self.users:
            return False
        
        new_password_hash = hash_password(new_password)
        self.users[username] = new_password_hash
        safe_save_json(self.users_path, self.users)
        return True
    
    def delete_user(self, username: str) -> bool:
        """사용자 삭제"""
        if username not in self.users or username == "admin":
            return False
        
        del self.users[username]
        safe_save_json(self.users_path, self.users)
        return True
    
    def save_session(self, username: str, password_changed: bool = True) -> None:
        """세션 정보 저장"""
        session_data = {
            "logged_in": True,
            "username": username,
            "password_changed": password_changed,
            "login_time": datetime.now().isoformat()
        }
        safe_save_json(self.session_path, session_data)
    
    def load_session(self) -> Optional[Dict]:
        """세션 정보 로드"""
        return safe_load_json(self.session_path, {})
    
    def clear_session(self) -> None:
        """세션 정보 초기화"""
        safe_save_json(self.session_path, {})
    
    def get_all_users(self) -> Dict[str, str]:
        """모든 사용자 반환"""
        return self.users.copy()
    
    def is_admin(self, username: str) -> bool:
        """관리자 여부 확인"""
        return username == "admin"
    
    def is_default_admin_password(self, username: str, password: str) -> bool:
        """기본 관리자 비밀번호 여부 확인"""
        return username == "admin" and password == "admin123" 