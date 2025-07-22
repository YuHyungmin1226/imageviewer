import uuid
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import streamlit as st
from utils import safe_load_json, safe_save_json

class SessionManager:
    """보안이 강화된 세션 관리 클래스"""
    
    def __init__(self, session_path: str):
        self.session_path = session_path
        self.sessions = self._load_sessions()
        self.session_timeout_hours = 24  # 24시간 후 세션 만료
    
    def _load_sessions(self) -> Dict:
        """세션 데이터 로드"""
        return safe_load_json(self.session_path, {})
    
    def _save_sessions(self) -> None:
        """세션 데이터 저장"""
        safe_save_json(self.session_path, self.sessions)
    
    def create_session(self, username: str, password_changed: bool = True) -> str:
        """새 세션 생성"""
        # 기존 세션 무효화 (동시 로그인 방지)
        self._invalidate_user_sessions(username)
        
        # 고유한 세션 ID 생성
        session_id = str(uuid.uuid4())
        
        # 세션 데이터 생성
        session_data = {
            "session_id": session_id,
            "username": username,
            "password_changed": password_changed,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "ip_address": self._get_client_ip(),
            "user_agent": self._get_user_agent()
        }
        
        # 세션 저장
        self.sessions[session_id] = session_data
        self._save_sessions()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """세션 유효성 검증"""
        if not session_id or session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # 세션 만료 확인
        if self._is_session_expired(session):
            self._remove_session(session_id)
            return None
        
        # IP 주소 변경 확인 (선택적)
        current_ip = self._get_client_ip()
        if session.get("ip_address") != current_ip:
            st.warning("보안을 위해 다시 로그인해주세요.")
            self._remove_session(session_id)
            return None
        
        # 마지막 활동 시간 업데이트
        session["last_activity"] = datetime.now().isoformat()
        self._save_sessions()
        
        return session
    
    def _is_session_expired(self, session: Dict) -> bool:
        """세션 만료 확인"""
        try:
            last_activity = datetime.fromisoformat(session["last_activity"])
            now = datetime.now()
            return (now - last_activity) > timedelta(hours=self.session_timeout_hours)
        except:
            return True
    
    def _invalidate_user_sessions(self, username: str) -> None:
        """사용자의 모든 세션 무효화"""
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            if session.get("username") == username:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self._remove_session(session_id)
    
    def _remove_session(self, session_id: str) -> None:
        """세션 제거"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
    
    def logout(self, session_id: str) -> None:
        """로그아웃"""
        self._remove_session(session_id)
    
    def _get_client_ip(self) -> str:
        """클라이언트 IP 주소 가져오기"""
        try:
            # Streamlit에서 IP 주소 가져오기 (실제 환경에서는 더 정확한 방법 필요)
            return "unknown"
        except:
            return "unknown"
    
    def _get_user_agent(self) -> str:
        """사용자 에이전트 가져오기"""
        try:
            # Streamlit에서 User-Agent 가져오기
            return "streamlit-app"
        except:
            return "unknown"
    
    def cleanup_expired_sessions(self) -> int:
        """만료된 세션 정리"""
        expired_count = 0
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                sessions_to_remove.append(session_id)
                expired_count += 1
        
        for session_id in sessions_to_remove:
            self._remove_session(session_id)
        
        return expired_count
    
    def get_active_sessions_count(self) -> int:
        """활성 세션 수 반환"""
        return len(self.sessions)
    
    def get_user_sessions(self, username: str) -> Dict:
        """사용자의 활성 세션 목록"""
        user_sessions = {}
        for session_id, session in self.sessions.items():
            if session.get("username") == username:
                user_sessions[session_id] = session
        return user_sessions 