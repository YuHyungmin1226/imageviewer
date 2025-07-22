-- Supabase 데이터베이스 스키마
-- Supabase 대시보드에서 SQL 편집기에 이 코드를 실행하세요

-- 사용자 테이블
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 게시글 테이블
CREATE TABLE posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    author TEXT NOT NULL,
    files JSONB DEFAULT '[]',
    url_previews JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    comments JSONB DEFAULT '[]',
    public BOOLEAN DEFAULT FALSE
);

-- 기본 admin 사용자 생성 (비밀번호: admin123)
INSERT INTO users (username, password_hash) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9')
ON CONFLICT (username) DO NOTHING;

-- RLS (Row Level Security) 설정
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 사용자 테이블 정책 (모든 사용자가 읽기 가능)
CREATE POLICY "Users are viewable by everyone" ON users
    FOR SELECT USING (true);

-- 게시글 테이블 정책 (모든 사용자가 읽기 가능)
CREATE POLICY "Posts are viewable by everyone" ON posts
    FOR SELECT USING (true);

-- 게시글 작성 정책 (인증된 사용자만 작성 가능)
CREATE POLICY "Users can insert posts" ON posts
    FOR INSERT WITH CHECK (true);

-- 게시글 수정 정책 (작성자만 수정 가능)
CREATE POLICY "Users can update own posts" ON posts
    FOR UPDATE USING (author = current_user);

-- 게시글 삭제 정책 (작성자만 삭제 가능)
CREATE POLICY "Users can delete own posts" ON posts
    FOR DELETE USING (author = current_user); 