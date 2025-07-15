import os
import sys
import subprocess
import tempfile
import shutil
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from rich import print as rprint
from rich.prompt import Confirm
from . import __version__

class GitHubUpdater:
    def __init__(self, repo_url: str = "https://github.com/0livrdavid/yt-download-mp3.git"):
        self.repo_url = repo_url
        # Corrigir formação da URL da API
        clean_url = repo_url.replace(".git", "")
        repo_path = clean_url.replace("https://github.com/", "")
        self.api_url = f"https://api.github.com/repos/{repo_path}"
        self.current_version = __version__
        
    def get_latest_release(self) -> Optional[Dict[str, Any]]:
        """Obtém informações da última release do GitHub."""
        try:
            response = requests.get(f"{self.api_url}/releases/latest", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            rprint(f"[red]Erro ao verificar releases: {e}[/red]")
            return None
    
    def get_latest_commit(self) -> Optional[Dict[str, Any]]:
        """Obtém informações do último commit."""
        try:
            response = requests.get(f"{self.api_url}/commits/main", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            rprint(f"[red]Erro ao verificar commits: {e}[/red]")
            return None
    
    def compare_versions(self, latest_version: str) -> str:
        """Compara versões e retorna status."""
        # Remover 'v' se existir
        latest_clean = latest_version.lstrip('v')
        current_clean = self.current_version.lstrip('v')
        
        try:
            # Converter para tuplas de números para comparação
            latest_parts = tuple(map(int, latest_clean.split('.')))
            current_parts = tuple(map(int, current_clean.split('.')))
            
            if latest_parts > current_parts:
                return "outdated"
            elif latest_parts < current_parts:
                return "ahead"
            else:
                return "current"
        except ValueError:
            # Se não conseguir comparar, usar comparação de string
            if latest_clean != current_clean:
                return "different"
            return "current"
    
    def check_for_updates(self) -> Dict[str, Any]:
        """Verifica se há atualizações disponíveis."""
        rprint("[blue]🔍 Verificando atualizações...[/blue]")
        
        # Tentar obter última release
        latest_release = self.get_latest_release()
        if latest_release:
            latest_version = latest_release['tag_name']
            status = self.compare_versions(latest_version)
            
            return {
                'update_available': status == "outdated",
                'latest_version': latest_version,
                'current_version': self.current_version,
                'status': status,
                'release_info': latest_release,
                'source': 'release'
            }
        
        # Se não há releases, verificar commits
        latest_commit = self.get_latest_commit()
        if latest_commit:
            return {
                'update_available': True,  # Assumir que há updates se há commits
                'latest_version': latest_commit['sha'][:8],
                'current_version': self.current_version,
                'status': 'commit_available',
                'commit_info': latest_commit,
                'source': 'commit'
            }
        
        return {
            'update_available': False,
            'error': 'Não foi possível verificar atualizações'
        }
    
    def download_and_install_update(self) -> bool:
        """Baixa e instala a atualização."""
        try:
            rprint("[blue]📦 Baixando atualização...[/blue]")
            
            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Clonar repositório
                clone_result = subprocess.run([
                    'git', 'clone', self.repo_url, str(temp_path / 'yt-download-mp3')
                ], capture_output=True, text=True)
                
                if clone_result.returncode != 0:
                    rprint(f"[red]Erro ao clonar repositório: {clone_result.stderr}[/red]")
                    return False
                
                repo_path = temp_path / 'yt-download-mp3'
                
                # Verificar se tem pip
                pip_cmd = 'pip3' if shutil.which('pip3') else 'pip'
                
                rprint("[blue]🔧 Instalando atualização...[/blue]")
                
                # Instalar do repositório clonado
                install_result = subprocess.run([
                    pip_cmd, 'install', '-e', str(repo_path)
                ], capture_output=True, text=True)
                
                if install_result.returncode != 0:
                    rprint(f"[red]Erro na instalação: {install_result.stderr}[/red]")
                    return False
                
                rprint("[green]✅ Atualização instalada com sucesso![/green]")
                return True
                
        except Exception as e:
            rprint(f"[red]Erro durante atualização: {e}[/red]")
            return False
    
    def interactive_update(self) -> bool:
        """Interface interativa para atualização."""
        update_info = self.check_for_updates()
        
        if 'error' in update_info:
            rprint(f"[red]❌ {update_info['error']}[/red]")
            return False
        
        if not update_info['update_available']:
            if update_info['status'] == 'current':
                rprint(f"[green]✅ Você já tem a versão mais recente ({self.current_version})[/green]")
            elif update_info['status'] == 'ahead':
                rprint(f"[yellow]🚀 Sua versão ({self.current_version}) é mais nova que a oficial ({update_info['latest_version']})[/yellow]")
            return True
        
        # Mostrar informações da atualização
        if update_info['source'] == 'release':
            release = update_info['release_info']
            rprint(f"\n[bold blue]🎉 Nova versão disponível![/bold blue]")
            rprint(f"[cyan]Atual:[/cyan] {update_info['current_version']}")
            rprint(f"[green]Nova:[/green] {update_info['latest_version']}")
            rprint(f"[yellow]Lançada em:[/yellow] {release['published_at'][:10]}")
            
            if release.get('body'):
                rprint(f"\n[bold]📋 Novidades:[/bold]")
                # Limitar descrição a 300 caracteres
                description = release['body'][:300]
                if len(release['body']) > 300:
                    description += "..."
                rprint(f"[dim]{description}[/dim]")
        else:
            rprint(f"\n[bold blue]🔄 Atualizações disponíveis![/bold blue]")
            rprint(f"[cyan]Versão atual:[/cyan] {update_info['current_version']}")
            rprint(f"[green]Último commit:[/green] {update_info['latest_version']}")
        
        # Confirmar instalação
        if Confirm.ask("\n[yellow]Deseja instalar a atualização?[/yellow]"):
            success = self.download_and_install_update()
            if success:
                rprint("\n[green]🎉 Atualização concluída! Reinicie o terminal para usar a nova versão.[/green]")
                return True
            else:
                rprint("\n[red]❌ Falha na atualização. Tente novamente ou instale manualmente.[/red]")
                return False
        else:
            rprint("\n[yellow]Atualização cancelada[/yellow]")
            return False