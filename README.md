# Valorant Discord Rich Presence

```
 _   _____   __   ____  ___  ___   _  ________                
| | / / _ | / /  / __ \/ _ \/ _ | / |/ /_  __/__________  ____
| |/ / __ |/ /__/ /_/ / , _/ __ |/    / / / /___/ __/ _ \/ __/
|___/_/ |_/____/\____/_/|_/_/ |_/_/|_/ /_/     /_/ / .__/\__/ 
                                                   /_/         
```

[![Discord][discord-shield]][discord-url]
[![Stars][stars-shield]][stars-url]
[![License][license-shield]][license-url]

## About

**Valorant RPC** displays your real-time VALORANT game status directly in your Discord profile! Show your friends what you're up to without alt-tabbing.

### Features

- 🎮 **Real-time game status** - Shows current map, agent, and game mode
- 📊 **Live score tracking** - Displays match score during games
- ⏱️ **Queue timer** - Shows how long you've been waiting in matchmaking
- 🏆 **Rank display** - Option to show your competitive rank
- 👥 **Party status** - Shows if you're solo or in a group
- 🌍 **Multi-language support** - Available in multiple languages including Polish

### Screenshots

<img src="assets/Demo1.png" alt="Demo" width="205" height="112">
<img src="assets/Demo2.png" alt="Demo" width="205" height="112">

## Installation

1. Download the latest release or clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

- **If VALORANT is not running:** The program will launch it for you
- **If VALORANT is already running:** Just start the program and the Discord presence will activate

The program runs in the system tray and updates your Discord status automatically.

## Recent Fixes

This fork includes important fixes for the updated Valorant API structure:

- ✅ Fixed `sessionLoopState` detection (moved to `matchPresenceData`)
- ✅ Fixed `accountLevel` retrieval (moved to `playerPresenceData`)
- ✅ Fixed in-game status detection
- ✅ Added safe key access to prevent crashes from missing data
- ✅ Improved error handling throughout

## Credits

- Original project by [colinhartigan](https://github.com/colinhartigan/valorant-rpc)
- This fork is actively maintained with bug fixes and updates

## Disclaimer

This project is not affiliated with Riot Games or any of its employees and therefore does not reflect the views of said parties.

Riot Games does not endorse or sponsor this project. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

<!-- Links -->
[discord-shield]: https://img.shields.io/discord/860288779558715402?color=7289da&label=Support&logo=discord&logoColor=7289da&style=for-the-badge
[discord-url]: https://discord.gg/uGuswsZwAT
[stars-shield]: https://img.shields.io/github/stars/colinhartigan/valorant-rpc?logo=github&style=for-the-badge
[stars-url]: https://github.com/colinhartigan/valorant-rpc/stargazers
[license-shield]: https://img.shields.io/github/license/colinhartigan/valorant-rpc?style=for-the-badge
[license-url]: https://github.com/colinhartigan/valorant-rpc/blob/v3/LICENSE.txt
