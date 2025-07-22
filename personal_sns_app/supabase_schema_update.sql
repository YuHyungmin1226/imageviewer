-- Supabase 스키마 업데이트: URL 미리보기 기능
-- Supabase 대시보드의 SQL 편집기에서 실행하세요

-- posts 테이블에 url_previews 컬럼 추가
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS url_previews JSONB DEFAULT '[]';

-- 기존 데이터의 url_previews 컬럼을 빈 배열로 초기화
UPDATE posts 
SET url_previews = '[]' 
WHERE url_previews IS NULL;

-- 업데이트 완료 확인
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'posts' 
AND column_name = 'url_previews'; 