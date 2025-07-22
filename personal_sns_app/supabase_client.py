from typing import List, Dict, Optional, Any
from datetime import datetime
import streamlit as st
from config import Config

class SupabaseClient:
    """Supabase 클라이언트 래퍼 클래스"""
    
    def __init__(self):
        self.client = None
        self.is_connected = False
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Supabase 클라이언트 초기화"""
        try:
            from supabase import create_client
            
            # Streamlit Secrets에서 설정 가져오기
            if hasattr(st, 'secrets') and 'supabase_url' in st.secrets and 'supabase_key' in st.secrets:
                supabase_url = st.secrets.supabase_url
                supabase_key = st.secrets.supabase_key
                self.client = create_client(supabase_url, supabase_key)
                self.is_connected = True
            elif Config.is_supabase_configured():
                # 환경변수에서 설정 가져오기
                self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                self.is_connected = True
            else:
                self.is_connected = False
                
        except ImportError:
            # supabase 패키지가 설치되지 않은 경우
            self.is_connected = False
        except Exception as e:
            st.warning(f"Supabase 연결 실패: {e}")
            self.is_connected = False
    
    def is_available(self) -> bool:
        """Supabase 사용 가능 여부"""
        return self.is_connected and self.client is not None
    
    # 게시글 관련 메서드
    def load_posts(self) -> List[Dict]:
        """게시글 목록 로드"""
        if not self.is_available():
            return []
        
        try:
            response = self.client.table('posts').select('*').order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            st.warning(f"Supabase 게시글 로드 실패: {e}")
            return []
    
    def save_post(self, post_data: Dict) -> bool:
        """게시글 저장"""
        if not self.is_available():
            return False
        
        try:
            self.client.table('posts').insert(post_data).execute()
            return True
        except Exception as e:
            st.warning(f"Supabase 게시글 저장 실패: {e}")
            return False
    
    def update_post(self, post_id: str, update_data: Dict) -> bool:
        """게시글 업데이트"""
        if not self.is_available():
            return False
        
        try:
            self.client.table('posts').update(update_data).eq('id', post_id).execute()
            return True
        except Exception as e:
            st.warning(f"Supabase 게시글 업데이트 실패: {e}")
            return False
    
    def delete_post(self, post_id: str) -> bool:
        """게시글 삭제"""
        if not self.is_available():
            return False
        
        try:
            self.client.table('posts').delete().eq('id', post_id).execute()
            return True
        except Exception as e:
            st.warning(f"Supabase 게시글 삭제 실패: {e}")
            return False
    
    # 사용자 관련 메서드
    def load_users(self) -> Dict[str, str]:
        """사용자 목록 로드"""
        if not self.is_available():
            return {"admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"}
        
        try:
            response = self.client.table('users').select('*').execute()
            users = {}
            for user in response.data:
                users[user['username']] = user['password_hash']
            return users
        except Exception as e:
            st.warning(f"Supabase 사용자 로드 실패: {e}")
            return {"admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"}
    
    def save_user(self, username: str, password_hash: str) -> bool:
        """사용자 저장"""
        if not self.is_available():
            return False
        
        try:
            self.client.table('users').insert({
                'username': username,
                'password_hash': password_hash,
                'created_at': datetime.now().isoformat()
            }).execute()
            return True
        except Exception as e:
            st.warning(f"Supabase 사용자 저장 실패: {e}")
            return False
    
    def update_user(self, username: str, password_hash: str) -> bool:
        """사용자 업데이트"""
        if not self.is_available():
            return False
        
        try:
            self.client.table('users').update({
                'password_hash': password_hash,
                'updated_at': datetime.now().isoformat()
            }).eq('username', username).execute()
            return True
        except Exception as e:
            st.warning(f"Supabase 사용자 업데이트 실패: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """사용자 삭제"""
        if not self.is_available():
            return False
        
        try:
            # 해당 사용자의 게시글도 함께 삭제
            self.client.table('posts').delete().eq('author', username).execute()
            # 사용자 삭제
            self.client.table('users').delete().eq('username', username).execute()
            return True
        except Exception as e:
            st.warning(f"Supabase 사용자 삭제 실패: {e}")
            return False
    
    def get_user_list(self) -> List[Dict]:
        """사용자 목록 조회 (관리자용)"""
        if not self.is_available():
            return []
        
        try:
            response = self.client.table('users').select('username, created_at').execute()
            return response.data
        except Exception as e:
            st.error(f"사용자 목록 로드 오류: {e}")
            return [] 