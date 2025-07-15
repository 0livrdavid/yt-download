# 🎵 YouTube to MP3 Downloader

Uma ferramenta CLI simples e elegante para baixar vídeos e playlists do YouTube como arquivos MP3 de alta qualidade.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

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

# Ver histórico
yb-download-mp3 --history

# Ver estatísticas
yb-download-mp3 --stats
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

O arquivo `yt_download_config.json` é criado automaticamente com:

```json
{
  "audio_format": "mp3",
  "audio_quality": "320",
  "download_thumbnails": false,
  "create_playlist_folder": true,
  "auto_mode_quality": "best",
  "history_enabled": true,
  "max_retries": 3
}
```

## 📊 Recursos do Histórico

- **Data e hora** de cada download
- **Título** do vídeo/música
- **Duração** em minutos
- **Tamanho do arquivo** em MB
- **Formato e qualidade** utilizados
- **Estatísticas gerais** (total, tamanho médio, etc.)

## 🔧 Formatos Suportados

| Formato | Qualidades Disponíveis | Recomendado Para |
|---------|------------------------|------------------|
| **MP3** | 128k, 192k, 256k, 320k | Uso geral, compatibilidade |
| **M4A** | Best, Worst | Qualidade superior, dispositivos Apple |
| **OGG** | Best, Worst | Código aberto, menor tamanho |
| **WAV** | Best, Worst | Áudio sem perda, edição |

## 🐛 Solução de Problemas

### Erro: "FFmpeg não encontrado"
- Certifique-se que FFmpeg está instalado e no PATH
- No Windows, reinicie o terminal após adicionar ao PATH

### Erro: "Vídeo não disponível"
- O vídeo pode estar privado ou removido
- Verifique se o link está correto
- Alguns vídeos podem ter restrições geográficas

### Downloads lentos
- Use qualidades menores (128k, 192k)
- Verifique sua conexão com internet
- O servidor do YouTube pode estar limitando velocidade

## 📈 Roadmap

- [ ] Suporte a outros sites (SoundCloud, etc.)
- [ ] Interface gráfica (GUI)
- [ ] Download de legendas
- [ ] Integração com Spotify para buscar músicas
- [ ] Cache inteligente para evitar re-downloads

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