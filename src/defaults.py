"""
Default config.toml and games.json
"""

DEFAULT_GAMES = """{
  "beatmania IIDX INFINITAS": {
    "type": "pixel",
    "processes": [
      {
        "exe": "*bm2dx.exe",
        "title": "beatmania IIDX INFINITAS"
      }
    ],
    "shortname": "IIDXINF",
    "states": {
      "Select": {
        "patterns": [
          {
            "description": "Blue line on the left",
            "resolution": [1920, 1080],
            "pixels": [
              [310, 125, 1, 213, 255, 0]
            ]
          }
        ]
      },
      "Playing": {
        "patterns": [
          {
            "description": "1P",
            "resolution": [1920, 1080],
            "pixels": [
              [339, 840, 17, 17, 18, 0],
              [53, 20, 155, 155, 155, 0]
            ]
          },
          {
            "description": "2P",
            "resolution": [1920, 1080],
            "pixels": [
              [1580, 840, 17, 17, 18, 0],
              [1867, 20, 155, 155, 155, 0]
            ]
          },
          {
            "description": "DP",
            "resolution": [1920, 1080],
            "pixels": [
              [724, 840, 20, 20, 20, 0],
              [438, 20, 155, 155, 155, 0],
              [1196, 840, 20, 20, 20, 0],
              [1482, 20, 155, 155, 155, 0]
            ]
          }
        ]
      },
      "Result": {
        "patterns": [
          {
            "description": "SP",
            "resolution": [1920, 1080],
            "pixels": [
              [931, 1037, 204, 204, 204, 0]
            ]
          },
          {
            "description": "DP",
            "resolution": [1920, 1080],
            "pixels": [
              [931, 1037, 0, 0, 0, 0],
              [942, 1060, 255, 254, 254, 0]
            ]
          }
        ]
      }
    }
  },
  "Sound Voltex: Exceed Gear (Konasute)": {
    "type": "pixel",
    "processes": [
      {
        "exe": "*sv6c.exe",
        "title": "SOUND VOLTEX EXCEED GEAR"
      }
    ],
    "shortname": "SDVXEAC",
    "states": {
      "Select": {
        "patterns": [
          {
            "description": "Landscape Monitor: Colored text around radar",
            "resolution": [1920, 1080],
            "pixels": [
              [897, 350, 0, 255, 242, 0],
              [922, 432, 255, 0, 202, 0]
            ]
          },
          {
            "description": "Portrait Monitor: Colored text around radar",
            "resolution": [1080, 1920],
            "pixels": [
              [423, 620, 0, 255, 242, 0],
              [466, 765, 255, 0, 202, 0]
            ]
          },
          {
            "description": "Landscape Monitor + Flipped Portrait Game: Colored text around radar",
            "resolution": [1920, 1080],
            "pixels": [
              [1299, 423, 0, 255, 242, 0],
              [1154, 466, 255, 0, 202, 0]
            ]
          },
          {
            "description": "Landscape Monitor + Portrait Game: Colored text around radar",
            "resolution": [1920, 1080],
            "pixels": [
              [620, 656, 0, 255, 242, 0],
              [765, 613, 255, 0, 202, 0]
            ]
          }
        ]
      },
      "Playing": {
        "patterns": [
          {
            "description": "Landscape Monitor: Frame to the left of song jacket, orange hyphen to the left of song title",
            "resolution": [1920, 1080],
            "pixels": [
              [670, 150, 225, 230, 236, 0],
              [860, 152, 0, 0, 0, 0]
            ]
          },
          {
            "description": "Portrait Monitor: Frame to the left of song jacket, orange hyphen to the left of song title",
            "resolution": [1080, 1920],
            "pixels": [
              [23, 254, 225, 230, 236, 0],
              [360, 270, 0, 0, 0, 0]
            ]
          },
          {
            "description": "Landscape Monitor + Flipped Portrait Game: Frame to the left of song jacket, orange hyphen to the left of song title",
            "resolution": [1920, 1080],
            "pixels": [
              [1665, 23, 225, 230, 236, 0],
              [1649, 360, 0, 0, 0, 0]
            ]
          },
          {
            "description": "Landscape Monitor + Portrait Game: Frame to the left of song jacket, orange hyphen to the left of song title",
            "resolution": [1920, 1080],
            "pixels": [
              [255, 1057, 225, 230, 236, 0],
              [271, 720, 0, 0, 0, 0]
            ]
          }
        ]
      },
      "Result": {
        "patterns": [
          {
            "description": "Landscape Monitor: Result screen chip/long/tsunami colored text",
            "resolution": [1920, 1080],
            "pixels": [
              [787, 687, 3, 234, 255, 0],
              [848, 687, 156, 255, 0, 0],
              [916, 687, 255, 0, 231, 0]
            ]
          },
          {
            "description": "Portrait Monitor: Result screen chip/long/tsunami colored text",
            "resolution": [1080, 1920],
            "pixels": [
              [232, 1220, 3, 234, 255, 0],
              [342, 1220, 156, 255, 0, 0],
              [463, 1220, 255, 0, 231, 0]
            ]
          },
          {
            "description": "Landscape Monitor + Flipped Portrait Game: Result screen chip/long/tsunami colored text",
            "resolution": [1920, 1080],
            "pixels": [
              [699, 232, 3, 234, 255, 0],
              [699, 342, 156, 255, 0, 0],
              [699, 463, 255, 0, 231, 0]
            ]
          },
          {
            "description": "Landscape Monitor + Portrait Game: Result screen chip/long/tsunami colored text",
            "resolution": [1920, 1080],
            "pixels": [
              [1220, 846, 3, 234, 255, 0],
              [1220, 736, 156, 255, 0, 0],
              [1220, 616, 255, 0, 231, 0]
            ]
          }
        ]
      }
    }
  },
  "beatmania IIDX 31 EPOLIS": {
    "type": "pixel",
    "shortname": "IIDX31",
    "processes": [
      {
        "exe": "spice64.exe",
        "title": "beatmania IIDX 31 EPOLIS main"
      }
    ],
    "states": {
      "Select": {
        "patterns": [
          {
            "description": "Top left T, bottom of yellow bar on the right",
            "resolution": [1920, 1080],
            "pixels": [
              [473, 39, 0, 0, 0, 0],
              [1903, 850, 225, 239, 0, 0]
            ]
          }
        ]
      },
      "Playing": {
        "patterns": [
          {
            "description": "1P",
            "resolution": [1920, 1080],
            "pixels": [
              [247, 982, 141, 137, 131, 0],
              [257, 972, 7, 6, 6, 0],
              [159, 1020, 225, 239, 0, 0]
            ]
          },
          {
            "description": "2P",
            "resolution": [1920, 1080],
            "pixels": [
              [1673, 982, 141, 137, 131, 0],
              [1662, 972, 7, 6, 6, 0],
              [1793, 1020, 225, 239, 0, 0]
            ]
          },
          {
            "description": "DP",
            "resolution": [1920, 1080],
            "pixels": [
              [606, 990, 219, 239, 0, 0],
              [783, 974, 219, 239, 0, 0],
              [787, 967, 142, 138, 132, 0],
              [1313, 990, 219, 239, 0, 0],
              [1136, 974, 219, 239, 0, 0],
              [1132, 967, 142, 138, 132, 0]
            ]
          }
        ]
      },
      "Result": {
        "patterns": [
          {
            "description": "SP",
            "resolution": [1920, 1080],
            "pixels": [
              [931, 1037, 191, 191, 191, 0]
            ]
          },
          {
            "description": "DP",
            "resolution": [1920, 1080],
            "pixels": [
              [931, 1037, 0, 0, 0, 0],
              [942, 1060, 239, 238, 238, 0]
            ]
          }
        ]
      }
    }
  },
  "beatmania IIDX 32 Pinky Crush": {
    "type": "pixel",
    "shortname": "IIDX32",
    "processes": [
      {
        "exe": "spice64.exe",
        "title": "beatmania IIDX 32 Pinky Crush main"
      }
    ],
    "states": {
      "Select": {
        "patterns": [
          {
            "description": "Top left pink M, bottom of pink bar on the right",
            "resolution": [1920, 1080],
            "pixels": [
              [107, 47, 239, 0, 186, 0],
              [1912, 862, 239, 0, 186, 0]
            ]
          }
        ]
      },
      "Playing": {
        "patterns": [
          {
            "description": "1P",
            "resolution": [1920, 1080],
            "pixels": [
              [9, 948, 239, 190, 229, 0],
              [531, 948, 239, 190, 229, 0],
              [271, 880, 193, 192, 192, 0]
            ]
          },
          {
            "description": "2P",
            "resolution": [1920, 1080],
            "pixels": [
              [1388, 948, 239, 190, 229, 0],
              [1910, 948, 239, 190, 229, 0],
              [1648, 880, 193, 192, 192, 0]
            ]
          },
          {
            "description": "DP",
            "resolution": [1920, 1080],
            "pixels": [
              [378, 908, 239, 52, 231, 0],
              [690, 980, 239, 52, 239, 0],
              [1541, 908, 239, 52, 231, 0],
              [1227, 980, 239, 52, 239, 0]
            ]
          }
        ]
      },
      "Result": {
        "patterns": [
          {
            "description": "SP",
            "resolution": [1920, 1080],
            "pixels": [
              [931, 1037, 191, 191, 191, 0]
            ]
          },
          {
            "description": "DP",
            "resolution": [1920, 1080],
            "pixels": [
              [931, 1037, 0, 0, 0, 0],
              [942, 1060, 239, 238, 238, 0]
            ]
          }
        ]
      }
    }
  },
  "Sound Voltex: Exceed Gear": {
    "type": "pixel",
    "processes": [
      {
        "exe": "spice64.exe",
        "title": "SOUND VOLTEX EXCEED GEAR - Main Screen"
      }
    ],
    "shortname": "SDVXEG",
    "states": {
      "Select": {
        "patterns": [
          {
            "description": "Portrait Monitor:Colored text around radar",
            "resolution": [1080, 1920],
            "pixels": [
              [423, 620, 0, 255, 242, 0],
              [466, 765, 255, 0, 202, 0]
            ]
          }
        ]
      },
      "Playing": {
        "patterns": [
          {
            "description": "Portrait Monitor: Frame to the left of song jacket, orange hyphen to the left of song title",
            "resolution": [1080, 1920],
            "pixels": [
              [23, 254, 225, 230, 236, 0],
              [360, 270, 0, 0, 0, 0]
            ]
          }
        ]
      },
      "Result": {
        "patterns": [
          {
            "description": "Portrait Monitor: Result screen chip/long/tsunami colored text",
            "resolution": [1080, 1920],
            "pixels": [
              [232, 1220, 0, 231, 247, 0],
              [342, 1220, 156, 251, 0, 0],
              [463, 1220, 247, 0, 222, 0]
            ]
          }
        ]
      }
    }
  },
  "beatoraja / lr2oraja": {
    "type": "log",
    "processes": [
      {
        "exe": "java.exe"
      }
    ],
    "shortname": "BMS",
    "logs": "beatoraja_log.xml",
    "states": {
      "Select": {
        "patterns": [
          {
            "class": "bms.player.beatoraja.SystemSoundManager",
            "method": "shuffle"
          },
          {
            "class": "bms.player.beatoraja.MainController$SystemSoundManager",
            "method": "shuffle"
          }
        ]
      },
      "Playing": {
        "patterns": [
          {
            "class": "bms.player.beatoraja.play.BMSPlayer",
            "method": "create"
          }
        ]
      },
      "Result": {
        "patterns": [
          {
            "class": "bms.player.beatoraja.result.MusicResult",
            "method": "lambda$prepare$0"
          }
        ]
      },
      "Unknown": {
        "patterns": [
          {
            "class": "bms.player.beatoraja.PlayDataAccessor",
            "method": "writeScoreData"
          }
        ]
      }
    }
  }
}

"""

DEFAULT_CONFIG = """[input]
save_key = "ctrl+space" # Keyboard key(s) to trigger recording save (allows for multiple keys like 'ctrl+shift+s')
debug = false # Enable detailed logging and debug output

[obs]   
host = "localhost" # OBS WebSocket server address
port = 4455 # OBS WebSocket server port
password = "YOUR_PASSWORD" # OBS WebSocket authentication password
timeout = 3 # Connection timeout in seconds

[audio]
start = "./sounds/start.wav" # Sound file played when recording begins
ready = "./sounds/ready.wav" # Sound file played when ready to save
saved = "./sounds/saved.wav" # Sound file played after successful save
failed = "./sounds/failed.wav" # Sound file played when save operation fails or is aborted

[detection] 
interval = 0.25 # Seconds between game state detection checks
detections_required = 2 # Consecutive matching detections needed to confirm state change

[recording]
result_wait = 1.5 # Seconds to display result screen before stopping
organize_by_game = true # Create separate folders for each detected game
save_thumbnails = true # Generate thumbnail images when recordings end
scene_change_delay = 0.3 # Delay in seconds before recording can start after scene change (should match your OBS scene transition duration)

[scenes] 
# Optional: Automatically switch OBS scenes based on detected game state
# 
# Switch scenes when SIGMArec detects game state changes (playing, results, menus).
#
# Configuration format:
#   [scenes]                    # Default fallbacks
#   Default = "Scene Name"      # Used when no game-specific scene is defined
#
#   [scenes.GAME_SHORTNAME]     # Game-specific settings
#   GameState = "Scene Name"
#
# Available games: BMS, IIDX31, IIDX32, IIDXINF, SDVXEAC, SDVXEG
# Available states: Default, Playing, Result, Select
#
# Examples:
#   [scenes]
#   Default = "Fullscreen"      # Fallback for all undefined scenes
#   
#   [scenes.BMS]
#   Playing = "BMS Handcam"     # BMS uses this while playing, "Fullscreen" for other states
#
#   [scenes.IIDX31]
#   Playing = "IIDX Handcam"
#   Result = "Results View"
#   Select = "Song Select"      # Complete configuration, no fallbacks needed

[video]
# Optional: Automatically adjust OBS video settings based on detected game
# 
# Change canvas resolution, output resolution, and frame rate when specific games are detected.
#
# Configuration format:
#   [video]                     # Default fallbacks
#   Base = "1920x1080"          # Default canvas for all games
#   Output = "1280x720"         # Default output for all games
#   FPS = 60                    # Default FPS for all games
#
#   [video.GAME_SHORTNAME]      # Game-specific settings
#   Base = "widthxheight"       # Canvas resolution
#   Output = "widthxheight"     # Output resolution  
#   FPS = number                # Frame rate
#
# Available games: BMS, IIDX31, IIDX32, IIDXINF, SDVXEAC, SDVXEG
#
# Examples:
#   [video]
#   Base = "1920x1080"          # Defaults for all games
#   Output = "1280x720"
#   FPS = 60
#   
#   [video.BMS]
#   FPS = 120                   # Higher FPS for BMS, inherits default resolutions
#
#   [video.IIDX31]
#   Base = "2560x1440"          # Full configuration for IIDX
#   Output = "1280x720"
#   FPS = 120
#
# Note: Game-specific settings override defaults. Unspecified settings preserve existing OBS values.

"""
