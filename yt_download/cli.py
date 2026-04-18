from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from typing import Dict, Any, List
from . import __version__

console = Console()

class CLI:
    def __init__(self):
        self.console = console
    
    def show_welcome(self, config=None):
        welcome_text = "[bold blue]🎵 YouTube to MP3 Downloader[/bold blue]\n"
        welcome_text += "[dim]Download YouTube videos and playlists as high-quality MP3 files[/dim]"
        welcome_text += f"\n[dim]Versão {__version__}[/dim]"
        
        if config:
            parallel_status = "🚀 Ativado" if config.get('parallel_downloads', False) else "⚪ Desativado"
            format_info = config.get('audio_format', 'mp3').upper()
            quality_info = config.get('audio_quality', '320')
            
            welcome_text += f"\n\n[bold]Configuração Atual:[/bold]"
            welcome_text += f"\n• Formato: [cyan]{format_info}[/cyan] | Qualidade: [cyan]{quality_info}[/cyan]"
            welcome_text += f"\n• Download Paralelo: {parallel_status}"
            
            if not config.get('parallel_downloads', False):
                welcome_text += f"\n[yellow]💡 Dica: Ative o download paralelo para playlists mais rápidas[/yellow]"
                welcome_text += f"\n[dim]   Use: yt-download --config[/dim]"
        
        self.console.print(Panel(welcome_text, border_style="blue"))
    
    def get_url_input(self) -> str:
        return Prompt.ask("\n[yellow]📎 Cole o link do YouTube[/yellow]")
    
    def show_url_info(self, info: Dict[str, Any]):
        if info['is_playlist']:
            rprint(f"\n[green]✅ Playlist detectada![/green]")
        else:
            rprint(f"\n[green]✅ Vídeo único detectado![/green]")
    
    def get_mode_choice(self, config=None) -> str:
        rprint("\n[bold]Escolha o modo de download:[/bold]")
        
        if config:
            format_info = config.get('audio_format', 'mp3').upper()
            quality_info = config.get('audio_quality', '320')
            rprint(f"[cyan]1.[/cyan] Automático ({format_info}, {quality_info})")
        else:
            rprint("[cyan]1.[/cyan] Automático (MP3, melhor qualidade)")
            
        rprint("[cyan]2.[/cyan] Manual (escolher formato e qualidade)")
        
        choice = Prompt.ask("Escolha", choices=["1", "2"], default="1")
        return "auto" if choice == "1" else "manual"
    
    def get_format_choice(self) -> str:
        rprint("\n[bold]Formatos disponíveis:[/bold]")
        formats = {
            "1": ("mp3", "MP3 (recomendado)"),
            "2": ("m4a", "M4A (AAC)"),
            "3": ("ogg", "OGG Vorbis"),
            "4": ("wav", "WAV (sem compressão)")
        }
        
        for key, (_, desc) in formats.items():
            rprint(f"[cyan]{key}.[/cyan] {desc}")
        
        choice = Prompt.ask("Escolha o formato", choices=list(formats.keys()), default="1")
        return formats[choice][0]
    
    def get_quality_choice(self, format_type: str) -> str:
        rprint(f"\n[bold]Qualidades disponíveis para {format_type.upper()}:[/bold]")
        
        if format_type == "mp3":
            qualities = {
                "1": ("320", "320 kbps (melhor qualidade)"),
                "2": ("256", "256 kbps (boa qualidade)"),
                "3": ("192", "192 kbps (qualidade média)"),
                "4": ("128", "128 kbps (menor tamanho)")
            }
        else:
            qualities = {
                "1": ("best", "Melhor qualidade disponível"),
                "2": ("worst", "Menor qualidade/tamanho")
            }
        
        for key, (_, desc) in qualities.items():
            rprint(f"[cyan]{key}.[/cyan] {desc}")
        
        choice = Prompt.ask("Escolha a qualidade", choices=list(qualities.keys()), default="1")
        return qualities[choice][0]
    
    def show_download_start(self, mode: str, format_type: str, quality: str):
        info = f"Modo: {mode.title()} | Formato: {format_type.upper()} | Qualidade: {quality}"
        rprint(f"\n[green]🚀 Iniciando download...[/green]")
        rprint(f"[dim]{info}[/dim]")
    
    def show_progress(self, message: str):
        rprint(f"[blue]⏳ {message}[/blue]")
    
    def show_success(self, title: str, filename: str):
        rprint(f"\n[green]✅ Download concluído![/green]")
        rprint(f"[bold]Título:[/bold] {title}")
        rprint(f"[bold]Arquivo:[/bold] {filename}")
    
    def show_error(self, error: str):
        rprint(f"\n[red]❌ Erro: {error}[/red]")
    
    def show_history(self, history_entries: List[Dict[str, Any]]):
        if not history_entries:
            rprint("\n[yellow]📝 Nenhum download no histórico[/yellow]")
            return
        
        table = Table(title="📝 Histórico de Downloads")
        table.add_column("Data", style="cyan")
        table.add_column("Título", style="white")
        table.add_column("Duração", justify="right", style="green")
        table.add_column("Tamanho", justify="right", style="blue")
        table.add_column("Formato", justify="center", style="magenta")
        
        for entry in history_entries[-10:]:  # Últimos 10
            table.add_row(
                entry['date'][:10],  # Apenas a data
                entry['title'][:40] + "..." if len(entry['title']) > 40 else entry['title'],
                f"{entry['duration_minutes']}min",
                f"{entry['file_size_mb']}MB",
                entry['format'].upper()
            )
        
        self.console.print(table)
    
    def show_stats(self, stats: Dict[str, Any]):
        if stats['total_downloads'] == 0:
            rprint("\n[yellow]📊 Nenhuma estatística disponível[/yellow]")
            return
        
        stats_text = f"""
[bold blue]📊 Estatísticas de Downloads[/bold blue]

[cyan]Total de downloads:[/cyan] {stats['total_downloads']}
[cyan]Tamanho total:[/cyan] {stats['total_size_mb']} MB
[cyan]Duração total:[/cyan] {stats['total_duration_minutes']} minutos
[cyan]Tamanho médio:[/cyan] {stats['average_file_size_mb']} MB
[cyan]Último download:[/cyan] {stats['most_recent'][:10] if stats['most_recent'] else 'N/A'}
        """
        self.console.print(Panel(stats_text, border_style="blue"))
    
    def show_reset_confirmation(self) -> bool:
        return Confirm.ask("\n[red]⚠️  Tem certeza que deseja apagar todo o histórico?[/red]")
    
    def show_reset_success(self):
        rprint("\n[green]✅ Histórico apagado com sucesso![/green]")
    
    def confirm_continue(self) -> bool:
        return Confirm.ask("\n[yellow]Fazer outro download?[/yellow]")
