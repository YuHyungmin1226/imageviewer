import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, send_file, Response
from werkzeug.utils import secure_filename
import mimetypes
import re
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
POSTS_PATH = os.path.join(BASE_DIR, 'posts.json')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['MAX_FILES'] = 10

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'},
    'audio': {'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'}
}

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

load_dotenv()

def allowed_file(filename):
    """파일 확장자가 허용된 것인지 확인"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    for category in ALLOWED_EXTENSIONS.values():
        if ext in category:
            return True
    return False

def get_file_type(filename):
    """파일 타입을 반환"""
    if '.' not in filename:
        return 'unknown'
    ext = filename.rsplit('.', 1)[1].lower()
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return 'unknown'

def load_posts():
    """게시물 데이터 로드"""
    try:
        with open(POSTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_posts(posts):
    """게시물 데이터 저장"""
    with open(POSTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def extract_url_preview(url):
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.find('meta', property='og:title') or soup.title
        image = soup.find('meta', property='og:image')
        desc = soup.find('meta', property='og:description')
        return {
            'url': url,
            'title': title['content'] if title and title.has_attr('content') else (title.string if title else url),
            'image': image['content'] if image and image.has_attr('content') else '',
            'desc': desc['content'] if desc and desc.has_attr('content') else ''
        }
    except Exception:
        return None

def find_first_url(text):
    match = re.search(r'(https?://[\w\-._~:/?#\[\]@!$&\'()*+,;=%]+)', text)
    return match.group(1) if match else None

@app.route('/')
def index():
    """메인 페이지"""
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/post', methods=['POST'])
def create_post():
    """새 게시물 생성"""
    try:
        content = request.form.get('content', '').strip()
        author = request.form.get('author', '').strip() or '사용자'
        if not content:
            return jsonify({'error': '내용을 입력해주세요.'}), 400
        
        # 파일 업로드 처리
        uploaded_files = []
        files = request.files.getlist('files')
        
        if len(files) > app.config['MAX_FILES']:
            return jsonify({'error': f'최대 {app.config["MAX_FILES"]}개의 파일만 업로드할 수 있습니다.'}), 400
        
        for file in files:
            if file and file.filename:
                if not allowed_file(file.filename):
                    return jsonify({'error': f'지원하지 않는 파일 형식입니다: {file.filename}'}), 400
                
                # 안전한 파일명 생성
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                file.save(file_path)
                
                # 파일 정보 저장
                file_info = {
                    'original_name': filename,
                    'saved_name': unique_filename,
                    'file_type': get_file_type(filename),
                    'size': os.path.getsize(file_path)
                }
                uploaded_files.append(file_info)
        
        # 링크 미리보기 추출
        url = find_first_url(content)
        link_preview = extract_url_preview(url) if url else None
        
        # 새 게시물 생성
        new_post = {
            'id': str(uuid.uuid4()),
            'content': content,
            'author': author,
            'files': uploaded_files,
            'timestamp': datetime.now().isoformat(),
            'likes': 0,
            'replies': [],
            'link_preview': link_preview
        }
        
        # 게시물 저장
        posts = load_posts()
        posts.insert(0, new_post)  # 최신 게시물을 맨 위에
        save_posts(posts)
        
        return jsonify({'success': True, 'post': new_post})
    
    except Exception as e:
        return jsonify({'error': f'게시물 생성 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "파일을 찾을 수 없습니다.", 404
    range_header = request.headers.get('Range', None)
    if not range_header:
        mime_type, _ = mimetypes.guess_type(file_path)
        return send_file(file_path, mimetype=mime_type or 'application/octet-stream')
    size = os.path.getsize(file_path)
    byte1, byte2 = 0, None
    m = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if m:
        g = m.groups()
        byte1 = int(g[0])
        if g[1]:
            byte2 = int(g[1])
    length = size - byte1
    with open(file_path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length if byte2 is None else byte2 - byte1 + 1)
    mime_type, _ = mimetypes.guess_type(file_path)
    rv = Response(data, 206, mimetype=mime_type or 'application/octet-stream', direct_passthrough=True)
    rv.headers.add('Content-Range', f'bytes {byte1}-{byte1 + len(data) - 1}/{size}')
    rv.headers.add('Accept-Ranges', 'bytes')
    return rv

@app.route('/like/<post_id>', methods=['POST'])
def like_post(post_id):
    """게시물 좋아요"""
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            post['likes'] += 1
            save_posts(posts)
            return jsonify({'success': True, 'likes': post['likes']})
    return jsonify({'error': '게시물을 찾을 수 없습니다.'}), 404

@app.route('/reply/<post_id>', methods=['POST'])
def reply_post(post_id):
    """게시물에 답글 작성"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        author = data.get('author', '').strip() or '사용자'
        if not content:
            return jsonify({'error': '답글 내용을 입력해주세요.'}), 400
        
        posts = load_posts()
        for post in posts:
            if post['id'] == post_id:
                reply = {
                    'id': str(uuid.uuid4()),
                    'content': content,
                    'author': author,
                    'timestamp': datetime.now().isoformat()
                }
                post['replies'].append(reply)
                save_posts(posts)
                return jsonify({'success': True, 'reply': reply})
        
        return jsonify({'error': '게시물을 찾을 수 없습니다.'}), 404
    
    except Exception as e:
        return jsonify({'error': f'답글 작성 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    posts = load_posts()
    new_posts = []
    deleted = False
    for post in posts:
        if post['id'] == post_id:
            # 업로드된 파일도 함께 삭제
            for file in post.get('files', []):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file['saved_name'])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
            deleted = True
            continue
        new_posts.append(post)
    if deleted:
        save_posts(new_posts)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': '게시물을 찾을 수 없습니다.'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001) 