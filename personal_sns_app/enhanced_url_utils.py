import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs
import streamlit as st
from typing import List, Dict, Optional, Tuple
import time
import json

class EnhancedURLPreviewGenerator:
    """향상된 URL 미리보기 생성 클래스 (YouTube 특별 지원)"""
    
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
    
    def extract_youtube_id(self, url: str) -> Optional[str]:
        """YouTube URL에서 동영상 ID 추출"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_youtube_data(self, video_id: str) -> Optional[Dict]:
        """YouTube 데이터 추출 (oEmbed API 사용)"""
        try:
            # YouTube oEmbed API 사용
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 고해상도 썸네일 URL 생성
                thumbnail_urls = [
                    f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",  # 최고 해상도
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",     # 고해상도
                    f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",     # 중간 해상도
                    f"https://img.youtube.com/vi/{video_id}/0.jpg"              # 기본
                ]
                
                # 사용 가능한 썸네일 찾기
                thumbnail_url = None
                for url in thumbnail_urls:
                    try:
                        thumb_response = requests.head(url, timeout=5)
                        if thumb_response.status_code == 200:
                            thumbnail_url = url
                            break
                    except:
                        continue
                
                return {
                    'type': 'youtube',
                    'video_id': video_id,
                    'title': data.get('title', ''),
                    'author_name': data.get('author_name', ''),
                    'author_url': data.get('author_url', ''),
                    'thumbnail_url': thumbnail_url or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    'width': data.get('width', 560),
                    'height': data.get('height', 315),
                    'duration': None,  # oEmbed에서는 제공하지 않음
                    'view_count': None,
                    'site_name': 'YouTube'
                }
        except Exception as e:
            st.write(f"YouTube 데이터 추출 오류: {e}")
        
        return None
    
    def get_url_preview(self, url: str) -> Optional[Dict]:
        """URL 메타데이터 추출 (YouTube 특별 처리)"""
        # 캐시 확인
        cache_key = url
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_data
        
        # YouTube URL 특별 처리
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = self.extract_youtube_id(url)
            if video_id:
                youtube_data = self.get_youtube_data(video_id)
                if youtube_data:
                    youtube_data['url'] = url
                    # 캐시에 저장
                    self.cache[cache_key] = (youtube_data, time.time())
                    return youtube_data
        
        # 일반 URL 처리
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
            preview_data['type'] = 'general'
            
            # 캐시에 저장
            self.cache[cache_key] = (preview_data, time.time())
            
            return preview_data
            
        except Exception as e:
            # 에러 발생 시 기본 정보만 반환
            return {
                'type': 'general',
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
    
    def render_youtube_preview(self, preview_data: Dict) -> None:
        """YouTube 미리보기 렌더링"""
        video_id = preview_data.get('video_id', '')
        title = preview_data.get('title', '')
        author_name = preview_data.get('author_name', '')
        thumbnail_url = preview_data.get('thumbnail_url', '')
        url = preview_data.get('url', '')
        
        # YouTube 스타일 미리보기 HTML
        youtube_html = f"""
        <div class="youtube-preview-card">
            <a href="{url}" target="_blank" class="youtube-preview-link">
                <div class="youtube-thumbnail-container">
                    <img src="{thumbnail_url}" alt="YouTube 썸네일" class="youtube-thumbnail" />
                    <div class="youtube-play-button">
                        <svg width="68" height="48" viewBox="0 0 68 48">
                            <path d="M66.52,7.74c-0.78-2.93-2.49-5.41-5.42-6.19C55.79,.13,34,0,34,0S12.21,.13,6.9,1.55 C3.97,2.33,2.27,4.81,1.48,7.74C0.06,13.05,0,24,0,24s0.06,10.95,1.48,16.26c0.78,2.93,2.49,5.41,5.42,6.19 C12.21,47.87,34,48,34,48s21.79-0.13,27.1-1.55c2.93-0.78,4.64-3.26,5.42-6.19C67.94,34.95,68,24,68,24S67.94,13.05,66.52,7.74z" fill="#f00"></path>
                            <path d="M 45,24 27,14 27,34" fill="#fff"></path>
                        </svg>
                    </div>
                </div>
                <div class="youtube-info">
                    <div class="youtube-title">{title}</div>
                    <div class="youtube-channel">{author_name}</div>
                    <div class="youtube-domain">YouTube</div>
                </div>
            </a>
        </div>
        """
        
        st.markdown(youtube_html, unsafe_allow_html=True)
    
    def render_url_preview(self, preview_data: Dict) -> None:
        """URL 미리보기 렌더링 (타입별 분기)"""
        if not preview_data:
            return
        
        preview_type = preview_data.get('type', 'general')
        
        if preview_type == 'youtube':
            self.render_youtube_preview(preview_data)
        else:
            # 기존 일반 미리보기
            self._render_general_preview(preview_data)
    
    def _render_general_preview(self, preview_data: Dict) -> None:
        """일반 URL 미리보기 렌더링"""
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