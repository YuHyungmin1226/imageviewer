import os
from typing import Optional

class Config:
    """애플리케이션 설정 관리 클래스"""
    
    # Supabase 설정
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # NEIS API 설정
    NEIS_API_KEY: str = os.getenv("NEIS_API_KEY", "c4ef97602ca54adc9e4cd49648b247f6")
    
    # 애플리케이션 설정
    MAX_POST_LENGTH: int = 500
    
    @classmethod
    def is_supabase_configured(cls) -> bool:
        """Supabase 설정이 완료되었는지 확인"""
        return bool(cls.SUPABASE_URL and cls.SUPABASE_KEY) 