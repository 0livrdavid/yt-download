import os
import sys
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.text import Text
from pathlib import Path
from typing import Dict, Any, List
from . import __version__
from .config import resolve_download_directory, get_download_mode_label

console = Console()


class _InputReader:
    def __enter__(self):
        self.active = False
        if os.name != "nt":
            import termios
            import tty

            self.termios = termios
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)
            self.tty = tty
            self.resume()
        return self

    def __exit__(self, exc_type, exc, tb):
        if os.name != "nt":
            self.suspend()

    def suspend(self):
        if os.name != "nt" and self.active:
            self.termios.tcsetattr(self.fd, self.termios.TCSADRAIN, self.old_settings)
            self.active = False

    def resume(self):
        if os.name != "nt" and not self.active:
            self.tty.setraw(self.fd)
            self.active = True

    def read_key(self):
        if os.name == "nt":
            import msvcrt

            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                special = msvcrt.getwch()
                mapping = {"H": "up", "P": "down", "K": "left", "M": "right"}
                return mapping.get(special, "")
            if key == "\r":
                return "enter"
            if key == "\x1b":
                return "esc"
            if key == "\x08":
                return "backspace"
            return key

        first = sys.stdin.read(1)
        if first == "\x1b":
            second = sys.stdin.read(1)
            if second == "[":
                third = sys.stdin.read(1)
                mapping = {"A": "up", "B": "down", "C": "right", "D": "left"}
                return mapping.get(third, "esc")
            return "esc"
        if first in ("\r", "\n"):
            return "enter"
        if first in ("\x7f", "\b"):
            return "backspace"
        return first

class CLI:
    def __init__(self):
        self.console = console
        self.current_config = None
        self.status_message = ""
        self.status_style = "blue"
        self.notice_message = ""
        self.notice_style = "yellow"

    def _build_welcome_text(self, config=None) -> str:
        welcome_text = "[bold blue]🎵 YouTube to MP3 Downloader[/bold blue]\n"
        welcome_text += "[dim]Download YouTube videos and playlists as high-quality MP3 files[/dim]"
        welcome_text += f"\n[dim]Versão {__version__}[/dim]"

        if config:
            destination = resolve_download_directory(config, Path.cwd())
            destination_mode = get_download_mode_label(config, Path.cwd())
            parallel_status = "🚀 Ativado" if config.get('parallel_downloads', False) else "⚪ Desativado"
            format_info = config.get('audio_format', 'mp3').upper()
            quality_info = config.get('audio_quality', '320')

            welcome_text += f"\n\n[bold]Configuração Atual:[/bold]"
            welcome_text += f"\n• Formato: [cyan]{format_info}[/cyan]|Qualidade: [cyan]{quality_info}[/cyan]"
            welcome_text += f"\n• Destino: [cyan]{destination_mode}[/cyan]|[dim]{destination}[/dim]"
            welcome_text += f"\n• Download Paralelo: {parallel_status}"
            welcome_text += f"\n[dim]Digite / para ver comandos rápidos[/dim]"

            if not config.get('parallel_downloads', False):
                welcome_text += f"\n[yellow]💡 Dica: Ative o download paralelo para playlists mais rápidas[/yellow]"
                welcome_text += f"\n[dim]   Use: yt-download --config[/dim]"

        return welcome_text

    def render_screen(self, config=None):
        if config is not None:
            self.current_config = config

        self.console.clear()
        welcome_text = self._build_welcome_text(self.current_config)
        self.console.print(Panel(welcome_text, border_style="blue"))

        if self.notice_message:
            self.console.print(Text(self.notice_message, style=self.notice_style))

        if self.status_message:
            self.console.print(Text(f"⏳ {self.status_message}", style=self.status_style))

    def show_welcome(self, config=None):
        self.status_message = ""
        self.notice_message = ""
        self.render_screen(config)

    def _render_url_prompt(self, buffer: str):
        self.status_message = ""
        self.notice_message = ""
        self.render_screen()
        sys.stdout.write(f"\n📎 Cole o link do YouTube: {buffer}")
        sys.stdout.flush()

    def get_url_input(self, commands: List[str] = None):
        if not sys.stdin.isatty():
            self.status_message = ""
            self.notice_message = ""
            self.render_screen()
            return Prompt.ask("\n[yellow]📎 Cole o link do YouTube[/yellow]")

        buffer = ""
        commands = commands or []

        with _InputReader() as reader:
            while True:
                self._render_url_prompt(buffer)
                key = reader.read_key()

                if key == "enter":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return buffer.strip()

                if key == "backspace":
                    buffer = buffer[:-1]
                    continue

                if key == "esc":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    raise KeyboardInterrupt

                if key == "/" and not buffer:
                    selected_command = self.choose_command(commands)
                    if not selected_command:
                        continue
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return {"type": "command", "value": selected_command}
                    continue

                if isinstance(key, str) and len(key) == 1 and key.isprintable():
                    buffer += key

    def show_url_info(self, info: Dict[str, Any]):
        if info['is_playlist']:
            self.notice_message = "✅ Playlist detectada!"
        else:
            self.notice_message = "✅ Vídeo único detectado!"
        self.notice_style = "green"
        self.render_screen()

    def get_mode_choice(self, config=None) -> str:
        self.status_message = ""
        self.render_screen(config)
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
        self.status_message = ""
        self.render_screen()
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
        self.status_message = ""
        self.render_screen()
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
        self.notice_message = f"🚀 Iniciando download | Modo: {mode.title()} | Formato: {format_type.upper()} | Qualidade: {quality}"
        self.notice_style = "green"
        self.render_screen()

    def show_progress(self, message: str):
        self.status_message = message
        self.status_style = "blue"
        self.render_screen()

    def show_warning(self, message: str):
        self.notice_message = f"⚠️  {message}"
        self.notice_style = "yellow"
        self.render_screen()

    def show_command_help(self, commands: List[str]):
        self.status_message = ""
        self.notice_message = ""
        self.render_screen()
        commands_text = "\n".join(f"[cyan]{command}[/cyan]" for command in commands)
        self.console.print("")
        self.console.print(Panel(commands_text, border_style="cyan", title="Comandos rápidos"))

    def choose_command(self, commands: List[str]):
        if not sys.stdin.isatty():
            self.show_command_help(commands)
            return None

        items = [command for command in commands if command.startswith("/")]
        selected_index = 0

        with _InputReader() as reader:
            while True:
                self.status_message = ""
                self.notice_message = ""
                self.render_screen()

                lines = ["[dim]↑/↓ navega • Enter executa • Esc volta[/dim]", ""]
                for index, item in enumerate(items):
                    if index == selected_index:
                        lines.append(f"[bold cyan]❯ {item}[/bold cyan]")
                    else:
                        lines.append(f"  {item}")

                self.console.print("")
                self.console.print(Panel("\n".join(lines), border_style="cyan", title="Comandos rápidos"))
                key = reader.read_key()

                if key == "up":
                    selected_index = (selected_index - 1) % len(items)
                elif key == "down":
                    selected_index = (selected_index + 1) % len(items)
                elif key == "enter":
                    return items[selected_index].split()[0]
                elif key == "esc":
                    return None

    def show_success(self, title: str, filename: str, file_size: float = None):
        self.status_message = ""
        self.notice_message = ""
        self.render_screen()
        rprint(f"\n[green]✅ Download concluído![/green]")
        rprint(f"[bold]Título:[/bold] {title}")
        rprint(f"[bold]Arquivo:[/bold] {filename}")
        if file_size is not None:
            rprint(f"[bold]Tamanho:[/bold] {file_size:.2f} MB")

    def show_error(self, error: str):
        self.status_message = ""
        self.notice_message = ""
        self.render_screen()
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
