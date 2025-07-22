-- 가장 간단한 해결책: URL 미리보기 컬럼만 추가
-- 정책은 건드리지 않고 컬럼만 추가

-- URL 미리보기 컬럼 추가 (이미 있으면 무시)
ALTER TABLE posts ADD COLUMN IF NOT EXISTS url_previews JSONB DEFAULT '[]';

-- 기존 데이터 초기화
UPDATE posts SET url_previews = '[]' WHERE url_previews IS NULL;

-- 확인
SELECT 'URL 미리보기 컬럼이 추가되었습니다!' as "완료"; 