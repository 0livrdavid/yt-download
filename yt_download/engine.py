"""Compatibilidade e atualização assistida do motor de download."""
import json
import re
import shutil
import subprocess
import sys
import time
from importlib.metadata import PackageNotFoundError, requires, version

import requests
from rich import print as rprint
from rich.prompt import Confirm

from .config import get_config_dir


def version_tuple(value):
    return tuple(int(part) for part in value.split('.'))


def runtime_options():
    """Usa apenas runtimes com a versão mínima suportada pelo EJS."""
    for name, minimum in [('deno', (2, 3, 0)), ('node', (22, 0, 0))]:
        executable = shutil.which(name)
        if not executable:
            continue
        try:
            result = subprocess.run([executable, '--version'], capture_output=True,
                                    text=True, timeout=3, check=True)
            match = re.search(r'\b(v?\d+\.\d+\.\d+)\b', result.stdout)
            if match and version_tuple(match[1].lstrip('v')) >= minimum:
                return {'js_runtimes': {name: {'path': executable}}}
        except (OSError, subprocess.SubprocessError):
            continue
    return {}


class EngineManager:
    def __init__(self):
        self.cache_path = get_config_dir() / 'engine_update.json'

    def check_latest(self, force=False):
        """Consulta no máximo diariamente; falhas de rede têm cache de uma hora."""
        now = time.time()
        if not force:
            try:
                cache = json.loads(self.cache_path.read_text(encoding='utf-8'))
                age = now - cache['checked_at']
                if 0 <= age < (86400 if cache.get('latest') else 3600):
                    return cache.get('latest')
            except (OSError, ValueError, KeyError, TypeError):
                pass
        latest = None
        try:
            response = requests.get('https://pypi.org/pypi/yt-dlp/json', timeout=3)
            response.raise_for_status()
            candidate = response.json()['info']['version']
            if re.fullmatch(r'\d+\.\d+\.\d+', candidate):
                latest = candidate
        except (requests.RequestException, ValueError, KeyError, TypeError):
            pass
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps({'checked_at': now, 'latest': latest}), encoding='utf-8')
        except OSError:
            pass
        return latest

    def diagnostics(self, check_updates=True):
        from yt_dlp.version import __version__
        warnings = []
        options = runtime_options()
        if not options:
            warnings.append('Instale Node.js 22+ ou Deno 2.3+ e deixe-o disponível no PATH.')
        try:
            ejs_version = version('yt-dlp-ejs')
            for requirement in requires('yt-dlp') or []:
                match = re.match(r'yt-dlp-ejs==([\d.]+)', requirement)
                if match and version_tuple(ejs_version) != version_tuple(match[1]):
                    warnings.append('yt-dlp-ejs incompatível com o motor instalado. Use --update-engine.')
                    ejs_version = None
                    break
        except PackageNotFoundError:
            ejs_version = None
            warnings.append('yt-dlp-ejs ausente. Use /update-engine ou yt-download --update-engine.')
        latest = self.check_latest() if check_updates else None
        if latest and version_tuple(latest) > version_tuple(__version__):
            warnings.append(f'yt-dlp desatualizado ({__version__} → {latest}). Use /update-engine ou --update-engine.')
        return {'version': __version__, 'ejs_version': ejs_version,
                'runtime': next(iter(options.get('js_runtimes', {})), None),
                'warnings': warnings, 'ready': bool(options) and bool(ejs_version)}

    def interactive_update(self):
        latest = self.check_latest(force=True)
        rprint(f'Motor yt-dlp: última versão consultada: {latest or "consulta indisponível"}')
        command = [sys.executable, '-m', 'pip', 'install', '--upgrade']
        if sys.prefix == sys.base_prefix:
            command.append('--user')
        command.append('yt-dlp[default]>=2026.3.17')
        rprint('Será atualizado o yt-dlp e suas dependências, incluindo yt-dlp-ejs, neste Python:')
        rprint(sys.executable)
        if not sys.stdin.isatty():
            rprint('[yellow]Execute --update-engine em um terminal interativo para confirmar.[/yellow]')
            return False
        if not Confirm.ask('Deseja instalar/atualizar essas dependências?', default=False):
            return False
        try:
            result = subprocess.run(command, check=False)
        except OSError as error:
            rprint(f'[red]Não foi possível executar pip: {error}[/red]')
            return False
        if result.returncode:
            rprint('[red]Atualização falhou. Confira a saída do pip acima.[/red]')
            return False
        rprint('[green]Motor atualizado. Encerre e abra novamente o yt-download antes de baixar.[/green]')
        return True


def compatibility_hint(error):
    message = str(error).lower()
    if any(term in message for term in ('403', 'signature', 'challenge', 'javascript', 'ejs')):
        return ('O YouTube recusou o acesso ou houve falha de compatibilidade. '
                'Use /update-engine ou yt-download --update-engine, reinicie o aplicativo '
                'e confira o Node/Deno com --check. Se persistir, pode haver restrição '
                'do vídeo ou bloqueio temporário; atualizar não garante resolver todo 403.')
    return None
