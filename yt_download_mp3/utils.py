import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SystemValidator:
    @staticmethod
    def check_ffmpeg() -> Dict[str, Any]:
        """Verifica se FFmpeg está instalado e disponível."""
        try:
            # Verificar se FFmpeg está no PATH
            ffmpeg_path = shutil.which('ffmpeg')
            if not ffmpeg_path:
                return {
                    'installed': False,
                    'error': 'FFmpeg não encontrado no PATH do sistema',
                    'suggestion': 'Instale FFmpeg: brew install ffmpeg (macOS) ou apt install ffmpeg (Ubuntu)'
                }
            
            # Verificar versão
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'installed': False,
                    'error': 'FFmpeg encontrado mas não funciona corretamente',
                    'suggestion': 'Reinstale FFmpeg'
                }
            
            # Extrair versão
            version_line = result.stdout.split('\n')[0]
            version = version_line.split(' ')[2] if len(version_line.split(' ')) > 2 else 'unknown'
            
            return {
                'installed': True,
                'path': ffmpeg_path,
                'version': version
            }
            
        except subprocess.TimeoutExpired:
            return {
                'installed': False,
                'error': 'FFmpeg não respondeu (timeout)',
                'suggestion': 'Verifique se FFmpeg está funcionando: ffmpeg -version'
            }
        except Exception as e:
            return {
                'installed': False,
                'error': f'Erro ao verificar FFmpeg: {str(e)}',
                'suggestion': 'Reinstale FFmpeg'
            }

class FileUtils:
    @staticmethod
    def get_file_size(file_path: Path) -> float:
        """Retorna o tamanho do arquivo em MB."""
        try:
            if file_path.exists():
                size_bytes = file_path.stat().st_size
                return round(size_bytes / (1024 * 1024), 2)
            return 0.0
        except Exception as e:
            logger.error(f"Erro ao obter tamanho do arquivo {file_path}: {e}")
            return 0.0
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove caracteres inválidos do nome do arquivo."""
        import re
        # Remover caracteres inválidos para nomes de arquivo
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remover espaços extras e pontos no final
        sanitized = re.sub(r'\s+', ' ', sanitized).strip('. ')
        return sanitized
    
    @staticmethod
    def find_downloaded_file(directory: Path, title: str, extension: str = "mp3") -> Optional[Path]:
        """Encontra arquivo baixado baseado no título."""
        sanitized_title = FileUtils.sanitize_filename(title)
        
        # Padrões possíveis de nome de arquivo
        patterns = [
            f"{sanitized_title}.{extension}",
            f"*{sanitized_title}*.{extension}",
            f"*{title[:20]}*.{extension}"  # Primeiros 20 caracteres
        ]
        
        for pattern in patterns:
            files = list(directory.glob(pattern))
            if files:
                return files[0]  # Retorna o primeiro encontrado
        
        return None
    
    @staticmethod
    def handle_duplicate_file(file_path: Path, action: str = "skip") -> Path:
        """Trata arquivos duplicados baseado na ação escolhida."""
        if not file_path.exists():
            return file_path
        
        if action == "skip":
            return file_path  # Não faz nada, mantém o existente
        elif action == "overwrite":
            file_path.unlink()  # Remove o arquivo existente
            return file_path
        elif action == "rename":
            # Adiciona número sequencial
            counter = 1
            stem = file_path.stem
            suffix = file_path.suffix
            parent = file_path.parent
            
            while True:
                new_path = parent / f"{stem}_{counter}{suffix}"
                if not new_path.exists():
                    return new_path
                counter += 1
        
        return file_path

class NetworkUtils:
    @staticmethod
    def test_connection(url: str = "https://www.youtube.com") -> bool:
        """Testa conectividade básica."""
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=10)
            return True
        except Exception:
            return False
    
    @staticmethod
    def test_youtube_connectivity() -> Dict[str, Any]:
        """Testa conectividade específica com YouTube."""
        import urllib.request
        import time
        
        # Teste principal do YouTube
        main_test = {
            'status': 'offline',
            'response_time': None,
            'error': None
        }
        
        try:
            start_time = time.time()
            response = urllib.request.urlopen("https://www.youtube.com", timeout=15)
            end_time = time.time()
            
            if response.getcode() == 200:
                main_test = {
                    'status': 'online',
                    'response_time': round((end_time - start_time) * 1000, 2),
                    'status_code': response.getcode()
                }
        except Exception as e:
            main_test['error'] = str(e)
        
        # Teste de vídeo específico (mais simples)
        video_test = False
        try:
            test_video = urllib.request.urlopen("https://youtu.be/dQw4w9WgXcQ", timeout=10)
            video_test = test_video.getcode() == 200
        except:
            video_test = False
        
        # Status geral
        youtube_working = main_test['status'] == 'online'
        overall_status = 'online' if youtube_working else 'offline'
        
        return {
            'all_working': youtube_working,
            'endpoints': {'https://www.youtube.com': main_test},
            'video_access': video_test,
            'overall_status': overall_status
        }