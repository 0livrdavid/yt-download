import os
import yt_dlp
import time
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from .history import DownloadHistory
from .utils import SystemValidator, FileUtils, NetworkUtils
from .logger import get_logger

class YTDownloader:
    def __init__(self, progress_callback: Optional[Callable] = None, config: Dict[str, Any] = None):
        self.progress_callback = progress_callback
        self.history = DownloadHistory()
        self.download_path = Path.cwd()
        self.config = config or {}
        self.logger = get_logger()
        self.max_retries = self.config.get('max_retries', 3)
        self.duplicate_action = self.config.get('duplicate_action', 'skip')  # skip, overwrite, rename
        
        # Stats de progresso
        self.download_stats = {
            'total_bytes': 0,
            'downloaded_bytes': 0,
            'start_time': 0,
            'speed': 0
        }
    
    def _progress_hook(self, d):
        if not self.progress_callback:
            return
            
        if d['status'] == 'downloading':
            # Atualizar stats
            if 'total_bytes' in d and d['total_bytes']:
                self.download_stats['total_bytes'] = d['total_bytes']
                self.download_stats['downloaded_bytes'] = d['downloaded_bytes']
                
                if self.download_stats['start_time'] == 0:
                    self.download_stats['start_time'] = time.time()
                
                # Calcular velocidade e ETA
                elapsed_time = time.time() - self.download_stats['start_time']
                if elapsed_time > 0:
                    self.download_stats['speed'] = d['downloaded_bytes'] / elapsed_time
                    
                    if self.download_stats['speed'] > 0:
                        remaining_bytes = d['total_bytes'] - d['downloaded_bytes']
                        eta_seconds = remaining_bytes / self.download_stats['speed']
                        eta_str = f"{int(eta_seconds//60)}:{int(eta_seconds%60):02d}"
                    else:
                        eta_str = "∞"
                else:
                    eta_str = "∞"
                
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                speed_mb = self.download_stats['speed'] / (1024 * 1024)
                
                self.progress_callback(
                    f"Baixando... {percent:.1f}% | "
                    f"{speed_mb:.1f} MB/s | "
                    f"ETA: {eta_str}"
                )
            else:
                self.progress_callback("Baixando...")
        elif d['status'] == 'finished':
            self.download_stats = {'total_bytes': 0, 'downloaded_bytes': 0, 'start_time': 0, 'speed': 0}
            self.progress_callback("Download concluído, processando áudio...")
    
    def check_system_requirements(self) -> Dict[str, Any]:
        """Verifica se todos os requisitos do sistema estão atendidos."""
        self.logger.info("Verificando requisitos do sistema...")
        
        # Verificar FFmpeg
        ffmpeg_check = SystemValidator.check_ffmpeg()
        self.logger.log_system_check("FFmpeg", ffmpeg_check['installed'], 
                                    f"- {ffmpeg_check.get('version', 'N/A')}" if ffmpeg_check['installed'] else f"- {ffmpeg_check['error']}")
        
        # Verificar conectividade com YouTube
        youtube_check = NetworkUtils.test_youtube_connectivity()
        network_ok = youtube_check['all_working']
        
        network_details = f"- Status: {youtube_check['overall_status']}"
        if youtube_check['overall_status'] == 'online':
            avg_response = sum(r['response_time'] for r in youtube_check['endpoints'].values() if r['response_time']) / len([r for r in youtube_check['endpoints'].values() if r['response_time']])
            network_details += f" | Latência média: {avg_response:.0f}ms"
        
        self.logger.log_system_check("YouTube", network_ok, network_details)
        
        return {
            'ffmpeg': ffmpeg_check,
            'network': network_ok,
            'youtube': youtube_check,
            'all_ok': ffmpeg_check['installed'] and network_ok
        }
    
    def _get_ydl_opts(self, format_type: str, quality: str, is_playlist: bool = False, playlist_title: str = None) -> Dict[str, Any]:
        output_template = str(self.download_path / "%(title)s.%(ext)s")
        
        if is_playlist:
            # Usar o título real da playlist ou um nome padrão
            folder_name = playlist_title if playlist_title else "%(playlist)s"
            # Sanitizar o nome da pasta (remover caracteres inválidos)
            if playlist_title:
                import re
                folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
            
            output_template = str(self.download_path / folder_name / "%(playlist_index)s - %(title)s.%(ext)s")
        
        # Base options
        ydl_opts = {
            'outtmpl': output_template,
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'retries': self.max_retries,
            'fragment_retries': self.max_retries,
        }
        
        # Adicionar thumbnail se configurado
        if self.config.get('download_thumbnails', False):
            ydl_opts['writethumbnail'] = True
            ydl_opts['writeinfojson'] = True
        
        if format_type == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality if quality.isdigit() else '320',
                }]
            })
        else:
            ydl_opts.update({
                'format': f'bestaudio[ext={format_type}]/bestaudio/best'
            })
        
        return ydl_opts
    
    def _download_with_retry(self, ydl, url: str, max_retries: int = None) -> bool:
        """Download com retry automático."""
        if max_retries is None:
            max_retries = self.max_retries
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Tentativa {attempt + 1}/{max_retries + 1} para {url[:50]}...")
                    if self.progress_callback:
                        self.progress_callback(f"Retry {attempt + 1}/{max_retries + 1}...")
                
                ydl.download([url])
                return True
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Falha na tentativa {attempt + 1}: {str(e)}")
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Backoff exponencial
                    self.logger.info(f"Aguardando {wait_time}s antes da próxima tentativa...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Todas as tentativas falharam para {url}: {str(last_error)}")
                    raise last_error
        
        return False
    
    def _find_output_file(self, title: str, format_type: str, playlist_title: str = None) -> Optional[Path]:
        """Encontra o arquivo de saída baseado no título."""
        search_dir = self.download_path
        if playlist_title:
            safe_folder_name = FileUtils.sanitize_filename(playlist_title)
            search_dir = self.download_path / safe_folder_name
        
        return FileUtils.find_downloaded_file(search_dir, title, format_type)
    
    def _download_playlist_parallel(self, ydl, entries: List[Dict], format_type: str, quality: str, playlist_title: str) -> List[Dict]:
        """Download paralelo de playlist."""
        results = []
        max_workers = min(self.config.get('max_parallel_downloads', 3), len(entries))
        
        def download_single(entry):
            if not entry:
                return {'title': 'Unknown', 'status': 'failed', 'error': 'Entry is None'}
            
            try:
                self.logger.log_download_start(entry['webpage_url'], format_type, quality)
                
                # Criar um downloader separado para thread
                with yt_dlp.YoutubeDL(self._get_ydl_opts(format_type, quality, True, playlist_title)) as thread_ydl:
                    success = self._download_with_retry(thread_ydl, entry['webpage_url'])
                    
                    if success:
                        file_path = self._find_output_file(entry.get('title', 'Unknown'), format_type, playlist_title)
                        file_size = FileUtils.get_file_size(file_path) if file_path else 0
                        
                        self.history.add_download(
                            title=entry.get('title', 'Unknown'),
                            duration=entry.get('duration', 0),
                            file_size=file_size * 1024 * 1024,
                            format_output=format_type,
                            quality=quality,
                            url=entry['webpage_url']
                        )
                        
                        self.logger.log_download_success(
                            entry.get('title', 'Unknown'), 
                            file_size, 
                            entry.get('duration', 0) / 60 if entry.get('duration') else 0
                        )
                        
                        return {'title': entry.get('title', 'Unknown'), 'status': 'success'}
                
            except Exception as e:
                self.logger.log_download_error(entry['webpage_url'], str(e))
                return {'title': entry.get('title', 'Unknown'), 'status': 'failed', 'error': str(e)}
        
        # Executar downloads em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_entry = {executor.submit(download_single, entry): entry for entry in entries}
            
            for future in concurrent.futures.as_completed(future_to_entry):
                result = future.result()
                results.append(result)
                
                if self.progress_callback:
                    completed = len(results)
                    total = len(entries)
                    self.progress_callback(f"Playlist: {completed}/{total} concluídos")
        
        return results
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:  # Playlist
                    entries = list(info['entries'])
                    return {
                        'type': 'playlist',
                        'title': info.get('title', 'Playlist'),
                        'count': len(entries),
                        'duration': sum(entry.get('duration', 0) for entry in entries if entry),
                        'entries': entries
                    }
                else:  # Single video
                    return {
                        'type': 'video',
                        'title': info.get('title', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'uploader': info.get('uploader', 'Unknown'),
                        'view_count': info.get('view_count', 0)
                    }
        except Exception as e:
            raise Exception(f"Erro ao obter informações do vídeo: {str(e)}")
    
    def download(self, url: str, format_type: str = "mp3", quality: str = "320", 
                is_playlist: bool = False) -> Dict[str, Any]:
        try:
            # Primeiro extrair informações para obter o título da playlist
            temp_ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': False}
            with yt_dlp.YoutubeDL(temp_ydl_opts) as temp_ydl:
                info = temp_ydl.extract_info(url, download=False)
            
            # Agora gerar as opções com o título correto da playlist
            playlist_title = None
            if is_playlist and 'entries' in info:
                playlist_title = info.get('title', 'Playlist').strip()
                if not playlist_title or playlist_title.lower() == 'na':
                    playlist_title = f"Playlist_{info.get('id', 'Unknown')}"
            
            ydl_opts = self._get_ydl_opts(format_type, quality, is_playlist, playlist_title)
            
            # Criar pasta da playlist se necessário
            if is_playlist and playlist_title:
                import re
                safe_folder_name = re.sub(r'[<>:"/\\|?*]', '_', playlist_title)
                playlist_folder = self.download_path / safe_folder_name
                playlist_folder.mkdir(exist_ok=True)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                
                if 'entries' in info:  # Playlist
                    results = []
                    
                    # Download paralelo se configurado
                    if self.config.get('parallel_downloads', False) and len(info['entries']) > 1:
                        results = self._download_playlist_parallel(ydl, info['entries'], format_type, quality, playlist_title)
                    else:
                        # Download sequencial
                        for entry in info['entries']:
                            if entry:  # Pode ser None para vídeos indisponíveis
                                try:
                                    self.logger.log_download_start(entry['webpage_url'], format_type, quality)
                                    
                                    # Download com retry
                                    success = self._download_with_retry(ydl, entry['webpage_url'])
                                    
                                    if success:
                                        # Calcular tamanho do arquivo
                                        file_path = self._find_output_file(entry.get('title', 'Unknown'), format_type, playlist_title)
                                        file_size = FileUtils.get_file_size(file_path) if file_path else 0
                                        
                                        # Adicionar ao histórico
                                        self.history.add_download(
                                            title=entry.get('title', 'Unknown'),
                                            duration=entry.get('duration', 0),
                                            file_size=file_size * 1024 * 1024,  # Converter MB para bytes
                                            format_output=format_type,
                                            quality=quality,
                                            url=entry['webpage_url']
                                        )
                                        
                                        self.logger.log_download_success(
                                            entry.get('title', 'Unknown'), 
                                            file_size, 
                                            entry.get('duration', 0) / 60 if entry.get('duration') else 0
                                        )
                                        
                                        results.append({
                                            'title': entry.get('title', 'Unknown'),
                                            'status': 'success'
                                        })
                                    
                                except Exception as e:
                                    self.logger.log_download_error(entry['webpage_url'], str(e))
                                    results.append({
                                        'title': entry.get('title', 'Unknown'),
                                        'status': 'failed',
                                        'error': str(e)
                                    })
                    
                    return {
                        'type': 'playlist',
                        'title': info.get('title', 'Playlist'),
                        'results': results,
                        'total': len(info['entries']),
                        'successful': len([r for r in results if r['status'] == 'success'])
                    }
                
                else:  # Single video
                    self.logger.log_download_start(url, format_type, quality)
                    
                    # Download com retry
                    success = self._download_with_retry(ydl, url)
                    
                    if success:
                        # Calcular tamanho do arquivo
                        file_path = self._find_output_file(info.get('title', 'Unknown'), format_type)
                        file_size = FileUtils.get_file_size(file_path) if file_path else 0
                        
                        # Adicionar ao histórico
                        self.history.add_download(
                            title=info.get('title', 'Unknown'),
                            duration=info.get('duration', 0),
                            file_size=file_size * 1024 * 1024,  # Converter MB para bytes
                            format_output=format_type,
                            quality=quality,
                            url=url
                        )
                        
                        self.logger.log_download_success(
                            info.get('title', 'Unknown'), 
                            file_size, 
                            info.get('duration', 0) / 60 if info.get('duration') else 0
                        )
                        
                        return {
                            'type': 'video',
                            'title': info.get('title', 'Unknown'),
                            'filename': f"{info.get('title', 'Unknown')}.{format_type}",
                            'status': 'success',
                            'file_size': file_size
                        }
                    
        except Exception as e:
            raise Exception(f"Erro durante o download: {str(e)}")
    
    def get_history(self):
        return self.history.get_recent(10)
    
    def get_stats(self):
        return self.history.get_stats()
    
    def reset_history(self):
        return self.history.reset_history()
    
    def get_logger(self):
        return self.logger