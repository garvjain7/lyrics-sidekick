import time
import re
import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from syncedlyrics import search
from dotenv import load_dotenv

load_dotenv()

# ===================== CONFIG =====================
CLIENT_ID = os.getenv("CLIENT_ID") 
CLIENT_SECRET = os.getenv("CLIENT_SECRET") 
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = "user-read-playback-state user-read-currently-playing"

# Typing speed per character
CHAR_DELAY = 0.01
# Polling interval to sync with Spotify
POLL_INTERVAL = 0.1

# ===================== TERMINAL STYLES =====================
# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

# ==================================================

# Hindi to Hinglish mapping dictionary
HINDI_TO_HINGLISH = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
    'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
    'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
    'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
    'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
    'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
    'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
    'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
    'श': 'sha', 'ष': 'sha', 'स': 'sa', 'ह': 'ha',
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
    'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ं': 'n', 'ः': 'h', 'ँ': 'n',
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    '।': '.', '॥': '..',
}


def convert_to_hinglish(text: str) -> str:
    """Convert Hindi script to Hinglish (Roman script)"""
    result = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Check if character is in mapping
        if char in HINDI_TO_HINGLISH:
            result.append(HINDI_TO_HINGLISH[char])
        else:
            # Keep non-Hindi characters as is (English, numbers, punctuation)
            result.append(char)
        
        i += 1
    
    hinglish_text = ''.join(result)
    
    # Clean up double vowels and common patterns
    hinglish_text = re.sub(r'aa(?!$)', 'a', hinglish_text)  # Remove extra 'a' after 'aa'
    
    return hinglish_text


def type_write(word: str, is_line_end: bool = False):
    """Print each character of the word with a small delay with attractive styling"""
    # Convert word to Hinglish if it contains Hindi
    hinglish_word = convert_to_hinglish(word)
    
    # Apply styling once to the entire word instead of per character
    if is_line_end:
        # Print styled word and end-of-line marker
        sys.stdout.write(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{hinglish_word}{Colors.RESET}{Colors.DIM}  ✧{Colors.RESET}\n")
        sys.stdout.flush()
    else:
        # Print styled word with space
        sys.stdout.write(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{hinglish_word}{Colors.RESET} ")
        sys.stdout.flush()
        time.sleep(CHAR_DELAY * len(hinglish_word))  # Sleep once for the word length


def parse_lrc(raw_lrc: str):
    """
    Parses raw LRC into list of (time_ms, word, line_id) for word-by-word karaoke.
    Returns: list of (word_time_ms, word, line_id) tuples
    Supports:
      - Word-level timestamps (Enhanced LRC)
      - Line-level timestamps (fallback)
    """
    lines = raw_lrc.splitlines()
    entries = []
    line_counter = 0

    line_ts_re = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")
    word_ts_re = re.compile(r"<(\d+):(\d+(?:\.\d+)?)>([^<>\n]+)")

    for ln in lines:
        m = line_ts_re.match(ln)
        if not m:
            continue
        mm, ss = m.groups()
        line_ms = int(mm) * 60_000 + int(float(ss) * 1000)

        word_matches = word_ts_re.findall(ln)
        if word_matches:
            # Word-level timestamps
            for w_mm, w_ss, w_text in word_matches:
                w_time = int(w_mm) * 60_000 + int(float(w_ss) * 1000)
                entries.append((w_time, w_text.strip(), line_counter))
        else:
            # Line-level fallback (split words evenly)
            text = re.sub(r"^\[\d+:\d+(?:\.\d+)?\]", "", ln).strip()
            words = text.split()
            interval = 200  # ms per word fallback
            for i, w in enumerate(words):
                entries.append((line_ms + i * interval, w, line_counter))
        
        line_counter += 1

    entries.sort(key=lambda x: x[0])
    return entries


def fetch_lyrics(song: str, artist: str):
    """
    Fetch lyrics using priority:
      1. Enhanced (word-level) -> auto fallback to synced
      2. Manual synced_only
      3. Plain as last resort
    """
    query = f"{song} {artist}"

    # Priority 1 → Enhanced (w/ auto fallback)
    raw = search(query, enhanced=True)
    if raw:
        print("Lyrics fetched: Enhanced/word-level (or auto fallback synced)")
        return raw

    # # Priority 2 → manual synced_only
    # raw = search(query, synced_only=True)
    # if raw:
    #     print("Lyrics fetched: Synced only (manual fallback)")
    #     return raw

    # # Priority 3 → plain
    # raw = search(query, plain=True)
    # if raw:
    #     print("Lyrics fetched: Plain (no timestamps)")
    #     return raw

    print("No lyrics found for this song.")
    return None


def get_current_spotify_progress(sp):
    """Returns current playback progress in ms"""
    data = sp.current_playback()
    if not data or not data.get("is_playing"):
        return None
    return data.get("progress_ms", 0)


def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))

    previous_track_id = None
    words = []
    printed = set()
    current_line = None

    while True:
        playback = sp.current_playback()

        if not playback or playback["item"] is None:
            os.system("cls" if os.name == "nt" else "clear")
            print("No song currently playing on Spotify...")
            time.sleep(1)
            continue

        track = playback["item"]
        current_track_id = track["id"]
        song = track["name"]
        artist = track["artists"][0]["name"]

        # GIVE REAL-TIME SYNCED WORDS
        prog = get_current_spotify_progress(sp)
        if prog is None:
            time.sleep(0.2)
            continue

        # ========= SONG CHANGE DETECTION ==========
        if current_track_id != previous_track_id:
            os.system("cls" if os.name == "nt" else "clear")
            # Styled header with colors
            print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}🎵 Now Playing: {song} — {artist}{Colors.RESET}\n")
            print(f"{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}\n")

            raw_lrc = fetch_lyrics(song, artist)
            if raw_lrc:
                words = parse_lrc(raw_lrc)
            else:
                words = []

            printed = set()  # Reset state
            # Pre-populate printed with all already-played lyrics
            for t_ms, w, line_id in words:
                if t_ms <= prog:
                    printed.add(t_ms)
            
            current_line = None
            previous_track_id = current_track_id
            print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}── Starting Karaoke ──{Colors.RESET}\n")
        # ==========================================

        # Print new words that haven't been printed yet
        for i, (t_ms, w, line_id) in enumerate(words):
            if t_ms <= prog and t_ms not in printed:
                # Check if this is the last word in the line
                is_last_in_line = (i + 1 >= len(words) or words[i + 1][2] != line_id)
                type_write(w, is_line_end=is_last_in_line)
                printed.add(t_ms)
                current_line = line_id

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    main()
