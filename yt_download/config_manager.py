import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
from rich.text import Text

from .config import Config, DEFAULT_CONFIG, detect_system_downloads_path, resolve_download_directory

console = Console()


def _hard_clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


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
    VISIBLE_ITEMS = 5
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
        self.scroll_offset = 0

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
            "audio_quality": "(disponivel apenas para MP3)",
            "max_parallel_downloads": "(so vale quando downloads paralelos estiverem ativos)",
        }
        return help_map.get(key, "")

    def _ensure_visible(self):
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.VISIBLE_ITEMS:
            self.scroll_offset = self.selected_index - self.VISIBLE_ITEMS + 1

    def _render(self, cli=None):
        self._ensure_visible()
        if cli is not None:
            cli.show_welcome(self.config.settings)
        else:
            _hard_clear()

        effective_dir = resolve_download_directory(self.config.settings, Path.cwd())
        visible_keys = self.FIELD_ORDER[self.scroll_offset:self.scroll_offset + self.VISIBLE_ITEMS]
        lines: list[Text] = [
            Text("↑/↓ navega • ←/→ altera • Enter edita • Esc sai", style="dim"),
            Text(" "),
        ]

        if self.scroll_offset > 0:
            lines.append(Text("▲ Há mais opções acima", style="dim"))

        for key in visible_keys:
            index = self.FIELD_ORDER.index(key)
            label = self.LABELS[key]
            value = self._field_value(key)
            help_text = self._field_help(key)

            row = Text()
            if index == self.selected_index:
                row.append("❯ ", style="bold cyan")
                row.append(f"{label:<28}", style="bold white")
                row.append("  ")
                row.append(value, style="bold green")
            else:
                row.append("  ")
                row.append(f"{label:<28}", style="white")
                row.append("  ")
                row.append(value, style="green")

            if help_text:
                row.append("  ", style="white")
                row.append(help_text, style="dim")

            lines.append(row)
            lines.append(Text(""))

        if self.scroll_offset + self.VISIBLE_ITEMS < len(self.FIELD_ORDER):
            lines.append(Text("▼ Há mais opções abaixo", style="dim"))

        body = Text()
        for line in lines:
            body.append_text(line)
            body.append("\n")
        if lines:
            body = body[:-1]

        console.print("")
        console.print(Panel(body, border_style="cyan", title="Configurações", padding=(0, 1)))

    def _edit_selected_field(self):
        key = self.FIELD_ORDER[self.selected_index]

        if key == "download_location_mode":
            mode = self.config.get("download_location_mode")
            if mode == "system_downloads":
                detected = self.config.get("system_downloads_path", "").strip() or str(detect_system_downloads_path())
                _hard_clear()
                console.print(Panel(
                    "[bold blue]Editar pasta Downloads do sistema[/bold blue]\n"
                    "[dim]Deixe vazio para usar a pasta detectada automaticamente.[/dim]",
                    border_style="blue",
                ))
                new_value = console.input(f"\nCaminho [{detected}]: ").strip()
                self.config.set("system_downloads_path", new_value)
            elif mode == "custom_path":
                current = self.config.get("custom_download_path", "").strip() or str(Path.cwd())
                _hard_clear()
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
            _hard_clear()
            new_value = console.input(f"Tentativas máximas [{current}]: ").strip()
            if new_value.isdigit():
                self.config.set(key, max(1, min(10, int(new_value))))
            return

        if key == "max_parallel_downloads":
            current = str(self.config.get(key))
            _hard_clear()
            new_value = console.input(f"Máximo de downloads simultâneos [{current}]: ").strip()
            if new_value.isdigit():
                self.config.set(key, max(1, min(5, int(new_value))))

    def interactive_config(self, cli=None):
        """Interface interativa com navegação por teclas."""
        if not sys.stdin.isatty():
            rprint("[red]❌ O painel interativo precisa de um terminal TTY.[/red]")
            return

        with _KeyReader() as reader:
            while True:
                self._render(cli)
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

        if cli is not None:
            cli.show_welcome(self.config.settings)
        else:
            _hard_clear()
        rprint("[green]✅ Configurações salvas.[/green]")

    def reset_config(self):
        """Restaura configurações padrão."""
        _hard_clear()
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
