import streamlit as st
import os
import json
from datetime import datetime
import uuid
from PIL import Image
import io
import hashlib
from secure_auth import SecureAuth
from session_manager import SessionManager

# Supabase 연동
USE_SUPABASE = False
supabase = None

try:
    from supabase import create_client # type: ignore
    # Streamlit Secrets에서 Supabase 설정 가져오기
    if hasattr(st, 'secrets') and 'supabase_url' in st.secrets and 'supabase_key' in st.secrets:
        supabase_url = st.secrets.supabase_url
        supabase_key = st.secrets.supabase_key
        supabase = create_client(supabase_url, supabase_key)
        USE_SUPABASE = True
    else:
        # Supabase 설정이 없으면 로컬 모드로 실행
        USE_SUPABASE = False
        supabase = None
except ImportError:
    # supabase 패키지가 설치되지 않은 경우
    USE_SUPABASE = False
    supabase = None
except Exception as e:
    # Supabase 연결 실패 시 로컬 모드로 실행
    USE_SUPABASE = False
    supabase = None

# 로컬 파일 시스템 (백업용)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_PATH = os.path.join(BASE_DIR, "posts.json")
USERS_PATH = os.path.join(BASE_DIR, "users.json")
SESSION_PATH = os.path.join(BASE_DIR, "session.json")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Streamlit Cloud에서는 읽기 전용이므로 업로드 디렉토리 생성 시도
try:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
except Exception:
    # Streamlit Cloud에서는 파일 시스템 쓰기 권한이 제한적
    pass

# Supabase 데이터베이스 함수들
def supabase_load_posts():
    if not USE_SUPABASE or supabase is None:
        return []
    try:
        response = supabase.table('posts').select('*').order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.warning(f"Supabase 게시글 로드 실패: {e}")
        return []

def supabase_save_post(post_data):
    if not USE_SUPABASE or supabase is None:
        return False
    try:
        supabase.table('posts').insert(post_data).execute()
        return True
    except Exception as e:
        st.warning(f"Supabase 게시글 저장 실패: {e}")
        return False

def supabase_update_post(post_id, update_data):
    if not USE_SUPABASE or supabase is None:
        return False
    try:
        supabase.table('posts').update(update_data).eq('id', post_id).execute()
        return True
    except Exception as e:
        st.warning(f"Supabase 게시글 업데이트 실패: {e}")
        return False

def supabase_delete_post(post_id):
    if not USE_SUPABASE or supabase is None:
        return False
    try:
        supabase.table('posts').delete().eq('id', post_id).execute()
        return True
    except Exception as e:
        st.warning(f"Supabase 게시글 삭제 실패: {e}")
        return False

def supabase_load_users():
    if not USE_SUPABASE or supabase is None:
        return {"admin": hash_password("admin123")}
    try:
        response = supabase.table('users').select('*').execute()
        users = {}
        for user in response.data:
            users[user['username']] = user['password_hash']
        return users
    except Exception as e:
        st.warning(f"Supabase 사용자 로드 실패: {e}")
        return {"admin": hash_password("admin123")}

def supabase_save_user(username, password_hash):
    if not USE_SUPABASE or supabase is None:
        return False
    try:
        supabase.table('users').insert({
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.warning(f"Supabase 사용자 저장 실패: {e}")
        return False

def supabase_update_user(username, password_hash):
    if not USE_SUPABASE or supabase is None:
        return False
    try:
        supabase.table('users').update({
            'password_hash': password_hash,
            'updated_at': datetime.now().isoformat()
        }).eq('username', username).execute()
        return True
    except Exception as e:
        st.warning(f"Supabase 사용자 업데이트 실패: {e}")
        return False

# 로컬 파일 시스템 함수들 (백업용)
def safe_load_json(path, default):
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

def safe_save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"파일 저장 오류: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# 보안 인증 시스템 초기화
secure_auth = SecureAuth(USERS_PATH, SESSION_PATH)
session_manager = SessionManager(SESSION_PATH)

# 세션 상태 초기화
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'password_changed' not in st.session_state:
    st.session_state.password_changed = False

# 세션 유효성 검증
if st.session_state.session_id:
    try:
        session_data = session_manager.validate_session(st.session_state.session_id)
        st.write(f"Debug: session_data type={type(session_data)}, value={session_data}")
        if isinstance(session_data, dict):
            st.session_state.logged_in = True
            st.session_state.current_user = session_data.get("username")
            st.session_state.password_changed = session_data.get("password_changed", True)
        else:
            # 세션이 만료되었거나 유효하지 않음
            st.session_state.session_id = None
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.password_changed = False
    except Exception as e:
        st.error(f"세션 검증 중 오류: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# 데이터 로드
try:
    if USE_SUPABASE:
        posts = supabase_load_posts()
        users = supabase_load_users()
    else:
        posts = safe_load_json(POSTS_PATH, [])
        users = safe_load_json(USERS_PATH, {"admin": hash_password("admin123")})
except Exception as e:
    # 데이터 로드 실패 시 기본값 사용
    posts = []
    users = {"admin": hash_password("admin123")}

# CSS 스타일
st.markdown("""
<style>
.stTextInput>div>div>input, .stTextArea textarea, .stFileUploader>label {
    font-size: 18px;
}
.stTextInput, .stTextArea, .stFileUploader, .stButton {
    margin-bottom: 18px;
}
.post-card {
    background: #f5f6fa;
    border-radius: 16px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    padding: 18px 20px 12px 20px;
    margin-bottom: 24px;
}
.post-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}
.post-author {
    font-weight: 600;
    color: #1da1f2;
    margin-right: 8px;
}
.post-time {
    color: #aaa;
    font-size: 13px;
}
.stFileUploader button {
    display: none !important;
}
.stButton > button {
    margin-right: 10px;
}
.button-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

try:
    if not st.session_state.logged_in:
        st.title("로그인")
        auth_mode = st.radio(" ", ["로그인", "회원가입"], index=0, horizontal=True, label_visibility="collapsed")
        if auth_mode == "회원가입":
            st.subheader("새 계정 만들기")
            with st.form("signup_form"):
                new_username = st.text_input("사용자명", key="signup_username")
                new_password = st.text_input("비밀번호", type="password", key="signup_password")
                confirm_password = st.text_input("비밀번호 확인", type="password", key="signup_confirm")
                signup_submitted = st.form_submit_button("회원가입")
                if signup_submitted:
                    if new_password != confirm_password:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        success, message = secure_auth.register_user(new_username, new_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        else:
            st.subheader("로그인")
            with st.form("login_form"):
                username = st.text_input("사용자명", key="login_username")
                password = st.text_input("비밀번호", type="password", key="login_password")
                login_submitted = st.form_submit_button("로그인")
                if login_submitted:
                    try:
                        success, session_id, message = secure_auth.login(username, password)
                        st.write(f"Debug: success={success}, session_id type={type(session_id)}, message={message}")
                        if success:
                            st.session_state.session_id = session_id
                            st.session_state.logged_in = True
                            st.session_state.current_user = username
                            st.session_state.password_changed = not (username == "admin" and password == "admin123")
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    except Exception as e:
                        st.error(f"로그인 처리 중 오류: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
    else:
        # 비밀번호 변경이 필요한 경우 (admin 계정이 기본 비밀번호로 로그인한 경우)
        if st.session_state.current_user == "admin" and not st.session_state.password_changed:
            st.title("비밀번호 변경")
            st.warning("보안을 위해 기본 비밀번호를 변경해주세요.")
            with st.form("change_password_form"):
                current_password = st.text_input("현재 비밀번호", type="password")
                new_password = st.text_input("새 비밀번호", type="password")
                confirm_password = st.text_input("새 비밀번호 확인", type="password")
                change_submitted = st.form_submit_button("비밀번호 변경")
                if change_submitted:
                    if not current_password or not new_password or not confirm_password:
                        st.error("모든 필드를 입력해주세요.")
                    elif current_password != "admin123":
                        st.error("현재 비밀번호가 올바르지 않습니다.")
                    elif new_password != confirm_password:
                        st.error("새 비밀번호가 일치하지 않습니다.")
                    elif new_password == "admin123":
                        st.error("새 비밀번호는 기존 비밀번호와 달라야 합니다.")
                    else:
                        new_password_hash = hash_password(new_password)
                        success, message = secure_auth.change_password("admin", current_password, new_password)
                        if success:
                            st.session_state.password_changed = True
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            if st.button("나중에 변경"):
                st.session_state.password_changed = True
                st.rerun()
        else:
            st.markdown(f"**안녕하세요, {st.session_state.current_user}님!**")
            
            # Admin 전용 사용자 관리 기능
            if st.session_state.current_user == "admin":
                st.markdown("---")
                st.subheader("🔧 관리자 기능")
                
                # 보안 정보
                st.info(f"현재 로그인된 사용자: {st.session_state.current_user}")
                st.info(f"Supabase 사용 여부: {USE_SUPABASE}")
                st.info(f"활성 세션 수: {session_manager.get_active_sessions_count()}")
                
                # 로그인 시도 정보 (관리자용)
                if st.session_state.current_user:
                    try:
                        login_info = secure_auth.get_login_attempts_info(st.session_state.current_user)
                        if isinstance(login_info, dict):
                            if login_info.get('count', 0) > 0:
                                st.warning(f"로그인 시도: {login_info['count']}회")
                            if login_info.get('locked', False):
                                st.error(f"계정 잠금: {login_info['remaining_time']}분 남음")
                    except Exception as e:
                        st.debug(f"로그인 정보 로드 오류: {e}")
                
                # 사용자 목록 표시 (매번 새로 로드)
                if USE_SUPABASE:
                    try:
                        response = supabase.table('users').select('username, created_at').execute()
                        all_users = response.data if response.data else []
                        st.info(f"Supabase에서 로드된 사용자 수: {len(all_users)}")
                    except Exception as e:
                        st.error(f"사용자 목록 로드 오류: {e}")
                        all_users = []
                else:
                    all_users = [{"username": username, "created_at": "N/A"} for username in users.keys()]
                    st.info(f"로컬에서 로드된 사용자 수: {len(all_users)}")
                
                if all_users:
                    st.write("**등록된 사용자 목록:**")
                    for user in all_users:
                        if isinstance(user, dict) and user.get("username") != "admin":  # admin 제외
                            col1, col2, col3 = st.columns([3, 2, 1])
                            with col1:
                                st.write(f"👤 {user.get('username', 'Unknown')}")
                            with col2:
                                created_at = user.get('created_at', 'N/A')
                                if created_at and created_at != 'N/A':
                                    try:
                                        st.write(f"가입일: {created_at[:10]}")
                                    except:
                                        st.write("가입일: N/A")
                                else:
                                    st.write("가입일: N/A")
                            with col3:
                                if st.button(f"삭제", key=f"delete_user_{user.get('username', 'unknown')}", use_container_width=True):
                                    username = user.get('username', '')
                                    if username:
                                        if USE_SUPABASE:
                                            try:
                                                st.info(f"사용자 '{username}' 삭제 중...")
                                                # 해당 사용자의 게시글도 함께 삭제
                                                posts_response = supabase.table('posts').delete().eq('author', username).execute()
                                                st.info(f"게시글 {len(posts_response.data) if posts_response.data else 0}개 삭제됨")
                                                
                                                # 사용자 삭제
                                                user_response = supabase.table('users').delete().eq('username', username).execute()
                                                st.success(f"사용자 '{username}'가 삭제되었습니다.")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"사용자 삭제 오류: {e}")
                                        else:
                                            # 로컬 파일에서 삭제
                                            if username in users:
                                                del users[username]
                                                safe_save_json(USERS_PATH, users)
                                            # 해당 사용자의 게시글도 삭제
                                            posts[:] = [post for post in posts if post.get("author") != username]
                                            safe_save_json(POSTS_PATH, posts)
                                            st.success(f"사용자 '{username}'가 삭제되었습니다.")
                                            st.rerun()
                else:
                    st.write("등록된 사용자가 없습니다.")
                
                st.markdown("---")
            
            if st.button("로그아웃"):
                if st.session_state.session_id:
                    secure_auth.logout(st.session_state.session_id)
                st.session_state.session_id = None
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.password_changed = False
                st.rerun()
            with st.form("post_form", clear_on_submit=True):
                content = st.text_area("내용", placeholder="무엇을 공유하고 싶으신가요?", max_chars=500)
                if "file_upload_open" not in st.session_state:
                    st.session_state.file_upload_open = False
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                with col1:
                    submitted = st.form_submit_button("게시", use_container_width=True)
                with col2:
                    if st.form_submit_button("파일 첨부", use_container_width=True):
                        st.session_state.file_upload_open = not st.session_state.file_upload_open
                with col3:
                    pass
                with col4:
                    pass
                if st.session_state.file_upload_open:
                    files = st.file_uploader(
                        "파일 첨부 (최대 10개, 로컬에서만 저장됨)", 
                        accept_multiple_files=True, 
                        type=["png","jpg","jpeg","gif","bmp","webp","mp4","avi","mov","wmv","flv","webm","mkv","mp3","wav","flac","aac","ogg","m4a"]
                    )
                else:
                    files = []
                if submitted and content.strip():
                    uploaded_files = []
                    for file in files or []:
                        try:
                            file_id = f"{uuid.uuid4().hex}_{file.name}"
                            file_path = os.path.join(UPLOADS_DIR, file_id)
                            with open(file_path, "wb") as f_out:
                                f_out.write(file.read())
                            uploaded_files.append({
                                "original_name": file.name,
                                "saved_name": file_id,
                                "file_type": file.type,
                                "size": os.path.getsize(file_path)
                            })
                        except Exception as e:
                            st.warning(f"파일 업로드 실패 (Streamlit Cloud에서는 파일 저장이 제한됨): {e}")
                            # 파일 업로드 실패해도 게시글은 작성 가능
                    new_post = {
                        "id": str(uuid.uuid4()),
                        "content": content,
                        "author": st.session_state.current_user,
                        "files": uploaded_files,
                        "created_at": datetime.now().isoformat(),
                        "likes": [],
                        "comments": [],
                        "public": False
                    }
                    if USE_SUPABASE:
                        if supabase_save_post(new_post):
                            posts.insert(0, new_post)
                            st.success("게시물이 등록되었습니다!")
                    else:
                        posts.insert(0, new_post)
                        safe_save_json(POSTS_PATH, posts)
                        st.success("게시물이 등록되었습니다!")
            # 포스트 목록 표시 (본인 글과 공개된 글만)
            visible_posts = [post for post in posts if post["author"] == st.session_state.current_user or post.get("public", False)]
            for idx, post in enumerate(visible_posts):
                with st.container():
                    st.markdown('<div class="post-card">', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="post-header">'
                        f'<span class="post-author">{post["author"]}</span>'
                        f'<span class="post-time">{post["created_at"][:16]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div style="font-size:17px; margin-bottom:10px; white-space:pre-wrap">{post["content"]}</div>',
                        unsafe_allow_html=True
                    )
                    for file in post.get("files", []):
                        file_path = os.path.join(UPLOADS_DIR, file["saved_name"])
                        audio_exts = [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"]
                        try:
                            if any(file_path.lower().endswith(ext) for ext in audio_exts):
                                st.audio(file_path)
                            elif "image" in file["file_type"] or file_path.lower().endswith((".png",".jpg",".jpeg",".gif",".bmp",".webp")):
                                with Image.open(file_path) as img:
                                    if hasattr(img, '_getexif') and img._getexif() is not None:
                                        exif = img._getexif()
                                        orientation = exif.get(274)
                                        if orientation == 3:
                                            img = img.rotate(180, expand=True)
                                        elif orientation == 6:
                                            img = img.rotate(270, expand=True)
                                        elif orientation == 8:
                                            img = img.rotate(90, expand=True)
                                    img_byte_arr = io.BytesIO()
                                    img.save(img_byte_arr, format=img.format or 'JPEG')
                                    img_byte_arr.seek(0)
                                    st.image(img_byte_arr, use_container_width=True)
                            elif "video" in file["file_type"] or file_path.lower().endswith((".mp4",".avi",".mov",".wmv",".flv",".webm",".mkv")):
                                st.video(file_path)
                            else:
                                st.write(f"첨부파일: {file['original_name']}")
                        except Exception as e:
                            st.warning(f"첨부파일 표시 실패 (Streamlit Cloud에서는 파일 접근이 제한됨): {e}")
                    col1, col2, col3, col4 = st.columns([1,1,1,1])
                    liked = st.session_state.current_user in post.get("likes",[])
                    like_count = len(post.get("likes", []))
                    like_icon = "❤️" if liked else "🤍"
                    like_text = f"{like_icon} {like_count}" if like_count > 0 else like_icon
                    if col1.button(like_text, key=f"like_{post['id']}", use_container_width=True):
                        if not liked:
                            post.setdefault("likes", []).append(st.session_state.current_user)
                        else:
                            post.setdefault("likes", []).remove(st.session_state.current_user)
                        if USE_SUPABASE:
                            supabase_update_post(post['id'], {"likes": post["likes"]})
                        else:
                            safe_save_json(POSTS_PATH, posts)
                        st.rerun()
                    if col2.button("댓글", key=f"comment_toggle_{post['id']}", use_container_width=True):
                        if "comment_open" not in st.session_state:
                            st.session_state["comment_open"] = {}
                        st.session_state["comment_open"][post['id']] = not st.session_state["comment_open"].get(post['id'], False)
                    if post["author"] == st.session_state.current_user:
                        public_status = post.get("public", False)
                        public_text = "공개" if public_status else "비공개"
                        if col3.button(public_text, key=f"public_{post['id']}", use_container_width=True):
                            post["public"] = not public_status
                            if USE_SUPABASE:
                                supabase_update_post(post['id'], {"public": post["public"]})
                            else:
                                safe_save_json(POSTS_PATH, posts)
                            st.rerun()
                    if post["author"] == st.session_state.current_user or st.session_state.current_user == "admin":
                        if col4.button("삭제", key=f"delete_{post['id']}", use_container_width=True):
                            for file in post.get("files", []):
                                file_path = os.path.join(UPLOADS_DIR, file["saved_name"])
                                try:
                                    if os.path.exists(file_path):
                                        os.remove(file_path)
                                except Exception:
                                    # Streamlit Cloud에서는 파일 삭제가 제한적
                                    pass
                            if USE_SUPABASE:
                                if supabase_delete_post(post['id']):
                                    posts.remove(post)
                            else:
                                posts.remove(post)
                                safe_save_json(POSTS_PATH, posts)
                            st.rerun()
                    if "comment_open" in st.session_state and st.session_state["comment_open"].get(post['id'], False):
                        with st.form(f"comment_form_{post['id']}", clear_on_submit=True):
                            comment_text = st.text_input("댓글을 입력하세요", key=f"comment_input_{post['id']}")
                            comment_submit = st.form_submit_button("댓글 등록")
                            if comment_submit and comment_text.strip():
                                post.setdefault("comments", []).append({
                                    "author": st.session_state.current_user,
                                    "content": comment_text,
                                    "timestamp": datetime.now().isoformat()
                                })
                                if USE_SUPABASE:
                                    supabase_update_post(post['id'], {"comments": post["comments"]})
                                else:
                                    safe_save_json(POSTS_PATH, posts)
                                st.rerun()
                    if post.get("comments", []):
                        for c in post.get("comments", []):
                            st.markdown(f"<div style='margin-left:10px; margin-bottom:4px; font-size:15px;'><b>{c['author']}</b> <span style='color:#aaa;font-size:12px'>{c['timestamp'][:16]}</span><br>{c['content']}</div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
except Exception as e:
    st.error(f"예기치 않은 오류가 발생했습니다: {e}") 