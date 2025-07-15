import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class YTDownloadLogger:
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger("yt_download_mp3")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (apenas para ERROR e WARNING)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (se especificado)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def log_download_start(self, url: str, format_type: str, quality: str):
        self.info(f"Download iniciado - URL: {url[:50]}... | Formato: {format_type} | Qualidade: {quality}")
    
    def log_download_success(self, title: str, file_size: float, duration: float):
        self.info(f"Download concluído - {title} | {file_size}MB | {duration:.1f}min")
    
    def log_download_error(self, url: str, error: str):
        self.error(f"Falha no download - URL: {url[:50]}... | Erro: {error}")
    
    def log_system_check(self, component: str, status: bool, details: str = ""):
        level = "info" if status else "error"
        getattr(self.logger, level)(f"Verificação do sistema - {component}: {'OK' if status else 'FALHA'} {details}")

# Singleton logger instance
_logger_instance = None

def get_logger(log_level: str = "INFO", log_file: Optional[str] = None) -> YTDownloadLogger:
    global _logger_instance
    if _logger_instance is None:
        # Usar log file padrão se não especificado
        if log_file is None:
            log_file = Path.cwd() / "yt_download.log"
        _logger_instance = YTDownloadLogger(log_level, str(log_file))
    return _logger_instance