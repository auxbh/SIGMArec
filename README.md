# SIGMArec

**Automated rhythm game recording with intelligent state detection**

SIGMArec is an automated recording tool for rhythm games that intelligently detects gameplay states and manages OBS Studio recordings. It captures your sessions automatically and provides a convenient save system for preserving your desired plays.

## ✨ Features

- **Smart State Detection**: Automatically detects game states (Select, Playing, Result) using pixel analysis or log monitoring
- **OBS Recording**: Seamless control of OBS Studio video settings and recording via WebSocket
- **OBS Scene Switching**: Configurable auto-switching of scenes based on game states
- **Lastplay System**: Save your best recordings with a hotkey during result screens
- **Audio Feedback**: Sound notifications for recording events - **won't work with WASAPI exclusive**
- **Organized Storage**: Automatically organizes recordings by game with optional thumbnails
- **Multi-Game Support**: Supports multiple rhythm games out of the box

## 🚀 Quick Start

1. **Download** the latest release from [GitHub Releases](https://github.com/NotAkitake/SIGMArec/releases)
2. **Extract** the ZIP file to your desired folder
3. **Copy** `example.config.toml` to `config.toml`
4. **Edit** `config.toml` with your OBS settings (see Configuration section)
5. **Start** OBS with WebSocket enabled
6. **Run** `SIGMArec.exe`

Then **play** any supported game. SIGMArec should now record your gameplay.  
**Press** your defined `save_key` after hearing the `ready` sound on result screen to save your last play.

## ⚙️ Configuration

### OBS Studio Setup
1. Open OBS Studio
2. Go to `Tools > WebSocket Server Settings`
3. Enable `Enable WebSocket server`
4. Set a secure `Server Password` and click Apply
5. Note the port number (default: 4455)

### Config file
The `example.config.toml` file should contain all you need to know for each option.  
If an option isn't present in your `config.toml` file, defaults will be used.

## 🎮 Supported Games

### Pixel-based Detection
At 1080p, not upscaled, windowed is ok.  
For IIDX, default frame skin must be used.
- **Sound Voltex: Exceed Gear** (including Konasute)
- **beatmania IIDX INFINITAS**
- **beatmania IIDX 31 EPOLIS**
- **beatmania IIDX 32 Pinky Crush**

### Log-based Detection
- **beatoraja**
- **LR2oraja**

## 🔨 Build from source

### Requirements

- Windows w/ PowerShell
- Latest python (and pip)

### Process

- Clone the project
- Open a terminal in the project directory
- Run `build.ps1`