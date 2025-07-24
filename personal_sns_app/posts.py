from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import os
import streamlit as st
from utils import safe_load_json, safe_save_json, validate_file_type, validate_file_size, format_file_size, sanitize_filename, create_upload_directory
from config import Config

class PostManager:
    """게시글 관리 클래스"""
    
    def __init__(self, posts_path: str):
        self.posts_path = posts_path
        self.posts = self._load_posts()
    
    def _load_posts(self) -> List[Dict]:
        """게시글 데이터 로드"""
        return safe_load_json(self.posts_path, [])
    
    def create_post(self, content: str, author: str) -> Optional[Dict]:
        """새 게시글 생성 (파일 첨부 없음)"""
        if not content.strip() or not author:
            return None
        if len(content) > Config.MAX_POST_LENGTH:
            st.error(f"게시글은 {Config.MAX_POST_LENGTH}자를 초과할 수 없습니다.")
            return None
        new_post = {
            "id": str(uuid.uuid4()),
            "content": content.strip(),
            "author": author,
            "created_at": datetime.now().isoformat(),
            "comments": [],
            "public": False
        }
        self.posts.insert(0, new_post)
        safe_save_json(self.posts_path, self.posts)
        return new_post
    
    def get_posts_for_user(self, username: str, is_admin: bool = False) -> List[Dict]:
        """사용자에게 보여줄 게시글 목록"""
        if is_admin:
            return self.posts  # 관리자는 모든 게시글 볼 수 있음
        return [post for post in self.posts if post["author"] == username or post.get("public", False)]
    
    def update_post(self, post_id: str, update_data: Dict) -> bool:
        """게시글 업데이트"""
        for post in self.posts:
            if post["id"] == post_id:
                post.update(update_data)
                safe_save_json(self.posts_path, self.posts)
                return True
        return False
    
    def delete_post(self, post_id: str, username: str, is_admin: bool = False) -> bool:
        """게시글 삭제 (첨부파일 삭제 없음)"""
        for i, post in enumerate(self.posts):
            if post["id"] == post_id:
                if not is_admin and post["author"] != username:
                    return False
                del self.posts[i]
                safe_save_json(self.posts_path, self.posts)
                return True
        return False
    

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
            self.posts.remove(post)
        
        if deleted_count > 0:
            safe_save_json(self.posts_path, self.posts)
        
        return deleted_count 