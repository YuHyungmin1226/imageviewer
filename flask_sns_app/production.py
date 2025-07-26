#!/usr/bin/env python3
"""
Flask SNS 앱 프로덕션 실행 스크립트
Windows용 Waitress 서버 사용
"""

import os
import sys

# 현재 디렉터리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    print("🚀 Flask SNS 앱을 프로덕션 모드로 시작합니다...")
    print("📱 브라우저에서 http://localhost:5000 으로 접속하세요")
    print("🔑 기본 관리자 계정: admin / admin123")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    # 데이터베이스 초기화
    with app.app_context():
        print("🗄️  데이터베이스 테이블을 생성합니다...")
        db.create_all()
        
        # 기본 관리자 계정 생성
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 기본 관리자 계정이 생성되었습니다. (admin/admin123)")
        else:
            print("ℹ️  관리자 계정이 이미 존재합니다.")
    
    print("🌐 프로덕션 웹 서버를 시작합니다...")
    
    try:
        # Waitress 서버 사용 (Windows용)
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000, threads=4)
    except ImportError:
        print("⚠️  Waitress가 설치되지 않았습니다. 개발 서버로 실행합니다.")
        print("💡 프로덕션 배포를 위해 'pip install waitress'를 실행하세요.")
        app.run(host='0.0.0.0', port=5000, debug=False) 