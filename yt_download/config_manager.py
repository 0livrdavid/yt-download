import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from .config import Config, DEFAULT_CONFIG, detect_system_downloads_path, resolve_download_directory

console = Console()


class _KeyReader:
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

    class _SuspendContext:
        def __init__(self, reader):
            self.reader = reader

        def __enter__(self):
            self.reader.suspend()

        def __exit__(self, exc_type, exc, tb):
            self.reader.resume()

    def suspend_input(self):
        return self._SuspendContext(self)

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
        return first


class ConfigManager:
    FIELD_ORDER = [
        "audio_format",
        "audio_quality",
        "download_location_mode",
        "download_thumbnails",
        "create_playlist_folder",
        "auto_mode_quality",
        "history_enabled",
        "max_retries",
        "duplicate_action",
        "parallel_downloads",
        "max_parallel_downloads",
        "log_level",
    ]

    LABELS = {
        "audio_format": "Formato de áudio",
        "audio_quality": "Qualidade de áudio",
        "download_location_mode": "Destino dos downloads",
        "download_thumbnails": "Thumbnail como capa",
        "create_playlist_folder": "Criar pasta para playlists",
        "auto_mode_quality": "Qualidade no modo automático",
        "history_enabled": "Salvar histórico",
        "max_retries": "Máximo de tentativas",
        "duplicate_action": "Ao encontrar duplicados",
        "parallel_downloads": "Downloads paralelos",
        "max_parallel_downloads": "Máximo simultâneo",
        "log_level": "Nível de log",
    }

    OPTIONS = {
        "audio_format": ["mp3", "m4a", "ogg", "wav"],
        "audio_quality": ["128", "192", "256", "320"],
        "download_location_mode": ["current_dir", "system_downloads", "custom_path"],
        "download_thumbnails": [False, True],
        "create_playlist_folder": [False, True],
        "auto_mode_quality": ["best", "worst"],
        "history_enabled": [False, True],
        "max_retries": list(range(1, 11)),
        "duplicate_action": ["skip", "overwrite", "rename"],
        "parallel_downloads": [False, True],
        "max_parallel_downloads": [1, 2, 3, 4, 5],
        "log_level": ["DEBUG", "INFO", "WARNING", "ERROR"],
    }

    def __init__(self):
        self.config = Config()
        self.selected_index = 0

    def _next_value(self, key: str, direction: int):
        if key == "audio_quality" and self.config.get("audio_format") != "mp3":
            return
        if key == "max_parallel_downloads" and not self.config.get("parallel_downloads"):
            return

        options = self.OPTIONS[key]
        current = self.config.get(key)
        try:
            index = options.index(current)
        except ValueError:
            index = 0

        new_index = (index + direction) % len(options)
        self.config.set(key, options[new_index])

        if key == "download_location_mode" and self.config.get("custom_download_path") == "":
            if self.config.get("download_location_mode") == "custom_path":
                self.config.set("custom_download_path", str(Path.cwd()))

    def _bool_label(self, value: bool) -> str:
        return "Sim" if value else "Não"

    def _download_mode_display(self) -> str:
        mode = self.config.get("download_location_mode")
        if mode == "system_downloads":
            path = self.config.get("system_downloads_path", "").strip() or str(detect_system_downloads_path())
            return f"Downloads do sistema ({path})"
        if mode == "custom_path":
            path = self.config.get("custom_download_path", "").strip() or str(Path.cwd())
            return f"Pasta personalizada ({path})"
        return "Pasta atual"

    def _field_value(self, key: str) -> str:
        value = self.config.get(key)
        if key in {"download_thumbnails", "create_playlist_folder", "history_enabled", "parallel_downloads"}:
            return self._bool_label(bool(value))
        if key == "download_location_mode":
            return self._download_mode_display()
        if key == "audio_quality" and self.config.get("audio_format") != "mp3":
            return "N/A para este formato"
        if key == "max_parallel_downloads" and not self.config.get("parallel_downloads"):
            return "Desativado"
        return str(value)

    def _field_help(self, key: str) -> str:
        help_map = {
            "download_location_mode": "Use ←/→ para trocar o modo e Enter para editar caminhos",
            "audio_quality": "Disponível apenas para MP3",
            "max_parallel_downloads": "Só vale quando downloads paralelos estiverem ativos",
        }
        return help_map.get(key, "")

    def _render(self):
        console.clear()
        effective_dir = resolve_download_directory(self.config.settings, Path.cwd())

        header = (
            "[bold blue]⚙️ Configurações[/bold blue]\n"
            "[dim]↑/↓ navega • ←/→ altera • Enter edita opções especiais • Esc sai[/dim]\n"
            f"[dim]Destino efetivo agora: {effective_dir}[/dim]"
        )
        console.print(Panel(header, border_style="blue"))
        lines = []
        for index, key in enumerate(self.FIELD_ORDER):
            label = self.LABELS[key]
            value = self._field_value(key)
            help_text = self._field_help(key)
            if index == self.selected_index:
                prefix = "[bold cyan]❯[/bold cyan]"
                label_text = f"[bold]{label}[/bold]"
                value_text = f"[bold green]{value}[/bold green]"
            else:
                prefix = " "
                label_text = label
                value_text = f"[green]{value}[/green]"

            line = f"{prefix} {label_text}: {value_text}"
            if help_text:
                line += f"\n    [dim]{help_text}[/dim]"
            lines.append(line)

        console.print(Panel("\n".join(lines), border_style="cyan", title="Opções"))

    def _edit_selected_field(self):
        key = self.FIELD_ORDER[self.selected_index]

        if key == "download_location_mode":
            mode = self.config.get("download_location_mode")
            if mode == "system_downloads":
                detected = self.config.get("system_downloads_path", "").strip() or str(detect_system_downloads_path())
                console.clear()
                console.print(Panel(
                    "[bold blue]Editar pasta Downloads do sistema[/bold blue]\n"
                    "[dim]Deixe vazio para usar a pasta detectada automaticamente.[/dim]",
                    border_style="blue",
                ))
                new_value = console.input(f"\nCaminho [{detected}]: ").strip()
                self.config.set("system_downloads_path", new_value)
            elif mode == "custom_path":
                current = self.config.get("custom_download_path", "").strip() or str(Path.cwd())
                console.clear()
                console.print(Panel(
                    "[bold blue]Editar pasta personalizada[/bold blue]\n"
                    "[dim]Informe o caminho completo da pasta onde os arquivos serão salvos.[/dim]",
                    border_style="blue",
                ))
                new_value = console.input(f"\nCaminho [{current}]: ").strip()
                if new_value:
                    self.config.set("custom_download_path", str(Path(new_value).expanduser()))
            return

        if key == "max_retries":
            current = str(self.config.get(key))
            console.clear()
            new_value = console.input(f"Tentativas máximas [{current}]: ").strip()
            if new_value.isdigit():
                self.config.set(key, max(1, min(10, int(new_value))))
            return

        if key == "max_parallel_downloads":
            current = str(self.config.get(key))
            console.clear()
            new_value = console.input(f"Máximo de downloads simultâneos [{current}]: ").strip()
            if new_value.isdigit():
                self.config.set(key, max(1, min(5, int(new_value))))

    def interactive_config(self):
        """Interface interativa com navegação por teclas."""
        if not sys.stdin.isatty():
            rprint("[red]❌ O painel interativo precisa de um terminal TTY.[/red]")
            return

        with _KeyReader() as reader:
            while True:
                self._render()
                key = reader.read_key()

                if key == "up":
                    self.selected_index = (self.selected_index - 1) % len(self.FIELD_ORDER)
                elif key == "down":
                    self.selected_index = (self.selected_index + 1) % len(self.FIELD_ORDER)
                elif key == "left":
                    self._next_value(self.FIELD_ORDER[self.selected_index], -1)
                elif key == "right":
                    self._next_value(self.FIELD_ORDER[self.selected_index], 1)
                elif key == "enter":
                    with reader.suspend_input():
                        self._edit_selected_field()
                elif key == "esc":
                    break

        console.clear()
        rprint("[green]✅ Configurações salvas.[/green]")

    def reset_config(self):
        """Restaura configurações padrão."""
        console.clear()
        choice = console.input("[red]Restaurar todas as configurações para o padrão? [y/N]: [/red]").strip().lower()
        if choice == "y":
            self.config.save_config(DEFAULT_CONFIG.copy())
            self.config = Config()
            rprint("[green]✅ Configurações restauradas para o padrão![/green]")
        else:
            rprint("[yellow]Operação cancelada[/yellow]")

    def set_config_value(self, key: str, value: str):
        """Define um valor específico de configuração."""
        try:
            if value.lower() in ("true", "false"):
                parsed_value = value.lower() == "true"
            elif value.isdigit():
                parsed_value = int(value)
            else:
                parsed_value = value

            self.config.set(key, parsed_value)
            rprint(f"[green]✅ {key} = {parsed_value}[/green]")
        except Exception as e:
            rprint(f"[red]❌ Erro ao definir configuração: {e}[/red]")
