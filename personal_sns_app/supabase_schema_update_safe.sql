-- 안전한 Supabase 스키마 업데이트: URL 미리보기 기능
-- 기존 정책과 충돌하지 않도록 설계됨
-- Supabase 대시보드의 SQL 편집기에서 실행하세요

-- 1단계: posts 테이블에 url_previews 컬럼 추가 (이미 존재하면 무시)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'posts' AND column_name = 'url_previews'
    ) THEN
        ALTER TABLE posts ADD COLUMN url_previews JSONB DEFAULT '[]';
        RAISE NOTICE 'url_previews 컬럼이 추가되었습니다.';
    ELSE
        RAISE NOTICE 'url_previews 컬럼이 이미 존재합니다.';
    END IF;
END $$;

-- 2단계: 기존 데이터의 url_previews 컬럼을 빈 배열로 초기화
UPDATE posts 
SET url_previews = '[]' 
WHERE url_previews IS NULL;

-- 3단계: 업데이트 결과 확인
SELECT 
    'posts 테이블 컬럼 정보' as "테이블",
    column_name as "컬럼명", 
    data_type as "데이터타입", 
    is_nullable as "NULL허용", 
    column_default as "기본값"
FROM information_schema.columns 
WHERE table_name = 'posts' 
AND column_name IN ('content', 'files', 'url_previews', 'likes', 'comments')
ORDER BY ordinal_position;

-- 4단계: 샘플 데이터 확인 (최근 5개 게시글)
SELECT 
    id,
    content,
    author,
    CASE 
        WHEN url_previews IS NULL THEN 'NULL'
        WHEN url_previews = '[]' THEN '빈 배열'
        ELSE '데이터 있음'
    END as url_previews_status,
    created_at
FROM posts 
ORDER BY created_at DESC 
LIMIT 5;

-- 완료 메시지
SELECT 'URL 미리보기 기능을 위한 스키마 업데이트가 완료되었습니다!' as "업데이트 완료"; 