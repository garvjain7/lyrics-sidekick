# 🎵 Lyrics SideKick

A real-time karaoke lyrics display application that syncs with your Spotify playback. Watch lyrics scroll in beautiful Hinglish (romanized Hindi) with word-by-word synchronization!

## Features

✨ **Real-time Sync** - Lyrics synchronize perfectly with your Spotify playback  
🎤 **Word-by-Word Display** - Each word appears in sync with the song  
🇮🇳 **Hinglish Support** - Automatically converts Hindi lyrics to Hinglish (Roman script) for easy reading  
🌈 **Attractive Terminal UI** - Colorful, styled output with ANSI colors and formatting  
📍 **Mid-Song Join** - Start the app anytime; it syncs from the current playback position  
🎨 **Line-by-Line Formatting** - Lyrics display beautifully with line breaks and visual separators  
🔍 **Multi-Source Lyrics** - Fetches enhanced/synced/plain lyrics from available sources  

## Prerequisites

- Python 3.11 or higher
- Spotify account (free or premium)
- Internet connection

## Installation

1. **Clone or download this repository:**
   ```bash
   cd lyricsSideKick
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Spotify API credentials:**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Get your `CLIENT_ID` and `CLIENT_SECRET`
   - Set the Redirect URI to `http://127.0.0.1:8888/callback`

4. **Create a `.env` file** in the project directory:
   ```
   CLIENT_ID=your_client_id_here
   CLIENT_SECRET=your_client_secret_here
   REDIRECT_URI=http://localhost:8888/callback
   ```

## Usage

1. **Start Spotify playback** on any device connected to your account

2. **Run the script:**
   ```bash
   python lyrics_sidekick.py
   ```

3. **Grant permissions** when prompted for Spotify authentication (first time only)

4. **Watch the lyrics sync** with your currently playing song!

The terminal will display:
- Currently playing song name and artist
- Real-time lyrics synchronized with playback
- Automatic Hinglish conversion for Hindi songs
- Beautiful colored output with visual separators

## Configuration

Edit `lyrics_sidekick.py` to customize:

- **`CHAR_DELAY`** - Typing animation speed (default: 0.01)
- **`POLL_INTERVAL`** - Polling frequency (default: 0.1 seconds)
- **Colors** - Modify the `Colors` class to change terminal colors

Example to increase speed:
```python
CHAR_DELAY = 0.005  # Faster typing
```

## How It Works

1. **Connects to Spotify API** via OAuth authentication
2. **Monitors current playback** and detects song changes
3. **Fetches synchronized lyrics** from `syncedlyrics` library (supports LRC format)
4. **Parses timestamps** to match words with playback position
5. **Converts Hindi to Hinglish** using custom transliteration
6. **Displays lyrics in real-time** with attractive terminal styling

## Supported Formats

- **Enhanced LRC** - Word-level timestamps for precise sync
- **Synced LRC** - Line-level timestamps with word interpolation
- **Plain Lyrics** - Fallback for songs without timestamps

## Language Support

- 🇬🇧 **English** - Displays as-is
- 🇮🇳 **Hindi** - Automatically converted to Hinglish
- 🔄 **Mixed** - Songs with both English and Hindi lyrics are handled seamlessly

## Troubleshooting

### No lyrics found for a song
- The song may not have synchronized lyrics available
- Try with a more popular song or different artist

### Spotify authentication fails
- Ensure your `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` are correct in `.env`
- Delete the Spotify cache and try again

### Lyrics don't sync properly
- This may happen for very new songs or obscure tracks
- The app will still display available lyrics without sync

### Terminal colors not showing
- Some terminals don't support ANSI colors
- Try running in a terminal that supports color codes (CMD, PowerShell, WSL, or Git Bash on Windows)

## Dependencies

- **spotipy** - Spotify API wrapper
- **python-dotenv** - Environment variable loader
- **syncedlyrics** - Synchronized lyrics fetcher
- **indic-transliteration** - Hindi/Devanagari transliteration

## License

This project is open source and available for personal use.

## Contributing

Feel free to fork, modify, and improve! Some ideas:
- Add support for more Indian languages
- Implement GUI instead of terminal
- Add lyrics recording/caching
- Support for multiple music services

## Notes

- This tool works best with songs that have synchronized lyrics available
- Lyrics are fetched in real-time, so internet connection is required
- Spotify account authentication is required for API access

---

**Enjoy your karaoke! 🎤🎵**
