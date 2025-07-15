#!/usr/bin/env python3

import sys
import argparse
from rich import print as rprint
from .cli import CLI
from .config import Config
from .config_manager import ConfigManager
from .url_validator import URLValidator
from .downloader import YTDownloader
from .updater import GitHubUpdater

def create_parser():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and playlists as MP3 files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yb-download-mp3                          # Interactive mode
  yb-download-mp3 --url "youtube_url"      # Quick download with default settings
  yb-download-mp3 --history                # Show download history
  yb-download-mp3 --stats                  # Show download statistics
  yb-download-mp3 --reset                  # Clear download history
  yb-download-mp3 --config                 # Configure application settings
  yb-download-mp3 --check                  # Check system requirements
  yb-download-mp3 --update                 # Check for updates and install
        """
    )
    
    parser.add_argument('--url', '-u', type=str, help='YouTube URL to download')
    parser.add_argument('--format', '-f', choices=['mp3', 'm4a', 'ogg', 'wav'], 
                       default='mp3', help='Audio format (default: mp3)')
    parser.add_argument('--quality', '-q', type=str, default='320',
                       help='Audio quality (default: 320 for mp3, best for others)')
    parser.add_argument('--auto', '-a', action='store_true',
                       help='Auto mode: use best quality MP3')
    parser.add_argument('--history', action='store_true',
                       help='Show download history')
    parser.add_argument('--stats', action='store_true',
                       help='Show download statistics')
    parser.add_argument('--reset', action='store_true',
                       help='Reset (clear) download history')
    parser.add_argument('--config', action='store_true',
                       help='Configure application settings')
    parser.add_argument('--check', action='store_true',
                       help='Check system requirements')
    parser.add_argument('--update', action='store_true',
                       help='Check for updates and install if available')
    parser.add_argument('--version', '-v', action='version', version='1.0.0')
    
    return parser

def handle_download(cli, config, url, format_type="mp3", quality="320", auto_mode=False):
    try:
        # Inicializar downloader com configuração
        downloader = YTDownloader(progress_callback=cli.show_progress, config=config.settings)
        
        # Verificar requisitos do sistema
        cli.show_progress("Verificando sistema...")
        system_check = downloader.check_system_requirements()
        
        if not system_check['all_ok']:
            if not system_check['ffmpeg']['installed']:
                cli.show_error(f"FFmpeg: {system_check['ffmpeg']['error']}")
                rprint(f"[yellow]💡 {system_check['ffmpeg']['suggestion']}[/yellow]")
                return False
            if not system_check['network']:
                cli.show_error("Sem conexão com a internet")
                return False
        
        # Validar URL
        cli.show_progress("Validando URL...")
        url_info = URLValidator.validate_and_classify(url)
        
        if not url_info['valid']:
            cli.show_error(url_info['error'])
            return False
        
        # Usar URL limpa
        url = url_info['url']
        cli.show_url_info(url_info)
        
        # Se não for modo automático, perguntar configurações
        if not auto_mode:
            mode = cli.get_mode_choice()
            if mode == "manual":
                format_type = cli.get_format_choice()
                quality = cli.get_quality_choice(format_type)
        else:
            mode = "auto"
        
        # Mostrar informações do download
        cli.show_download_start(mode, format_type, quality)
        
        # Realizar download
        result = downloader.download(
            url=url,
            format_type=format_type,
            quality=quality,
            is_playlist=url_info['is_playlist']
        )
        
        # Mostrar resultado
        if result['type'] == 'playlist':
            successful = result['successful']
            total = result['total']
            rprint(f"\n[green]✅ Playlist '{result['title']}' processada![/green]")
            rprint(f"[cyan]Downloads bem-sucedidos: {successful}/{total}[/cyan]")
            
            if result['results']:
                failed = [r for r in result['results'] if r['status'] == 'failed']
                if failed:
                    rprint(f"\n[yellow]⚠️  Falhas ({len(failed)}):[/yellow]")
                    for fail in failed[:5]:  # Mostrar apenas os primeiros 5
                        rprint(f"  • {fail['title']}")
        else:
            cli.show_success(result['title'], result['filename'])
        
        return True
        
    except KeyboardInterrupt:
        rprint("\n[yellow]⚠️  Download cancelado pelo usuário[/yellow]")
        return False
    except Exception as e:
        cli.show_error(str(e))
        return False

def interactive_mode():
    cli = CLI()
    config = Config()
    
    cli.show_welcome()
    
    try:
        while True:
            try:
                # Obter URL
                url = cli.get_url_input()
                
                if not url.strip():
                    cli.show_error("URL não pode estar vazia")
                    continue
                
                # Processar download
                success = handle_download(cli, config, url)
                
                if success:
                    # Perguntar se quer continuar
                    if not cli.confirm_continue():
                        break
                else:
                    # Em caso de erro, perguntar se quer tentar novamente
                    if not cli.confirm_continue():
                        break
                        
            except KeyboardInterrupt:
                rprint("\n[yellow]👋 Até logo![/yellow]")
                break
            except Exception as e:
                cli.show_error(f"Erro inesperado: {str(e)}")
                if not cli.confirm_continue():
                    break
                    
    except KeyboardInterrupt:
        rprint("\n[yellow]👋 Até logo![/yellow]")

def main():
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        cli = CLI()
        config = Config()
        downloader = YTDownloader()
        
        # Mostrar histórico
        if args.history:
            history = downloader.get_history()
            cli.show_history(history)
            return
        
        # Mostrar estatísticas
        if args.stats:
            stats = downloader.get_stats()
            cli.show_stats(stats)
            return
        
        # Reset do histórico
        if args.reset:
            if cli.show_reset_confirmation():
                downloader.reset_history()
                cli.show_reset_success()
            else:
                rprint("\n[yellow]Operação cancelada[/yellow]")
            return
        
        # Configuração
        if args.config:
            config_manager = ConfigManager()
            config_manager.interactive_config()
            return
        
        # Verificação do sistema
        if args.check:
            system_check = downloader.check_system_requirements()
            
            rprint("\n[bold blue]🔍 Verificação do Sistema[/bold blue]\n")
            
            # FFmpeg
            if system_check['ffmpeg']['installed']:
                rprint(f"[green]✅ FFmpeg: {system_check['ffmpeg']['version']} - OK[/green]")
            else:
                rprint(f"[red]❌ FFmpeg: {system_check['ffmpeg']['error']}[/red]")
                rprint(f"[yellow]💡 {system_check['ffmpeg']['suggestion']}[/yellow]")
            
            # YouTube
            youtube_info = system_check['youtube']
            if youtube_info['all_working']:
                rprint(f"[green]✅ YouTube: {youtube_info['overall_status'].title()}[/green]")
                # Mostrar latências dos endpoints
                for endpoint, data in youtube_info['endpoints'].items():
                    if data['status'] == 'online':
                        endpoint_name = endpoint.split('//')[1].split('.')[0]
                        rprint(f"  [dim]• {endpoint_name}: {data['response_time']}ms[/dim]")
            else:
                rprint(f"[red]❌ YouTube: {youtube_info['overall_status'].title()}[/red]")
                # Mostrar quais endpoints falharam
                for endpoint, data in youtube_info['endpoints'].items():
                    if data['status'] == 'offline':
                        endpoint_name = endpoint.split('//')[1].split('.')[0]
                        rprint(f"  [dim]• {endpoint_name}: offline[/dim]")
            
            # Status geral
            if system_check['all_ok']:
                rprint("\n[green]🎉 Sistema pronto para uso![/green]")
            else:
                rprint("\n[red]⚠️  Resolva os problemas acima antes de usar[/red]")
            
            return
        
        # Update
        if args.update:
            updater = GitHubUpdater()
            updater.interactive_update()
            return
        
        # Download direto via argumentos
        if args.url:
            format_type = args.format
            quality = args.quality
            auto_mode = args.auto
            
            success = handle_download(cli, config, args.url, format_type, quality, auto_mode)
            sys.exit(0 if success else 1)
        
        # Modo interativo
        interactive_mode()
        
    except KeyboardInterrupt:
        rprint("\n[yellow]👋 Até logo![/yellow]")
        sys.exit(0)
    except Exception as e:
        rprint(f"\n[red]❌ Erro fatal: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()