-- 좋아요 기능 제거: likes 컬럼 삭제
-- Supabase SQL 편집기에서 실행

-- posts 테이블의 likes 컬럼 제거
ALTER TABLE posts DROP COLUMN IF EXISTS likes;

-- 확인
SELECT 
    column_name as "컬럼명", 
    data_type as "타입"
FROM information_schema.columns 
WHERE table_name = 'posts'
ORDER BY ordinal_position; 