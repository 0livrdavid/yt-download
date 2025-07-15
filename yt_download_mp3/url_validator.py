import re
import requests
from urllib.parse import urlparse, parse_qs
from typing import Tuple, Optional, Dict, Any

class URLValidator:
    YOUTUBE_DOMAINS = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com', 'music.youtube.com']
    
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() in URLValidator.YOUTUBE_DOMAINS
        except:
            return False
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def is_playlist(url: str) -> Tuple[bool, Optional[str]]:
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            playlist_id = query_params.get('list', [None])[0]
            if playlist_id:
                return True, playlist_id
            
            if '/playlist' in parsed.path:
                return True, None
            
            return False, None
        except:
            return False, None
    
    @staticmethod
    def clean_url(url: str) -> str:
        """Remove parâmetros desnecessários da URL."""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Manter apenas parâmetros essenciais
            essential_params = {}
            if 'v' in query_params:
                essential_params['v'] = query_params['v'][0]
            if 'list' in query_params:
                essential_params['list'] = query_params['list'][0]
            if 'index' in query_params:
                essential_params['index'] = query_params['index'][0]
            
            # Reconstruir URL limpa
            clean_query = '&'.join([f"{k}={v}" for k, v in essential_params.items()])
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{'?' + clean_query if clean_query else ''}"
        except:
            return url
    
    @staticmethod
    def validate_accessibility(url: str) -> Dict[str, Any]:
        """Verifica se a URL é acessível."""
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            return {
                'accessible': response.status_code < 400,
                'status_code': response.status_code,
                'final_url': response.url
            }
        except requests.RequestException as e:
            return {
                'accessible': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_and_classify(url: str) -> dict:
        # Validação básica de formato
        if not url or not isinstance(url, str):
            return {
                'valid': False,
                'error': 'URL não fornecida ou inválida'
            }
        
        # Adicionar https:// se não tiver protocolo
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validar domínio do YouTube
        if not URLValidator.is_valid_youtube_url(url):
            return {
                'valid': False,
                'error': 'URL inválida ou não é do YouTube'
            }
        
        # Limpar URL
        clean_url = URLValidator.clean_url(url)
        
        # Classificar tipo
        is_playlist_url, playlist_id = URLValidator.is_playlist(clean_url)
        video_id = URLValidator.extract_video_id(clean_url)
        
        # Validação adicional
        if not video_id and not playlist_id:
            return {
                'valid': False,
                'error': 'Não foi possível extrair ID do vídeo ou playlist'
            }
        
        return {
            'valid': True,
            'is_playlist': is_playlist_url,
            'video_id': video_id,
            'playlist_id': playlist_id,
            'url': clean_url,
            'original_url': url
        }