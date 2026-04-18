import json
import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "audio_format": "mp3",
    "audio_quality": "320",
    "download_thumbnails": False,
    "create_playlist_folder": True,
    "auto_mode_quality": "best",
    "history_enabled": True,
    "max_retries": 3,
    "duplicate_action": "skip",  # skip, overwrite, rename
    "parallel_downloads": False,
    "max_parallel_downloads": 3,
    "log_level": "INFO"
}

CONFIG_FILE = "yt_download_config.json"
HISTORY_FILE = "yt_download_history.json"
LOG_FILE = "yt_download.log"

def get_config_dir():
    """Retorna o diretório padrão de configuração do usuário."""
    return Path.home() / ".yt-download"

def ensure_config_dir() -> Path:
    """Cria o diretório padrão de configuração quando necessário."""
    config_dir = get_config_dir()
    config_dir.mkdir(exist_ok=True)
    return config_dir

def get_legacy_storage_path(filename: str) -> Path:
    """Retorna o caminho antigo usado antes da pasta ~/.yt-download."""
    return Path.home() / filename

def get_storage_path(filename: str) -> Path:
    """
    Resolve o caminho de armazenamento priorizando o layout atual, mas
    mantendo compatibilidade com instalações antigas que salvavam em ~/
    com nomes yt_download*.
    """
    config_dir = get_config_dir()
    current_path = config_dir / filename
    legacy_path = get_legacy_storage_path(filename)

    if current_path.exists():
        return current_path
    if legacy_path.exists():
        return legacy_path
    ensure_config_dir()
    return current_path

class Config:
    def __init__(self):
        self.config_path = get_storage_path(CONFIG_FILE)
        self.history_path = get_storage_path(HISTORY_FILE)
        self.settings = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    config = DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        self.save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None):
        if config is None:
            config = self.settings

        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        self.settings[key] = value
        self.save_config()
