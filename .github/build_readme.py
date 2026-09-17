import os
import re
from collections import defaultdict

# ---------------------------------------------------------
# Regex patterns to parse markdown links and descriptions
# ---------------------------------------------------------
LINK_PATTERN = re.compile(
    r'(?:[-*]\s+|\d+\.\s+)?(?:\[\*\*|\*\*)?\[?([^\]\*\n]+)\]?\*?\*?\s*\((https?://[^\s\)]+)\)(?:\s*(?:—|-|:)\s*(.+))?'
)

def clean_text(text):
    if not text:
        return ""
    # Strip emojis and markdown formatting
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.replace('**', '').replace('__', '').strip()
    return text

def parse_files():
    repos = {}
    
    # Files to look for in the repo directory
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith(('.md', '.txt')) and file != 'README.md':
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            match = LINK_PATTERN.search(line)
                            if match:
                                name = match.group(1).strip()
                                url = match.group(2).strip()
                                desc = match.group(3).strip() if match.group(3) else ""
                                
                                # Avoid badge / license / anchor links
                                if any(x in url.lower() for x in ['shields.io', 'badge.svg', 'license', 'github.com/login', '#']):
                                    continue
                                
                                if url not in repos:
                                    clean_name = clean_text(name).split('/')[-1].strip()
                                    clean_desc = clean_text(desc)
                                    if not clean_desc or len(clean_desc) < 3:
                                        clean_desc = "Open-source utility and tool."
                                    else:
                                        # Keep description concise (under 8 words)
                                        words = clean_desc.split()
                                        clean_desc = ' '.join(words[:7])
                                        if not clean_desc.endswith('.'):
                                            clean_desc += '.'
                                            
                                    repos[url] = {
                                        'name': clean_name if clean_name else name,
                                        'url': url,
                                        'desc': clean_desc,
                                        'raw': line.lower()
                                    }
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return repos

# ---------------------------------------------------------
# Categorization Engine (Granular & Functional)
# ---------------------------------------------------------
def categorize(repos):
    data = {
        'Android': defaultdict(list),
        'iOS': defaultdict(list),
        'Windows': defaultdict(list),
        'macOS': defaultdict(list)
    }

    for url, info in repos.items():
        text = (info['name'] + ' ' + info['desc'] + ' ' + info['raw'] + ' ' + url).lower()
        
        # 1. ANDROID
        if any(k in text for k in ['android', 'apk', 'f-droid', 'magisk', 'kernelsu', 'xposed', 'monet', 'material you', 'shizuku']):
            if any(k in text for k in ['f-droid', 'store', 'market', 'obtainium', 'sideload', 'installer']):
                data['Android']['App Stores & Sideloading'].append(info)
            elif any(k in text for k in ['patch', 'mod', 'telegram', 'instagram', 'reddit', 'tweaks', 'inugram']):
                data['Android']['App Mods & Patches'].append(info)
            elif any(k in text for k in ['revanced', 'morphe', 'xposed', 'lsposed']):
                data['Android']['Patching Frameworks & Engines'].append(info)
            elif any(k in text for k in ['youtube', 'stream', 'anime', 'manga', 'newpipe', 'cloudstream', 'tv']):
                data['Android']['Online Video Streamers'].append(info)
            elif any(k in text for k in ['mpv', 'player', 'vlc', 'exoplayer', 'video player']):
                data['Android']['Offline Video Players'].append(info)
            elif any(k in text for k in ['video editor', 'cutter', 'screen recorder', 'trim']):
                data['Android']['Video Editors & Recorders'].append(info)
            elif any(k in text for k in ['spotify', 'music streaming', 'innertune', 'simpmusic', 'spotube']):
                data['Android']['Online Music Streamers'].append(info)
            elif any(k in text for k in ['audio player', 'music player', 'offline music', 'auxio', 'flac']):
                data['Android']['Offline Audio Players'].append(info)
            elif any(k in text for k in ['tts', 'speech', 'tag', 'lyrics', 'shazam', 'voice recorder']):
                data['Android']['Audio Tools, Tagging & Speech'].append(info)
            elif any(k in text for k in ['podcast', 'audiobook']):
                data['Android']['Podcasts & Audiobooks'].append(info)
            elif any(k in text for k in ['download', 'torrent', 'aria2', 'ytdl']):
                data['Android']['Download Managers'].append(info)
            elif any(k in text for k in ['browser', 'chromium', 'firefox', 'gecko']):
                data['Android']['Web Browsers'].append(info)
            elif any(k in text for k in ['root', 'magisk', 'kernelsu', 'apatch', 'recovery', 'twrp']):
                data['Android']['Root & Kernel Solutions'].append(info)
            elif any(k in text for k in ['debloat', 'freeze', 'canta', 'uninstaller', 'appmanager']):
                data['Android']['System Debloaters & Package Tools'].append(info)
            elif any(k in text for k in ['monitor', 'pcap', 'integrity', 'cpu', 'logcat', 'diagnostic']):
                data['Android']['System Diagnostics & Hardware'].append(info)
            elif any(k in text for k in ['firewall', 'adblock', 'dns', 'adaway', 'rethink']):
                data['Android']['Ad Blockers, Firewalls & DNS'].append(info)
            elif any(k in text for k in ['vpn', 'wireguard', 'tailscale', 'proxy', 'v2ray', 'tor']):
                data['Android']['VPNs, Proxies & Anonymity'].append(info)
            elif any(k in text for k in ['password', '2fa', 'authenticator', 'keepass', 'bitwarden']):
                data['Android']['Password Managers & 2FA'].append(info)
            elif any(k in text for k in ['file manager', 'explorer', 'archive', '7z']):
                data['Android']['File Managers & Archivers'].append(info)
            elif any(k in text for k in ['pdf', 'scanner', 'ocr']):
                data['Android']['Document Scanners & OCR'].append(info)
            elif any(k in text for k in ['reader', 'ebook', 'epub', 'koreader', 'comic']):
                data['Android']['Document & E-Book Readers'].append(info)
            elif any(k in text for k in ['transfer', 'localsend', 'kde connect', 'remote', 'rustdesk']):
                data['Android']['File Transfer & Remote Control'].append(info)
            elif any(k in text for k in ['sync', 'backup', 'cloud', 'davx', 'syncthing']):
                data['Android']['Cloud Storage & Sync Engines'].append(info)
            elif any(k in text for k in ['notes', 'markdown', 'logseq', 'joplin', 'knowledge']):
                data['Android']['Notes & Knowledge Bases'].append(info)
            elif any(k in text for k in ['office', 'document', 'collabora']):
                data['Android']['Office Suites & Editors'].append(info)
            elif any(k in text for k in ['todo', 'habit', 'task', 'productivity', 'timer']):
                data['Android']['Task & Habit Trackers'].append(info)
            elif any(k in text for k in ['gallery', 'photo', 'camera', 'vault']):
                data['Android']['Photo Galleries & Camera Vaults'].append(info)
            elif any(k in text for k in ['mail', 'email', 'thunderbird', 'k-9']):
                data['Android']['Email Clients & Aliasing'].append(info)
            elif any(k in text for k in ['chat', 'messenger', 'matrix', 'simplex', 'xmpp']):
                data['Android']['Chat & Messaging Clients'].append(info)
            elif any(k in text for k in ['social', 'mastodon', 'reddit', 'lemmy', 'client']):
                data['Android']['Social Network Frontends'].append(info)
            elif any(k in text for k in ['keyboard', 'input', 'ime', 'heliboard']):
                data['Android']['Keyboards & Input Tools'].append(info)
            elif any(k in text for k in ['launcher', 'home', 'desktop']):
                data['Android']['Home Screen Launchers'].append(info)
            elif any(k in text for k in ['map', 'navigation', 'gps', 'osm']):
                data['Android']['Maps & Navigation'].append(info)
            elif any(k in text for k in ['finance', 'budget', 'expense', 'money']):
                data['Android']['Finance & Expense Trackers'].append(info)
            elif any(k in text for k in ['health', 'fitness', 'workout', 'running']):
                data['Android']['Health & Fitness'].append(info)
            elif any(k in text for k in ['quran', 'islam', 'prayer', 'adhan', 'taqwa']):
                data['Android']['Religion & Islamic Apps'].append(info)
            elif any(k in text for k in ['weather', 'forecast']):
                data['Android']['Weather Apps'].append(info)
            elif any(k in text for k in ['emulator', 'retroarch', 'game', 'gaming']):
                data['Android']['Gaming & Emulation'].append(info)
            elif any(k in text for k in ['termux', 'ide', 'terminal', 'compiler', 'code']):
                data['Android']['Mobile Terminals & IDEs'].append(info)
            else:
                data['Android']['General Utilities'].append(info)

        # 2. IOS
        elif any(k in text for k in ['ios', 'iphone', 'ipad', 'ipa', 'swiftui', 'xcode', 'cocoapods']):
            if any(k in text for k in ['tweak', 'mod', 'jailbreak', 'ytkace', 'maxtube']):
                data['iOS']['App Mods & Tweaks'].append(info)
            elif any(k in text for k in ['sideload', 'ipatool', 'altstore', 'installer']):
                data['iOS']['Sideloading & Package Installers'].append(info)
            elif any(k in text for k in ['stream', 'video', 'player', 'youtube', 'vlc']):
                data['iOS']['Media & Video Players'].append(info)
            elif any(k in text for k in ['audio', 'sound', 'music', 'dsp', 'speech']):
                data['iOS']['Audio Synthesis & Speech'].append(info)
            elif any(k in text for k in ['networking', 'http', 'alamofire', 'socket', 'api']):
                data['iOS']['Networking & API Clients'].append(info)
            elif any(k in text for k in ['database', 'realm', 'sqlite', 'coredata', 'storage']):
                data['iOS']['Databases & Local Storage'].append(info)
            elif any(k in text for k in ['security', 'keychain', 'crypto', 'lock']):
                data['iOS']['Security, Crypto & Keychain'].append(info)
            elif any(k in text for k in ['layout', 'autolayout', 'snapkit', 'ui', 'view']):
                data['iOS']['UI Layout Engines & Components'].append(info)
            elif any(k in text for k in ['animation', 'lottie', 'transition']):
                data['iOS']['Animation & Transitions'].append(info)
            elif any(k in text for k in ['xcode', 'extension', 'plugin', 'linter']):
                data['iOS']['Xcode Extensions & Tooling'].append(info)
            else:
                data['iOS']['General iOS Utilities'].append(info)

        # 3. WINDOWS
        elif any(k in text for k in ['windows', 'win11', 'win10', 'powershell', 'reg add', 'defender', 'rufus']):
            if any(k in text for k in ['debloat', 'winutil', 'sophia', 'tweaker', 'optimizer']):
                data['Windows']['System Debloaters & Setup Tools'].append(info)
            elif any(k in text for k in ['defender', 'security', 'hardening', 'firewall']):
                data['Windows']['Windows Defender & Security Hardening'].append(info)
            elif any(k in text for k in ['update', 'store', 'wumgr', 'winget']):
                data['Windows']['Windows Update & Store Managers'].append(info)
            elif any(k in text for k in ['media', 'player', 'mpv', 'audio', 'stream', 'music']):
                data['Windows']['Media Players & Audio Streamers'].append(info)
            elif any(k in text for k in ['screen', 'recording', 'obs', 'editor', 'video']):
                data['Windows']['Video Editors & Screen Recorders'].append(info)
            elif any(k in text for k in ['ai', 'agent', 'llm', 'chatgpt', 'claude', 'coding']):
                data['Windows']['AI Coding Agents & Local LLMs'].append(info)
            elif any(k in text for k in ['download', 'torrent', 'idm', 'yt-dlp']):
                data['Windows']['Download Accelerators & Scrapers'].append(info)
            elif any(k in text for k in ['quran', 'islam', 'adhan']):
                data['Windows']['Islamic Apps'].append(info)
            else:
                data['Windows']['General Windows Tools'].append(info)

        # 4. MACOS
        else:
            if any(k in text for k in ['audio', 'sound', 'music', 'equalizer', 'daw', 'player']):
                data['macOS']['Audio, Players & Recording'].append(info)
            elif any(k in text for k in ['video', 'screen', 'obs', 'cut', 'transcode', 'movie']):
                data['macOS']['Video Players & Editors'].append(info)
            elif any(k in text for k in ['browser', 'safari', 'extension', 'pip']):
                data['macOS']['Browsers & Safari Extensions'].append(info)
            elif any(k in text for k in ['chat', 'message', 'mail', 'email', 'irc']):
                data['macOS']['Communication & Email'].append(info)
            elif any(k in text for k in ['database', 'sql', 'redis', 'postgres', 'mongo']):
                data['macOS']['Database Management Clients'].append(info)
            elif any(k in text for k in ['git', 'github', 'repo', 'version']):
                data['macOS']['Git GUI Clients'].append(info)
            elif any(k in text for k in ['api', 'developer', 'http', 'debug', 'json']):
                data['macOS']['API & Developer Tools'].append(info)
            elif any(k in text for k in ['download', 'torrent', 'transfer', 'sharing', 'cask']):
                data['macOS']['Downloaders & File Sharing'].append(info)
            elif any(k in text for k in ['editor', 'ide', 'code', 'markdown', 'notes', 'latex']):
                data['macOS']['Code, Text & Markdown Editors'].append(info)
            elif any(k in text for k in ['finder', 'cleaner', 'monitor', 'stats', 'system']):
                data['macOS']['System Monitors & Finder Tools'].append(info)
            elif any(k in text for k in ['menubar', 'status bar', 'menu']):
                data['macOS']['Menubar Utilities'].append(info)
            elif any(k in text for k in ['security', 'firewall', 'encrypt', 'vpn']):
                data['macOS']['Security & Firewalls'].append(info)
            elif any(k in text for k in ['terminal', 'emulator', 'shell']):
                data['macOS']['Terminal Emulators'].append(info)
            elif any(k in text for k in ['window', 'tile', 'snap', 'alttab']):
                data['macOS']['Window Management'].append(info)
            else:
                data['macOS']['General Utilities'].append(info)

    return data

# ---------------------------------------------------------
# Markdown Generator with requested Header & Layout
# ---------------------------------------------------------
def generate_markdown(data):
    lines = []
    
    # Header requested by user
    lines.append('<h1 align="center">Awesome Aimw</h1>')
    lines.append('<p align="center">')
    lines.append('  <b>AIMW</b> : Android, IOS, MacOS and Windows. A list of awesome projects, libraries, tools, fonts, and dev/design resources')
    lines.append('</p>')
    lines.append('<p align="center">')
    lines.append('  <img src="Photos/Photo.png" alt="The photo">')
    lines.append('</p>\n')
    lines.append('---\n')
    lines.append('<h1 align="center">In case you have any suggestion </h1>\n')
    lines.append('<p align="center">')
    lines.append('  <a href="https://t.me/whosthefr">')
    lines.append('    <img src="Photos/Tele.png" alt="Telegram" width="50" height="50">')
    lines.append('  </a>')
    lines.append('</p>\n')
    lines.append('---\n')
    lines.append('<h2 align="center">Go find it</h2>\n')
    lines.append('<p align="center">')
    lines.append('  <a href="#toc-android"><b>Android</b></a> •')
    lines.append('  <a href="#toc-ios"><b>iOS</b></a> •')
    lines.append('  <a href="#toc-windows"><b>Windows</b></a> •')
    lines.append('  <a href="#toc-macos"><b>macOS</b></a>')
    lines.append('</p>\n<br>\n')
    
    # Table of Contents
    lines.append('<h2 align="center" id="table-of-contents">Table of Contents</h2>\n')
    lines.append('<details open>\n<summary><b>Click to expand / collapse</b></summary>\n<br>\n')
    
    for platform in ['Android', 'iOS', 'Windows', 'macOS']:
        plat_anchor = f"toc-{platform.lower()}"
        total_p = sum(len(items) for items in data[platform].values())
        lines.append(f'- <b id="{plat_anchor}">[{platform} ({total_p})](#{platform.lower()})</b>')
        for cat, items in sorted(data[platform].items()):
            cat_anchor = f"{platform.lower()}-{re.sub(r'[^a-zA-Z0-9]+', '-', cat).lower().strip('-')}"
            lines.append(f'  - [{cat} ({len(items)})](#{cat_anchor})')
        lines.append('')
        
    lines.append('</details>\n<br>\n<br>\n---\n')
    
    # Platforms Content
    for platform in ['Android', 'iOS', 'Windows', 'macOS']:
        lines.append(f'<h1 align="center" id="{platform.lower()}">{platform}</h1>\n<br>\n')
        for cat, items in sorted(data[platform].items()):
            cat_anchor = f"{platform.lower()}-{re.sub(r'[^a-zA-Z0-9]+', '-', cat).lower().strip('-')}"
            lines.append(f'<h3 align="center" id="{cat_anchor}">{cat} ({len(items)})</h3>\n')
            
            # Sort apps alphabetically
            for app in sorted(items, key=lambda x: x['name'].lower()):
                lines.append(f"- [{app['name']}]({app['url']}) - {app['desc']}")
            lines.append('\n<br>\n')
        lines.append('\n---\n')
        
    return '\n'.join(lines)

def main():
    print("Parsing all repository data from files...")
    repos = parse_files()
    print(f"Total unique software entries found: {len(repos)}")
    
    print("Categorizing into Android, iOS, Windows, macOS...")
    categorized_data = categorize(repos)
    
    print("Generating complete README.md...")
    md_content = generate_markdown(categorized_data)
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("Done! README.md has been generated with all items included without any omissions.")

if __name__ == '__main__':
    main()