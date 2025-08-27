<!-- Shields -->
[version-shield]: https://img.shields.io/github/v/release/NotAkitake/SIGMArec?color=f0c6c6
[version-url]: https://github.com/NotAkitake/SIGMArec/releases
[downloads-shield]: https://img.shields.io/github/downloads/NotAkitake/SIGMArec/total?color=c6a0f6
[downloads-url]: https://github.com/NotAkitake/SIGMArec/releases
[license-shield]: https://img.shields.io/github/license/NotAkitake/SIGMArec?color=f5bde6
[license-url]: https://github.com/NotAkitake/SIGMArec/blob/main/LICENSE
[ko-fi-shield]: https://img.shields.io/badge/Ko--fi-Donate-f2a3f7?style=flat&logo=kofi&logoColor=white
[ko-fi-url]: https://ko-fi.com/akitake
[stars-shield]: https://img.shields.io/github/stars/NotAkitake/SIGMArec
[stars-url]: http://github.com/NotAkitake/SIGMArec/stargazers
<div align="center">
  
[![Version][version-shield]][version-url]
[![Download Counter][downloads-shield]][downloads-url]
[![License][license-shield]][license-url]
[![Ko-fi][ko-fi-shield]][ko-fi-url]
[![Star Counter][stars-shield]][stars-url]
  
</div>

<!-- Header -->
<div align="center">
  <h2 align="center">SIGMArec</h3>
  <p align="center">
    <p>Automatically record and organize your rhythm game sessions.</p>
    <a href="https://github.com/NotAkitake/SIGMArec/releases">Download now</a>
    ·
    <a href="https://github.com/NotAkitake/SIGMArec/issues">Create an Issue</a>
    <br />
    <br />
  </p>
</div>

---

<!-- Security heads-up -->
> [!NOTE]
> Some antivirus software (like Windows Defender) may flag SIGMArec as malicious.
> **This is a false positive.**  
>
> Reasons:
> - Requires **administrator privileges** to detect key presses in elevated games.
> - Periodically **captures screenshots** for pixel detection.
>
> Why you can rest easy:
> - Official releases are automatically built from source via **GitHub Actions**.
> - You can review the code and compile it yourself if you prefer.

---

## :sparkles: Features

- **Game Detection**  
  Detects supported rhythm games and their states for seamless integration.

- **Recording Control**  
  Automatically starts recording when gameplay begins and stops when it ends.  
  *Save your last play with a hotkey, or let the next play overwrite the previous one to save space.*

- **Scene Switching**  
  Automatically switch OBS scenes per game and/or based on state *(Select, Playing, Result)*.

- **Video Settings**  
  Apply custom OBS video settings (resolution, FPS) per game as soon as you tab into it.

- **Organized Library**  
  Sort recordings into game-specific folders within your OBS recording directory.  
  *Optionally save a result screen screenshot alongside the video.*

- **Audio Feedback**  
  Provides sound cues to indicate key events, such as when a recording starts, stops, is ready to be saved, or has been saved.  
  *Since SIGMArec doesn’t hook into games or display overlays, audio cues keep you informed without interrupting gameplay.*  
  *Note: If your game uses exclusive audio control (e.g., WASAPI Exclusive), these sounds may not be audible.*

## :rocket: Quick Start

1. **Download** the latest release from [GitHub Releases](https://github.com/NotAkitake/SIGMArec/releases)
2. **Extract** the ZIP file to your desired folder
3. **Copy** `example.config.toml` to `config.toml`
4. **Edit** `config.toml` using commented text for guidance
5. **Start** OBS with WebSocket enabled (see Configuration section)
6. **Run** `SIGMArec.exe`

Then **play** any supported game. SIGMArec should now detect and record your gameplay!  
**Press** your defined `save_key` after hearing the "ready" sound on the result screen to **save your last play**.

## :gear: Configuration

### OBS Studio Setup
1. Open OBS Studio → Tools → WebSocket Server Settings
2. Enable **WebSocket server**
3. Set a **Server Password** and click Apply
4. Note the port number *(default: 4455)*

> *Without a manually set password, OBS generates a new one on each launch, so you’d need to update your config each time.*

### config.toml
The `example.config.toml` file should contain all you need to know for each option.  
If an option isn't present in your `config.toml` file, defaults will be used.  
Must be in the same directory as the executable.  

### games.json
Defines supported games and information required for their detection.  
Only modify only if you know what you're doing.  
Must be in the same directory as the executable.  

## :video_game: Supported Games

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

## :hammer: Run / Build from source

### Requirements

- Windows w/ PowerShell
- Latest python (and pip)

1. **Clone** the repository
2. **Navigate** to the project directory in your terminal of choice

### Running from Source
- Execute `run.ps1` to start SIGMArec from source

> *Run from an elevated terminal if you want your hotkeys to work in games running with administrator privileges.*

### Building the Application
- Execute `build.ps1` to create a standalone build
- Find the compiled application and all dependencies in the `release` folder
