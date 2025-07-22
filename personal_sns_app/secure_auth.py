import hashlib
import secrets
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import streamlit as st
from utils import safe_load_json, safe_save_json
from session_manager import SessionManager

class SecureAuth:
    """보안이 강화된 인증 시스템"""
    
    def __init__(self, users_path: str, session_path: str, use_supabase: bool = False, supabase_client=None):
        self.users_path = users_path
        self.session_manager = SessionManager(session_path)
        self.users = self._load_users()
        self.login_attempts = {}  # 로그인 시도 기록
        self.max_login_attempts = 5  # 최대 로그인 시도 횟수
        self.lockout_duration = 15  # 계정 잠금 시간 (분)
        self.use_supabase = use_supabase
        self.supabase = supabase_client
    
    def _load_users(self) -> Dict[str, str]:
        """사용자 데이터 로드"""
        return safe_load_json(self.users_path, {"admin": self._hash_password("admin123")})
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def _is_account_locked(self, username: str) -> bool:
        """계정 잠금 상태 확인"""
        if username not in self.login_attempts:
            return False
        
        attempts = self.login_attempts[username]
        if attempts['count'] >= self.max_login_attempts:
            lockout_time = datetime.fromisoformat(attempts['last_attempt'])
            if datetime.now() - lockout_time < timedelta(minutes=self.lockout_duration):
                return True
            else:
                # 잠금 시간이 지나면 초기화
                del self.login_attempts[username]
        
        return False
    
    def _record_login_attempt(self, username: str, success: bool) -> None:
        """로그인 시도 기록"""
        if username not in self.login_attempts:
            self.login_attempts[username] = {'count': 0, 'last_attempt': ''}
        
        if success:
            # 성공 시 기록 초기화
            del self.login_attempts[username]
        else:
            # 실패 시 기록 업데이트
            self.login_attempts[username]['count'] += 1
            self.login_attempts[username]['last_attempt'] = datetime.now().isoformat()
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[str], str]:
        """로그인 처리"""
        # 입력 검증
        if not username or not password:
            return False, None, "사용자명과 비밀번호를 모두 입력해주세요."
        
        # 계정 잠금 확인
        if self._is_account_locked(username):
            remaining_time = self._get_remaining_lockout_time(username)
            return False, None, f"계정이 잠겼습니다. {remaining_time}분 후에 다시 시도해주세요."
        
        # 사용자 존재 확인
        if username not in self.users:
            self._record_login_attempt(username, False)
            return False, None, "존재하지 않는 사용자명입니다."
        
        # 비밀번호 검증
        if self.users[username] != self._hash_password(password):
            self._record_login_attempt(username, False)
            return False, None, "비밀번호가 올바르지 않습니다."
        
        # 로그인 성공
        self._record_login_attempt(username, True)
        
        # 세션 생성
        password_changed = not (username == "admin" and password == "admin123")
        session_id = self.session_manager.create_session(username, password_changed)
        
        return True, session_id, "로그인 성공!"
    
    def _get_remaining_lockout_time(self, username: str) -> int:
        """잠금 해제까지 남은 시간 (분)"""
        if username not in self.login_attempts:
            return 0
        
        last_attempt = datetime.fromisoformat(self.login_attempts[username]['last_attempt'])
        elapsed = datetime.now() - last_attempt
        remaining = timedelta(minutes=self.lockout_duration) - elapsed
        return max(0, int(remaining.total_seconds() / 60))
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """사용자 등록"""
        if not username or not password:
            return False, "사용자명과 비밀번호를 모두 입력해주세요."
        if len(username) < 3:
            return False, "사용자명은 3자 이상이어야 합니다."
        if len(password) < 6:
            return False, "비밀번호는 6자 이상이어야 합니다."
        if username in self.users:
            return False, "이미 존재하는 사용자명입니다."
        password_hash = self._hash_password(password)
        self.users[username] = password_hash
        safe_save_json(self.users_path, self.users)
        # Supabase에도 저장
        if self.use_supabase and self.supabase is not None:
            try:
                self.supabase.table('users').insert({
                    'username': username,
                    'password_hash': password_hash,
                    'created_at': datetime.now().isoformat()
                }).execute()
            except Exception as e:
                st.warning(f"Supabase 사용자 저장 실패: {e}")
        return True, "회원가입이 완료되었습니다!"
    
    def change_password(self, username: str, current_password: str, new_password: str) -> Tuple[bool, str]:
        if self.users[username] != self._hash_password(current_password):
            return False, "현재 비밀번호가 올바르지 않습니다."
        if len(new_password) < 6:
            return False, "새 비밀번호는 6자 이상이어야 합니다."
        if new_password == current_password:
            return False, "새 비밀번호는 기존 비밀번호와 달라야 합니다."
        new_password_hash = self._hash_password(new_password)
        self.users[username] = new_password_hash
        safe_save_json(self.users_path, self.users)
        # Supabase에도 비밀번호 변경
        if self.use_supabase and self.supabase is not None:
            try:
                self.supabase.table('users').update({
                    'password_hash': new_password_hash,
                    'updated_at': datetime.now().isoformat()
                }).eq('username', username).execute()
            except Exception as e:
                st.warning(f"Supabase 비밀번호 변경 실패: {e}")
        self.session_manager._invalidate_user_sessions(username)
        return True, "비밀번호가 성공적으로 변경되었습니다!"
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """세션 유효성 검증"""
        return self.session_manager.validate_session(session_id)
    
    def logout(self, session_id: str) -> None:
        """로그아웃"""
        self.session_manager.logout(session_id)
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """사용자 정보 조회"""
        if username not in self.users:
            return None
        
        return {
            "username": username,
            "created_at": "N/A",  # 실제로는 생성 시간 저장 필요
            "last_login": "N/A"   # 실제로는 마지막 로그인 시간 저장 필요
        }
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        if username not in self.users or username == "admin":
            return False, "삭제할 수 없는 사용자입니다."
        del self.users[username]
        safe_save_json(self.users_path, self.users)
        if self.use_supabase and self.supabase is not None:
            try:
                self.supabase.table('users').delete().eq('username', username).execute()
            except Exception as e:
                st.warning(f"Supabase 사용자 삭제 실패: {e}")
        self.session_manager._invalidate_user_sessions(username)
        return True, f"사용자 '{username}'가 삭제되었습니다."
    
    def get_login_attempts_info(self, username: str) -> Dict:
        """로그인 시도 정보 조회"""
        if username not in self.login_attempts:
            return {"count": 0, "locked": False, "remaining_time": 0}
        
        attempts = self.login_attempts[username]
        locked = self._is_account_locked(username)
        remaining_time = self._get_remaining_lockout_time(username) if locked else 0
        
        return {
            "count": attempts['count'],
            "locked": locked,
            "remaining_time": remaining_time
        } 