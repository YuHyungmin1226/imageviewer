from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import os
import streamlit as st
from utils import safe_load_json, safe_save_json, validate_file_type, validate_file_size, format_file_size, sanitize_filename, create_upload_directory
from config import Config

class PostManager:
    """게시글 관리 클래스"""
    
    def __init__(self, posts_path: str, uploads_dir: str):
        self.posts_path = posts_path
        self.uploads_dir = uploads_dir
        self.posts = self._load_posts()
        create_upload_directory()
    
    def _load_posts(self) -> List[Dict]:
        """게시글 데이터 로드"""
        return safe_load_json(self.posts_path, [])
    
    def create_post(self, content: str, author: str, files: List[Any] = None) -> Optional[Dict]:
        """새 게시글 생성"""
        if not content.strip() or not author:
            return None
        
        if len(content) > Config.MAX_POST_LENGTH:
            st.error(f"게시글은 {Config.MAX_POST_LENGTH}자를 초과할 수 없습니다.")
            return None
        
        uploaded_files = []
        if files:
            uploaded_files = self._process_uploaded_files(files)
        
        new_post = {
            "id": str(uuid.uuid4()),
            "content": content.strip(),
            "author": author,
            "files": uploaded_files,
            "created_at": datetime.now().isoformat(),
            "comments": [],
            "public": False
        }
        
        self.posts.insert(0, new_post)
        safe_save_json(self.posts_path, self.posts)
        return new_post
    
    def _process_uploaded_files(self, files: List[Any]) -> List[Dict]:
        """업로드된 파일 처리"""
        uploaded_files = []
        
        for file in files:
            try:
                # 파일 타입 검증
                if not validate_file_type(file.name):
                    st.warning(f"지원하지 않는 파일 타입입니다: {file.name}")
                    continue
                
                # 파일 크기 검증
                if not validate_file_size(file.size):
                    st.warning(f"파일 크기가 너무 큽니다: {file.name} ({format_file_size(file.size)})")
                    continue
                
                # 파일명 정리
                safe_name = sanitize_filename(file.name)
                file_id = f"{uuid.uuid4().hex}_{safe_name}"
                file_path = os.path.join(self.uploads_dir, file_id)
                
                # 파일 저장
                with open(file_path, "wb") as f_out:
                    f_out.write(file.read())
                
                uploaded_files.append({
                    "original_name": file.name,
                    "saved_name": file_id,
                    "file_type": file.type,
                    "size": file.size
                })
                
            except Exception as e:
                st.warning(f"파일 업로드 실패: {file.name} - {e}")
        
        return uploaded_files
    
    def get_posts_for_user(self, username: str, is_admin: bool = False) -> List[Dict]:
        """사용자에게 보여줄 게시글 목록"""
        if is_admin:
            return self.posts  # 관리자는 모든 게시글 볼 수 있음
        
        # 본인 글과 공개된 글만
        return [post for post in self.posts 
                if post["author"] == username or post.get("public", False)]
    
    def update_post(self, post_id: str, update_data: Dict) -> bool:
        """게시글 업데이트"""
        for post in self.posts:
            if post["id"] == post_id:
                post.update(update_data)
                safe_save_json(self.posts_path, self.posts)
                return True
        return False
    
    def delete_post(self, post_id: str, username: str, is_admin: bool = False) -> bool:
        """게시글 삭제"""
        for i, post in enumerate(self.posts):
            if post["id"] == post_id:
                # 권한 확인
                if not is_admin and post["author"] != username:
                    return False
                
                # 첨부 파일 삭제
                self._delete_post_files(post.get("files", []))
                
                # 게시글 삭제
                del self.posts[i]
                safe_save_json(self.posts_path, self.posts)
                return True
        return False
    
    def _delete_post_files(self, files: List[Dict]) -> None:
        """게시글의 첨부 파일들 삭제"""
        for file in files:
            file_path = os.path.join(self.uploads_dir, file["saved_name"])
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                # Streamlit Cloud에서는 파일 삭제가 제한적
                pass
    

    def add_comment(self, post_id: str, username: str, content: str) -> bool:
        """댓글 추가"""
        if not content.strip():
            return False
        
        for post in self.posts:
            if post["id"] == post_id:
                comments = post.setdefault("comments", [])
                comments.append({
                    "author": username,
                    "content": content.strip(),
                    "timestamp": datetime.now().isoformat()
                })
                safe_save_json(self.posts_path, self.posts)
                return True
        return False
    
    def toggle_public(self, post_id: str, username: str) -> bool:
        """공개/비공개 토글"""
        for post in self.posts:
            if post["id"] == post_id and post["author"] == username:
                post["public"] = not post.get("public", False)
                safe_save_json(self.posts_path, self.posts)
                return True
        return False
    
    def delete_user_posts(self, username: str) -> int:
        """사용자의 모든 게시글 삭제"""
        deleted_count = 0
        posts_to_delete = []
        
        for post in self.posts:
            if post["author"] == username:
                posts_to_delete.append(post)
                deleted_count += 1
        
        for post in posts_to_delete:
            self._delete_post_files(post.get("files", []))
            self.posts.remove(post)
        
        if deleted_count > 0:
            safe_save_json(self.posts_path, self.posts)
        
        return deleted_count 