import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import streamlit as st
from typing import List, Dict, Optional, Tuple
import time

class URLPreviewGenerator:
    """URL 미리보기 생성 클래스"""
    
    def __init__(self, cache_duration: int = 3600):
        self.cache = {}
        self.cache_duration = cache_duration
    
    def extract_urls(self, text: str) -> List[str]:
        """텍스트에서 URL 추출"""
        # HTTP/HTTPS URL 패턴
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # 중복 제거 및 유효성 검증
        valid_urls = []
        for url in urls:
            try:
                parsed = urlparse(url)
                if parsed.netloc and parsed.scheme in ['http', 'https']:
                    valid_urls.append(url)
            except:
                continue
        
        return list(set(valid_urls))  # 중복 제거
    
    def get_url_preview(self, url: str) -> Optional[Dict]:
        """URL 메타데이터 추출"""
        # 캐시 확인
        cache_key = url
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            # 안전한 요청 헤더 설정
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # 타임아웃과 크기 제한으로 안전하게 요청
            response = requests.get(
                url, 
                headers=headers, 
                timeout=10, 
                stream=True,
                allow_redirects=True
            )
            
            # 응답 크기 제한 (1MB)
            max_content_length = 1024 * 1024  # 1MB
            if response.headers.get('content-length'):
                if int(response.headers['content-length']) > max_content_length:
                    return None
            
            # HTML 내용 읽기
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > max_content_length:
                    break
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(content, 'html.parser')
            
            # 메타데이터 추출
            preview_data = self._extract_metadata(soup, url)
            
            # 캐시에 저장
            self.cache[cache_key] = (preview_data, time.time())
            
            return preview_data
            
        except Exception as e:
            # 에러 발생 시 기본 정보만 반환
            return {
                'url': url,
                'title': self._get_domain_name(url),
                'description': '',
                'image': '',
                'site_name': self._get_domain_name(url),
                'error': str(e)
            }
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """HTML에서 메타데이터 추출"""
        # 제목 추출
        title = ''
        # Open Graph 제목
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title['content']
        # Twitter 제목
        elif soup.find('meta', attrs={'name': 'twitter:title'}):
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            title = twitter_title['content']
        # HTML title 태그
        elif soup.find('title'):
            title = soup.find('title').get_text().strip()
        else:
            title = self._get_domain_name(url)
        
        # 설명 추출
        description = ''
        # Open Graph 설명
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            description = og_desc['content']
        # Twitter 설명
        elif soup.find('meta', attrs={'name': 'twitter:description'}):
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            description = twitter_desc['content']
        # meta description
        elif soup.find('meta', attrs={'name': 'description'}):
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content']
        
        # 이미지 추출
        image = ''
        # Open Graph 이미지
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image = og_image['content']
        # Twitter 이미지
        elif soup.find('meta', attrs={'name': 'twitter:image'}):
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            image = twitter_image['content']
        
        # 상대 URL을 절대 URL로 변환
        if image and not image.startswith('http'):
            image = urljoin(url, image)
        
        # 사이트 이름 추출
        site_name = ''
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            site_name = og_site['content']
        else:
            site_name = self._get_domain_name(url)
        
        return {
            'url': url,
            'title': title[:100] if title else self._get_domain_name(url),  # 제목 길이 제한
            'description': description[:200] if description else '',  # 설명 길이 제한
            'image': image,
            'site_name': site_name
        }
    
    def _get_domain_name(self, url: str) -> str:
        """URL에서 도메인 이름 추출"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # www. 제거
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return url
    
    def render_url_preview(self, preview_data: Dict) -> None:
        """URL 미리보기 렌더링"""
        if not preview_data:
            return
        
        # 미리보기 카드 HTML 생성
        title = preview_data.get('title', '')
        description = preview_data.get('description', '')
        image = preview_data.get('image', '')
        site_name = preview_data.get('site_name', '')
        url = preview_data.get('url', '')
        
        # 이미지가 있는 경우와 없는 경우 다르게 처리
        if image:
            preview_html = f"""
            <div class="url-preview-card">
                <a href="{url}" target="_blank" class="url-preview-link">
                    <div class="url-preview-content">
                        <div class="url-preview-image">
                            <img src="{image}" alt="미리보기 이미지" />
                        </div>
                        <div class="url-preview-text">
                            <div class="url-preview-title">{title}</div>
                            <div class="url-preview-description">{description}</div>
                            <div class="url-preview-site">{site_name}</div>
                        </div>
                    </div>
                </a>
            </div>
            """
        else:
            preview_html = f"""
            <div class="url-preview-card">
                <a href="{url}" target="_blank" class="url-preview-link">
                    <div class="url-preview-content-no-image">
                        <div class="url-preview-title">{title}</div>
                        <div class="url-preview-description">{description}</div>
                        <div class="url-preview-site">{site_name}</div>
                    </div>
                </a>
            </div>
            """
        
        st.markdown(preview_html, unsafe_allow_html=True)
    
    def process_text_with_urls(self, text: str) -> Tuple[str, List[Dict]]:
        """텍스트에서 URL을 처리하고 미리보기 데이터 반환"""
        urls = self.extract_urls(text)
        previews = []
        
        for url in urls:
            preview_data = self.get_url_preview(url)
            if preview_data:
                previews.append(preview_data)
        
        return text, previews 