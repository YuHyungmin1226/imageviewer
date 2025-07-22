-- Supabase 완전 정리 및 새로운 설정
-- 기존 정책과 충돌 없이 깨끗하게 설정

-- 1단계: 모든 기존 정책 강제 삭제 (오류 무시)
DO $$ 
DECLARE
    policy_record RECORD;
BEGIN
    -- users 테이블의 모든 정책 삭제
    FOR policy_record IN 
        SELECT policyname FROM pg_policies WHERE tablename = 'users'
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(policy_record.policyname) || ' ON users';
    END LOOP;
    
    -- posts 테이블의 모든 정책 삭제
    FOR policy_record IN 
        SELECT policyname FROM pg_policies WHERE tablename = 'posts'
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(policy_record.policyname) || ' ON posts';
    END LOOP;
    
    RAISE NOTICE '모든 기존 정책이 삭제되었습니다.';
END $$;

-- 2단계: URL 미리보기 컬럼 추가
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

-- 3단계: 기존 데이터 초기화
UPDATE posts 
SET url_previews = '[]' 
WHERE url_previews IS NULL;

-- 4단계: 새로운 정책 생성 (중복 방지)
DO $$
BEGIN
    -- Users 테이블 정책
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_select_policy'
    ) THEN
        CREATE POLICY "users_select_policy" ON users FOR SELECT USING (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_insert_policy'
    ) THEN
        CREATE POLICY "users_insert_policy" ON users FOR INSERT WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_update_policy'
    ) THEN
        CREATE POLICY "users_update_policy" ON users FOR UPDATE USING (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_delete_policy'
    ) THEN
        CREATE POLICY "users_delete_policy" ON users FOR DELETE USING (true);
    END IF;
    
    -- Posts 테이블 정책
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'posts' AND policyname = 'posts_select_policy'
    ) THEN
        CREATE POLICY "posts_select_policy" ON posts FOR SELECT USING (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'posts' AND policyname = 'posts_insert_policy'
    ) THEN
        CREATE POLICY "posts_insert_policy" ON posts FOR INSERT WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'posts' AND policyname = 'posts_update_policy'
    ) THEN
        CREATE POLICY "posts_update_policy" ON posts FOR UPDATE USING (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'posts' AND policyname = 'posts_delete_policy'
    ) THEN
        CREATE POLICY "posts_delete_policy" ON posts FOR DELETE USING (true);
    END IF;
    
    RAISE NOTICE '모든 새로운 정책이 생성되었습니다.';
END $$;

-- 5단계: 결과 확인
SELECT 'users 테이블 정책' as "구분", policyname as "정책명", cmd as "명령" 
FROM pg_policies 
WHERE tablename = 'users'
UNION ALL
SELECT 'posts 테이블 정책' as "구분", policyname as "정책명", cmd as "명령" 
FROM pg_policies 
WHERE tablename = 'posts'
ORDER BY "구분", "정책명";

-- 6단계: 컬럼 확인
SELECT 
    table_name as "테이블",
    column_name as "컬럼명", 
    data_type as "타입", 
    column_default as "기본값"
FROM information_schema.columns 
WHERE table_name IN ('users', 'posts')
AND column_name IN ('id', 'username', 'content', 'files', 'url_previews', 'created_at')
ORDER BY table_name, ordinal_position;

-- 완료 메시지
SELECT '✅ Supabase 설정이 완료되었습니다! URL 미리보기 기능을 사용할 수 있습니다.' as "완료"; 