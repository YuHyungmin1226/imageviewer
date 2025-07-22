-- 최소 명령어로 URL 미리보기 기능 활성화
-- Supabase SQL 편집기에서 실행

-- url_previews 컬럼 추가 (이미 있으면 오류 무시)
ALTER TABLE posts ADD COLUMN IF NOT EXISTS url_previews JSONB DEFAULT '[]';

-- 기존 데이터 초기화
UPDATE posts SET url_previews = '[]' WHERE url_previews IS NULL; 