import subprocess
import sys
import re
from typing import Dict, Any, Optional

import requests
from rich import print as rprint
from rich.prompt import Confirm

from . import __version__


class GitHubUpdater:
    def __init__(self, repo_url: str = "https://github.com/0livrdavid/yt-download.git"):
        self.repo_url = repo_url
        clean_url = repo_url.removesuffix(".git")
        repo_path = clean_url.replace("https://github.com/", "")
        self.repo_path = repo_path
        self.api_url = f"https://api.github.com/repos/{repo_path}"
        self.raw_base_url = f"https://raw.githubusercontent.com/{repo_path}/main"
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
        """Obtém informações do último commit da branch main."""
        try:
            response = requests.get(f"{self.api_url}/commits/main", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            rprint(f"[red]Erro ao verificar commits: {e}[/red]")
            return None

    def get_latest_version_from_main(self) -> Optional[str]:
        """Lê a versão publicada no arquivo __init__.py da branch main."""
        try:
            response = requests.get(f"{self.raw_base_url}/yt_download/__init__.py", timeout=10)
            if response.status_code == 200:
                match = re.search(r'__version__\s*=\s*"([^"]+)"', response.text)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            rprint(f"[red]Erro ao verificar versão da main: {e}[/red]")
            return None

    def compare_versions(self, latest_version: str) -> str:
        """Compara versões e retorna status."""
        latest_clean = latest_version.lstrip("v")
        current_clean = self.current_version.lstrip("v")

        try:
            latest_parts = tuple(map(int, latest_clean.split(".")))
            current_parts = tuple(map(int, current_clean.split(".")))

            if latest_parts > current_parts:
                return "outdated"
            if latest_parts < current_parts:
                return "ahead"
            return "current"
        except ValueError:
            if latest_clean != current_clean:
                return "different"
            return "current"

    def check_for_updates(self) -> Dict[str, Any]:
        """Verifica se há atualizações disponíveis."""
        rprint("[blue]🔍 Verificando atualizações...[/blue]")

        latest_commit = self.get_latest_commit()
        latest_main_version = self.get_latest_version_from_main()
        if latest_main_version:
            status = self.compare_versions(latest_main_version)
            return {
                "update_available": status == "outdated",
                "latest_version": latest_main_version,
                "current_version": self.current_version,
                "status": status,
                "commit_info": latest_commit,
                "source": "main",
            }

        latest_release = self.get_latest_release()
        if latest_release:
            latest_version = latest_release["tag_name"]
            status = self.compare_versions(latest_version)
            return {
                "update_available": status == "outdated",
                "latest_version": latest_version,
                "current_version": self.current_version,
                "status": status,
                "release_info": latest_release,
                "source": "release",
            }

        return {
            "update_available": False,
            "error": "Não foi possível verificar atualizações",
        }

    def install_latest_from_git(self) -> bool:
        """Atualiza o pacote instalado usando pip + GitHub."""
        install_target = f"git+{self.repo_url}"
        install_cmd = [sys.executable, "-m", "pip", "install", "--user", "--upgrade", install_target]

        try:
            rprint("[blue]📦 Instalando versão mais recente a partir do GitHub...[/blue]")
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                error_output = result.stderr.strip() or result.stdout.strip() or "Erro desconhecido"
                rprint(f"[red]Erro na atualização: {error_output}[/red]")
                return False

            rprint("[green]✅ Atualização instalada com sucesso![/green]")
            return True
        except Exception as e:
            rprint(f"[red]Erro durante atualização: {e}[/red]")
            return False

    def interactive_update(self) -> bool:
        """Interface interativa para atualização."""
        update_info = self.check_for_updates()

        if "error" in update_info:
            rprint(f"[red]❌ {update_info['error']}[/red]")
            return False

        if not update_info["update_available"]:
            if update_info["status"] == "current":
                rprint(f"[green]✅ Você já tem a versão mais recente ({self.current_version})[/green]")
            elif update_info["status"] == "ahead":
                rprint(
                    f"[yellow]🚀 Sua versão ({self.current_version}) é mais nova que a oficial ({update_info['latest_version']})[/yellow]"
                )
            return True

        if update_info["source"] == "main":
            commit = update_info.get("commit_info")
            rprint("\n[bold blue]🎉 Nova versão disponível na branch main![/bold blue]")
            rprint(f"[cyan]Atual:[/cyan] {update_info['current_version']}")
            rprint(f"[green]Nova:[/green] {update_info['latest_version']}")
            if commit:
                rprint(f"[dim]Commit: {commit['sha'][:8]}[/dim]")
                rprint(f"[dim]{commit['commit']['message'].splitlines()[0]}[/dim]")
        elif update_info["source"] == "release":
            release = update_info["release_info"]
            rprint("\n[bold blue]🎉 Nova versão disponível![/bold blue]")
            rprint(f"[cyan]Atual:[/cyan] {update_info['current_version']}")
            rprint(f"[green]Nova:[/green] {update_info['latest_version']}")
            rprint(f"[yellow]Lançada em:[/yellow] {release['published_at'][:10]}")

            if release.get("body"):
                rprint("\n[bold]📋 Novidades:[/bold]")
                description = release["body"][:300]
                if len(release["body"]) > 300:
                    description += "..."
                rprint(f"[dim]{description}[/dim]")
        if Confirm.ask("\n[yellow]Deseja instalar a atualização?[/yellow]"):
            success = self.install_latest_from_git()
            if success:
                rprint("\n[green]🎉 Atualização concluída! Reinicie o terminal para usar a nova versão.[/green]")
                return True

            rprint("\n[red]❌ Falha na atualização. Tente novamente ou instale manualmente.[/red]")
            return False

        rprint("\n[yellow]Atualização cancelada[/yellow]")
        return False
