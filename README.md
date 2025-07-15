# 🎵 YouTube to MP3 Downloader

Uma ferramenta CLI **profissional** e **robusta** para baixar vídeos e playlists do YouTube como arquivos MP3 de alta qualidade, com recursos avançados de retry, downloads paralelos, auto-updater e muito mais.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 🏆 Diferenciais

**Por que escolher este downloader?**

| Recurso | Outros Tools | **YB-Download-MP3** |
|---------|--------------|---------------------|
| 📊 **Progresso** | "Baixando..." | ⚡ Velocidade + ETA + % |
| 🔄 **Falhas** | Erro = fim | 🛡️ 3 tentativas automáticas |
| ⚡ **Playlists** | Sequencial apenas | 🚀 Downloads paralelos |
| 📦 **Tamanho** | Estimativa/0MB | 📏 Cálculo real do arquivo |
| 🔧 **Config** | Arquivo manual | 🎛️ Interface interativa |
| 🔍 **Debug** | Sem logs | 📝 Sistema completo |
| 🔄 **Updates** | Manual | 🤖 Auto-updater GitHub |
| 🛡️ **Sistema** | Sem verificação | ✅ Testes FFmpeg + YouTube |

## ✨ Características

### 🎯 **Core Features**
- **🚀 Interface CLI intuitiva** com menus interativos coloridos
- **📱 Detecção automática** de vídeos únicos vs playlists
- **⚙️ Dois modos de operação**: Automático (rápido) e Manual (personalizável)
- **🎧 Múltiplos formatos**: MP3, M4A, OGG, WAV com qualidades configuráveis
- **📊 Histórico completo** com estatísticas detalhadas de downloads
- **⚡ Baseado em yt-dlp** (mais rápido e confiável que youtube-dl)

### 🔧 **Advanced Features**
- **📈 Progresso avançado** com velocidade, ETA e percentual em tempo real
- **🔄 Retry automático** com backoff exponencial (até 3 tentativas)
- **⚡ Downloads paralelos** para playlists (configurável)
- **🛡️ Validação robusta** de URLs com limpeza automática
- **🔍 Verificação de sistema** (FFmpeg + conectividade YouTube)
- **⚙️ Sistema de configuração** interativo completo

### 💎 **Professional Features**
- **🖼️ Download de thumbnails** dos vídeos (opcional)
- **📝 Sistema de logs** estruturado para debug
- **🔄 Auto-updater** integrado via GitHub
- **📁 Tratamento inteligente** de arquivos duplicados
- **🏷️ Sanitização automática** de nomes de arquivos
- **📊 Cálculo preciso** de tamanhos de arquivos

## 🛠️ Instalação

### Pré-requisitos

- Python 3.7 ou superior
- FFmpeg instalado no sistema

#### Instalando FFmpeg:

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
- Baixe de [ffmpeg.org](https://ffmpeg.org/download.html)
- Adicione ao PATH do sistema

### Instalação do YB-Download-MP3

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/yt-download-mp3.git
cd yt-download-mp3

# Instale as dependências
pip install -r requirements.txt

# Instale globalmente
pip install -e .
```

## 🚀 Como Usar

### Modo Interativo (Recomendado)

```bash
yb-download-mp3
```

O programa irá:
1. Solicitar o link do YouTube
2. Detectar automaticamente se é vídeo ou playlist
3. Perguntar o modo desejado (Automático ou Manual)
4. No modo manual, permitir escolher formato e qualidade
5. Realizar o download na pasta atual

### Linha de Comando Direta

```bash
# Download automático (MP3, melhor qualidade)
yb-download-mp3 --url "https://youtube.com/watch?v=..." --auto

# Download com formato específico
yb-download-mp3 --url "..." --format mp3 --quality 192

# Ver histórico com tamanhos reais
yb-download-mp3 --history

# Ver estatísticas detalhadas
yb-download-mp3 --stats

# Verificar se sistema está pronto (FFmpeg + YouTube)
yb-download-mp3 --check

# Configurar aplicação interativamente
yb-download-mp3 --config

# Verificar atualizações e instalar
yb-download-mp3 --update

# Limpar histórico de downloads
yb-download-mp3 --reset
```

## 📋 Exemplos de Uso

### Vídeo Único - Modo Automático
```bash
yb-download-mp3 --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --auto
```

### Playlist Completa - Modo Manual
```bash
yb-download-mp3
# Cole: https://www.youtube.com/playlist?list=...
# Escolha: 2 (Manual)
# Formato: 1 (MP3)
# Qualidade: 1 (320 kbps)
```

### Verificar Histórico
```bash
yb-download-mp3 --history
```

## 📁 Estrutura dos Arquivos

```
pasta-atual/
├── musica-individual.mp3
├── Playlist Name/
│   ├── 01 - Primeira Música.mp3
│   ├── 02 - Segunda Música.mp3
│   └── ...
├── yt_download_config.json    # Configurações
└── yt_download_history.json   # Histórico
```

## ⚙️ Configuração

### Interface Interativa
Use `yb-download-mp3 --config` para configurar via interface gráfica interativa.

### Arquivo de Configuração
O arquivo `yt_download_config.json` é criado automaticamente com:

```json
{
  "audio_format": "mp3",
  "audio_quality": "320",
  "download_thumbnails": false,
  "create_playlist_folder": true,
  "auto_mode_quality": "best",
  "history_enabled": true,
  "max_retries": 3,
  "duplicate_action": "skip",
  "parallel_downloads": false,
  "max_parallel_downloads": 3,
  "log_level": "INFO"
}
```

### Opções Disponíveis

| Configuração | Valores | Descrição |
|--------------|---------|-----------|
| `audio_format` | mp3, m4a, ogg, wav | Formato de áudio padrão |
| `audio_quality` | 128, 192, 256, 320 | Qualidade para MP3 (kbps) |
| `download_thumbnails` | true/false | Baixar thumbnails dos vídeos |
| `duplicate_action` | skip, overwrite, rename | Ação para arquivos duplicados |
| `parallel_downloads` | true/false | Downloads paralelos em playlists |
| `max_retries` | 1-10 | Tentativas em caso de falha |
| `log_level` | DEBUG, INFO, WARNING, ERROR | Nível de logging |

## 📊 Recursos do Histórico

### Informações Detalhadas
- **📅 Data e hora** de cada download
- **🎵 Título** completo do vídeo/música
- **⏱️ Duração** em minutos precisos
- **📦 Tamanho real** do arquivo em MB
- **🎧 Formato e qualidade** utilizados
- **🔗 URL original** do vídeo

### Estatísticas Avançadas
- **📈 Total de downloads** realizados
- **💾 Espaço ocupado** total em MB
- **⏰ Tempo total** de conteúdo baixado
- **📊 Tamanho médio** dos arquivos
- **📅 Data do último** download

### Comandos de Histórico
```bash
# Ver últimos 10 downloads com detalhes
yb-download-mp3 --history

# Ver estatísticas completas
yb-download-mp3 --stats

# Limpar todo o histórico
yb-download-mp3 --reset
```

## 🔧 Formatos Suportados

| Formato | Qualidades Disponíveis | Recomendado Para |
|---------|------------------------|------------------|
| **MP3** | 128k, 192k, 256k, 320k | Uso geral, compatibilidade |
| **M4A** | Best, Worst | Qualidade superior, dispositivos Apple |
| **OGG** | Best, Worst | Código aberto, menor tamanho |
| **WAV** | Best, Worst | Áudio sem perda, edição |

## 🔧 Recursos Avançados

### Sistema de Verificação
```bash
# Verificar se tudo está funcionando
yb-download-mp3 --check
```
- ✅ Valida instalação do FFmpeg
- ✅ Testa conectividade com YouTube
- ✅ Mostra latência dos servidores
- ✅ Verifica acesso a vídeos

### Auto-Atualizador
```bash
# Verificar e instalar atualizações
yb-download-mp3 --update
```
- 🔄 Conecta automaticamente com GitHub
- 📦 Baixa e instala versões mais recentes
- 📋 Mostra changelog das atualizações
- ⚡ Processo totalmente automatizado

### Downloads Paralelos
Para playlists grandes, ative downloads paralelos:
```bash
yb-download-mp3 --config
# Escolha "Sim" para downloads paralelos
# Configure máximo de downloads simultâneos (recomendado: 3)
```

### Tratamento de Duplicatas
Configurável via `--config`:
- **Skip**: Pula arquivos que já existem
- **Overwrite**: Sobrescreve arquivos existentes  
- **Rename**: Adiciona numeração (arquivo_1.mp3)

## 🐛 Solução de Problemas

### Diagnóstico Automático
```bash
# Primeira coisa a fazer em caso de problemas
yb-download-mp3 --check
```

### Problemas Comuns

**❌ FFmpeg não encontrado**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian  
sudo apt install ffmpeg

# Verificar instalação
yb-download-mp3 --check
```

**❌ YouTube offline/degradado**
- Problema temporário de conectividade
- Use VPN se estiver em região restrita
- Aguarde alguns minutos e tente novamente

**❌ Vídeo não disponível**
- Vídeo privado, removido ou com restrições
- Verifique se o link está correto
- Teste com outro vídeo público

**🐌 Downloads lentos**
- Use qualidades menores (128k, 192k)
- Desative downloads paralelos
- Verifique sua internet

### Logs para Debug
```bash
# Configurar logs detalhados
yb-download-mp3 --config
# Escolha log level: DEBUG

# Ver logs em tempo real
tail -f yt_download.log
```

## ⚡ Performance

### Benchmarks Típicos
- **Vídeo único (4min, 320kbps)**: ~30-60 segundos
- **Playlist (20 vídeos)**: ~8-15 minutos (sequencial)
- **Playlist (20 vídeos)**: ~3-6 minutos (paralelo)
- **Velocidade média**: 2-5 MB/s (depende da internet)

### Otimizações Implementadas
- ✅ **Downloads paralelos** para playlists
- ✅ **Retry automático** com backoff exponencial
- ✅ **Validação prévia** de URLs para evitar falhas
- ✅ **Cache de metadados** para evitar re-downloads
- ✅ **Compressão otimizada** por formato

### Dicas de Performance
```bash
# Para máxima velocidade em playlists
yb-download-mp3 --config
# Ative: parallel_downloads = true
# Configure: max_parallel_downloads = 3-5

# Para economizar banda/espaço
# Use qualidades menores: 128k ou 192k
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Minha nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Aviso Legal

Esta ferramenta é destinada apenas para uso pessoal e educacional. Respeite os direitos autorais e os termos de serviço do YouTube. O download de conteúdo protegido por direitos autorais pode violar os termos de uso das plataformas.

## 👨‍💻 Autor

**David Oliveira**
- LinkedIn: [seu-linkedin](https://linkedin.com/in/seu-perfil)
- GitHub: [@seu-usuario](https://github.com/seu-usuario)

---

⭐ Se este projeto te ajudou, considera dar uma estrela no GitHub!