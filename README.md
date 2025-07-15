# 🎵 YouTube Downloader

Uma ferramenta CLI **profissional** e **robusta** para baixar vídeos e playlists do YouTube em múltiplos formatos de áudio de alta qualidade (MP3, M4A, OGG, WAV), com recursos avançados de retry, downloads paralelos, auto-updater e muito mais.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 🏆 Diferenciais

**Por que escolher este downloader?**

| Recurso | Outros Tools | **yt-download** |
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

### Instalação do yt-download

```bash
# Método 1: Instalação direta do GitHub (Recomendado)
pip install git+https://github.com/0livrdavid/yt-download.git --user

# Método 2: Instalação local para desenvolvimento
git clone https://github.com/0livrdavid/yt-download.git
cd yt-download
pip install -e . --user
```

> 💡 **Dica**: Para desinstalar completamente, veja a seção [🗑️ Desinstalação](#️-desinstalação)

## 🚀 Como Usar

### ⚡ Início Rápido - Downloads Ultra-Rápidos

**Para playlists 3x mais rápidas, configure primeiro:**

```bash
# 1. Configure uma vez (recomendado)
yt-download --config
# Ative "Downloads Paralelos" = Sim

# 2. Use normalmente
yt-download
```

### Modo Interativo (Recomendado)

```bash
yt-download
```

O programa irá:
1. **Mostrar sua configuração atual** (formato, qualidade, download paralelo)
2. Solicitar o link do YouTube
3. Detectar automaticamente se é vídeo ou playlist
4. Perguntar o modo desejado (Automático ou Manual)
5. No modo manual, permitir escolher formato e qualidade
6. Realizar o download na pasta atual

### Linha de Comando Direta

```bash
# Download automático (MP3, melhor qualidade)
yt-download --url "https://youtube.com/watch?v=..." --auto

# Download com formato específico
yt-download --url "..." --format mp3 --quality 192

# Ver histórico com tamanhos reais
yt-download --history

# Ver estatísticas detalhadas
yt-download --stats

# Verificar se sistema está pronto (FFmpeg + YouTube)
yt-download --check

# Configurar aplicação interativamente
yt-download --config

# Verificar atualizações e instalar
yt-download --update

# Limpar histórico de downloads
yt-download --reset
```

## 📋 Exemplos de Uso

### Vídeo Único - Modo Automático
```bash
yt-download --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --auto
```

### Playlist Completa - Modo Manual
```bash
yt-download
# Cole: https://www.youtube.com/playlist?list=...
# Escolha: 2 (Manual)
# Formato: 1 (MP3)
# Qualidade: 1 (320 kbps)
```

### Verificar Histórico
```bash
yt-download --history
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
Use `yt-download --config` para configurar via interface gráfica interativa.

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
| **`parallel_downloads`** | **true/false** | **🚀 Downloads simultâneos em playlists** |
| `max_parallel_downloads` | 1-5 | Número máximo de downloads simultâneos |
| `max_retries` | 1-10 | Tentativas em caso de falha |
| `log_level` | DEBUG, INFO, WARNING, ERROR | Nível de logging |

### 🚀 Download Paralelo (Recomendado)

Para **acelerar significativamente** o download de playlists, ative o download paralelo:

```bash
# Edite o arquivo yt_download_config.json e altere:
"parallel_downloads": true,
"max_parallel_downloads": 3

# Ou use a interface interativa:
yt-download --config
```

**Performance com Download Paralelo:**
- ✅ **Playlist com 10 músicas**: ~2-3 minutos (vs 8-10 minutos sequencial)
- ✅ **Múltiplos downloads simultâneos**: Até 3x mais rápido
- ✅ **Uso otimizado da banda**: Aproveita melhor sua conexão

### 💡 Dicas de Performance

1. **Ative o Download Paralelo**: Para playlists, é a diferença entre 3 minutos e 10 minutos
2. **Use 3 downloads simultâneos**: Configuração ideal para a maioria das conexões
3. **Evite mais de 5 simultâneos**: Pode sobrecarregar o YouTube e sua conexão
4. **Monitore no modo verboso**: Use `--verbose` para ver o progresso detalhado

```bash
# Configuração otimizada recomendada:
{
  "parallel_downloads": true,
  "max_parallel_downloads": 3,
  "max_retries": 3
}
```

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
yt-download --history

# Ver estatísticas completas
yt-download --stats

# Limpar todo o histórico
yt-download --reset
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
yt-download --check
```
- ✅ Valida instalação do FFmpeg
- ✅ Testa conectividade com YouTube
- ✅ Mostra latência dos servidores
- ✅ Verifica acesso a vídeos

### Auto-Atualizador
```bash
# Verificar e instalar atualizações
yt-download --update
```
- 🔄 Conecta automaticamente com GitHub
- 📦 Baixa e instala versões mais recentes
- 📋 Mostra changelog das atualizações
- ⚡ Processo totalmente automatizado

### Downloads Paralelos
Para playlists grandes, ative downloads paralelos:
```bash
yt-download --config
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
yt-download --check
```

### Problemas Comuns

**❌ FFmpeg não encontrado**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian  
sudo apt install ffmpeg

# Verificar instalação
yt-download --check
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
yt-download --config
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
yt-download --config
# Ative: parallel_downloads = true
# Configure: max_parallel_downloads = 3-5

# Para economizar banda/espaço
# Use qualidades menores: 128k ou 192k
```

## 🗑️ Desinstalação

Para remover completamente o yt-download do seu sistema:

```bash
# Desinstalar o pacote
pip uninstall yt-download -y

# Verificar se foi removido
yt-download --version  # Deve retornar "command not found"
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
- LinkedIn: [olivr-davidg](https://www.linkedin.com/in/olivr-davidg)
- GitHub: [@0livrdavid](https://github.com/0livrdavid)

---

⭐ Se este projeto te ajudou, considera dar uma estrela no GitHub!
