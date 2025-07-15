import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def get_config_dir():
    """Retorna o diretório de configuração do usuário"""
    config_dir = Path.home() / ".yt-download"
    config_dir.mkdir(exist_ok=True)
    return config_dir

class DownloadHistory:
    def __init__(self, history_file: str = "yt_download_history.json"):
        config_dir = get_config_dir()
        self.history_file = config_dir / history_file
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []
    
    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def add_download(self, title: str, duration: int, file_size: int, 
                    format_output: str, quality: str, url: str):
        entry = {
            'title': title,
            'date': datetime.now().isoformat(),
            'duration_minutes': round(duration / 60, 2) if duration else 0,
            'file_size_mb': round(file_size / (1024 * 1024), 2) if file_size else 0,
            'format': format_output,
            'quality': quality,
            'url': url
        }
        
        self.history.append(entry)
        self.save_history()
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.history[-limit:] if self.history else []
    
    def search_by_title(self, title: str) -> List[Dict[str, Any]]:
        return [entry for entry in self.history 
                if title.lower() in entry['title'].lower()]
    
    def reset_history(self):
        self.history = []
        self.save_history()
    
    def get_stats(self) -> Dict[str, Any]:
        if not self.history:
            return {'total_downloads': 0}
        
        total_size = sum(entry.get('file_size_mb', 0) for entry in self.history)
        total_duration = sum(entry.get('duration_minutes', 0) for entry in self.history)
        
        return {
            'total_downloads': len(self.history),
            'total_size_mb': round(total_size, 2),
            'total_duration_minutes': round(total_duration, 2),
            'average_file_size_mb': round(total_size / len(self.history), 2),
            'most_recent': self.history[-1]['date'] if self.history else None
        }