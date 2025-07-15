from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from .config import Config

console = Console()

class ConfigManager:
    def __init__(self):
        self.config = Config()
    
    def show_current_config(self):
        """Mostra a configuração atual."""
        table = Table(title="⚙️  Configuração Atual")
        table.add_column("Configuração", style="cyan")
        table.add_column("Valor", style="white")
        table.add_column("Descrição", style="dim")
        
        config_descriptions = {
            "audio_format": "Formato de áudio padrão",
            "audio_quality": "Qualidade de áudio padrão",
            "download_thumbnails": "Baixar thumbnails dos vídeos",
            "create_playlist_folder": "Criar pasta para playlists",
            "auto_mode_quality": "Qualidade no modo automático",
            "history_enabled": "Salvar histórico de downloads",
            "max_retries": "Tentativas máximas em caso de falha",
            "duplicate_action": "Ação para arquivos duplicados",
            "parallel_downloads": "Downloads paralelos em playlists",
            "max_parallel_downloads": "Máximo de downloads simultâneos",
            "log_level": "Nível de log do sistema"
        }
        
        for key, value in self.config.settings.items():
            description = config_descriptions.get(key, "")
            table.add_row(key, str(value), description)
        
        console.print(table)
    
    def interactive_config(self):
        """Interface interativa para configuração."""
        rprint("\n[bold blue]⚙️  Configuração Interativa[/bold blue]")
        rprint("[dim]Pressione Enter para manter o valor atual[/dim]\n")
        
        # Formato de áudio
        current_format = self.config.get('audio_format')
        new_format = Prompt.ask(
            f"Formato de áudio [{current_format}]",
            choices=["mp3", "m4a", "ogg", "wav"],
            default=current_format
        )
        self.config.set('audio_format', new_format)
        
        # Qualidade de áudio (só para MP3)
        if new_format == "mp3":
            current_quality = self.config.get('audio_quality')
            new_quality = Prompt.ask(
                f"Qualidade de áudio [{current_quality}]",
                choices=["128", "192", "256", "320"],
                default=current_quality
            )
            self.config.set('audio_quality', new_quality)
        
        # Download de thumbnails (como capa embutida)
        rprint("\n[bold yellow]🖼️ Thumbnails como Capa[/bold yellow]")
        rprint("[dim]Embute a imagem do YouTube como capa no arquivo de áudio (MP3/M4A)[/dim]")
        
        current_thumbnails = self.config.get('download_thumbnails')
        new_thumbnails = Confirm.ask(
            f"Embuter thumbnail como capa? [{'Sim' if current_thumbnails else 'Não'}]",
            default=current_thumbnails
        )
        self.config.set('download_thumbnails', new_thumbnails)
        
        # Pastas para playlists
        current_folder = self.config.get('create_playlist_folder')
        new_folder = Confirm.ask(
            f"Criar pasta para playlists? [{'Sim' if current_folder else 'Não'}]",
            default=current_folder
        )
        self.config.set('create_playlist_folder', new_folder)
        
        # Número de tentativas
        current_retries = self.config.get('max_retries')
        new_retries = Prompt.ask(
            f"Tentativas máximas em caso de falha [{current_retries}]",
            default=str(current_retries)
        )
        try:
            self.config.set('max_retries', int(new_retries))
        except ValueError:
            rprint("[red]Valor inválido, mantendo configuração anterior[/red]")
        
        # Ação para duplicatas
        current_duplicate = self.config.get('duplicate_action')
        new_duplicate = Prompt.ask(
            f"Ação para arquivos duplicados [{current_duplicate}]",
            choices=["skip", "overwrite", "rename"],
            default=current_duplicate
        )
        self.config.set('duplicate_action', new_duplicate)
        
        # Downloads paralelos (destacado)
        rprint("\n[bold yellow]🚀 Downloads Paralelos (Recomendado)[/bold yellow]")
        rprint("[dim]Acelera significativamente o download de playlists (até 3x mais rápido)[/dim]")
        
        current_parallel = self.config.get('parallel_downloads')
        new_parallel = Confirm.ask(
            f"Ativar downloads paralelos? [{'Sim' if current_parallel else 'Não'}]",
            default=current_parallel
        )
        self.config.set('parallel_downloads', new_parallel)
        
        if new_parallel:
            rprint("[green]✅ Ótima escolha! Suas playlists serão baixadas muito mais rapidamente.[/green]")
            current_max_parallel = self.config.get('max_parallel_downloads')
            new_max_parallel = Prompt.ask(
                f"Máximo de downloads simultâneos (1-5) [{current_max_parallel}]",
                default=str(current_max_parallel)
            )
            try:
                max_val = max(1, min(5, int(new_max_parallel)))
                self.config.set('max_parallel_downloads', max_val)
                if max_val != int(new_max_parallel):
                    rprint(f"[yellow]Valor ajustado para {max_val} (recomendado)[/yellow]")
            except ValueError:
                rprint("[red]Valor inválido, mantendo configuração anterior[/red]")
        else:
            rprint("[yellow]💡 Dica: Downloads paralelos aceleram muito o processo de playlists[/yellow]")
        
        # Nível de log
        current_log = self.config.get('log_level')
        new_log = Prompt.ask(
            f"Nível de log [{current_log}]",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default=current_log
        )
        self.config.set('log_level', new_log)
        
        rprint("\n[green]✅ Configuração salva com sucesso![/green]")
    
    def reset_config(self):
        """Restaura configurações padrão."""
        if Confirm.ask("\n[red]⚠️  Restaurar todas as configurações para o padrão?[/red]"):
            from .config import DEFAULT_CONFIG
            for key, value in DEFAULT_CONFIG.items():
                self.config.set(key, value)
            rprint("[green]✅ Configurações restauradas para o padrão![/green]")
        else:
            rprint("[yellow]Operação cancelada[/yellow]")
    
    def set_config_value(self, key: str, value: str):
        """Define um valor específico de configuração."""
        try:
            # Converter valores booleanos
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            # Converter valores numéricos
            elif value.isdigit():
                value = int(value)
            
            self.config.set(key, value)
            rprint(f"[green]✅ {key} = {value}[/green]")
        except Exception as e:
            rprint(f"[red]❌ Erro ao definir configuração: {e}[/red]")