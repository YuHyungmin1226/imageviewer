"""
기본 테스트 파일
실제 테스트는 pytest를 사용하여 구현하는 것을 권장합니다.
"""

import unittest
from utils import hash_password, validate_file_type, validate_file_size, format_file_size
from config import Config

class TestUtils(unittest.TestCase):
    """유틸리티 함수 테스트"""
    
    def test_hash_password(self):
        """비밀번호 해싱 테스트"""
        password = "test123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # 같은 비밀번호는 같은 해시를 생성해야 함
        self.assertEqual(hash1, hash2)
        
        # 다른 비밀번호는 다른 해시를 생성해야 함
        hash3 = hash_password("test124")
        self.assertNotEqual(hash1, hash3)
    
    def test_validate_file_type(self):
        """파일 타입 검증 테스트"""
        # 유효한 파일 타입
        self.assertTrue(validate_file_type("test.jpg"))
        self.assertTrue(validate_file_type("test.PNG"))
        self.assertTrue(validate_file_type("test.mp4"))
        
        # 유효하지 않은 파일 타입
        self.assertFalse(validate_file_type("test.exe"))
        self.assertFalse(validate_file_type("test.bat"))
        self.assertFalse(validate_file_type(""))
    
    def test_validate_file_size(self):
        """파일 크기 검증 테스트"""
        # 유효한 파일 크기
        self.assertTrue(validate_file_size(1024))  # 1KB
        self.assertTrue(validate_file_size(Config.MAX_FILE_SIZE))  # 최대 크기
        
        # 유효하지 않은 파일 크기
        self.assertFalse(validate_file_size(Config.MAX_FILE_SIZE + 1))
        self.assertFalse(validate_file_size(0))
    
    def test_format_file_size(self):
        """파일 크기 포맷 테스트"""
        self.assertEqual(format_file_size(0), "0B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1048576), "1.0 MB")

class TestConfig(unittest.TestCase):
    """설정 클래스 테스트"""
    
    def test_get_allowed_file_types(self):
        """허용된 파일 타입 목록 테스트"""
        allowed_types = Config.get_allowed_file_types()
        
        # 이미지 타입이 포함되어야 함
        self.assertIn("jpg", allowed_types)
        self.assertIn("png", allowed_types)
        
        # 비디오 타입이 포함되어야 함
        self.assertIn("mp4", allowed_types)
        
        # 오디오 타입이 포함되어야 함
        self.assertIn("mp3", allowed_types)

if __name__ == '__main__':
    unittest.main() 