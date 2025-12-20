# Valorant Discord Rich Presence

```
 _   _____   __   ____  ___  ___   _  ________                
| | / / _ | / /  / __ \/ _ \/ _ | / |/ /_  __/__________  ____
| |/ / __ |/ /__/ /_/ / , _/ __ |/    / / / /___/ __/ _ \/ __/
|___/_/ |_/____/\____/_/|_/_/ |_/_/|_/ /_/     /_/ / .__/\__/ 
                                                   /_/         
```
> **🔧 This is an actively maintained fork of the original [valorant-rpc](https://github.com/colinhartigan/valorant-rpc) project.**  
> The original repository has been archived. This fork includes bug fixes and updates to keep the project working with the latest Valorant API changes.

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

## Changelog

### v3.2.5 - 2025-12-20

#### Fixed
- Fixed crash when entering the Shooting Range (`sessionLoopState` KeyError)
- Implemented safe data access in `range.py` consistent with other game modes

### v3.2.4 - 2025-12-19

#### Fixed
- Fixed `sessionLoopState` detection (moved to `matchPresenceData`)
- Fixed `accountLevel` retrieval (moved to `playerPresenceData`)
- Fixed in-game status detection - now properly shows game mode and score
- Fixed `provisioningFlow` detection for shooting range vs regular games
- Added safe `.get()` key access to prevent crashes from missing data

#### Added
- Improved matchmaking queue status detection
- Added `partyState` detection from `partyPresenceData` and `matchPresenceData`
- Queue status now properly displays when searching for a match

#### Changed
- Updated all presence files to use safe key access patterns
- Improved error handling throughout the codebase

## Credits

- Original project by [colinhartigan](https://github.com/colinhartigan/valorant-rpc)
- This fork is actively maintained with bug fixes and updates

## Disclaimer

This project is not affiliated with Riot Games or any of its employees and therefore does not reflect the views of said parties.

Riot Games does not endorse or sponsor this project. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.


