import json
import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "audio_format": "mp3",
    "audio_quality": "320",
    "download_location_mode": "current_dir",
    "system_downloads_path": "",
    "custom_download_path": "",
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

def detect_system_downloads_path() -> Path:
    """Tenta detectar a pasta Downloads padrão do sistema."""
    home = Path.home()

    xdg_config = home / ".config" / "user-dirs.dirs"
    if xdg_config.exists():
        try:
            contents = xdg_config.read_text(encoding="utf-8")
            for line in contents.splitlines():
                if line.startswith("XDG_DOWNLOAD_DIR="):
                    raw_value = line.split("=", 1)[1].strip().strip('"')
                    expanded = raw_value.replace("$HOME", str(home))
                    return Path(expanded).expanduser()
        except OSError:
            pass

    return home / "Downloads"

def resolve_download_directory(settings: Dict[str, Any], current_dir: Path = None) -> Path:
    """Resolve o diretório efetivo de download a partir das configurações."""
    current_dir = current_dir or Path.cwd()
    mode = settings.get("download_location_mode", "current_dir")

    if mode == "system_downloads":
        configured_path = settings.get("system_downloads_path", "").strip()
        path = Path(configured_path).expanduser() if configured_path else detect_system_downloads_path()
        return path

    if mode == "custom_path":
        configured_path = settings.get("custom_download_path", "").strip()
        if configured_path:
            return Path(configured_path).expanduser()

    return current_dir

def get_download_mode_label(settings: Dict[str, Any], current_dir: Path = None) -> str:
    mode = settings.get("download_location_mode", "current_dir")
    if mode == "system_downloads":
        return "Downloads do sistema"
    if mode == "custom_path":
        return "Pasta personalizada"
    return "Pasta atual"

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
