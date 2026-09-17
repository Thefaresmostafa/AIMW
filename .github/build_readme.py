import os
import re
from collections import defaultdict

# ----------------------------------------------------------------------
# 1. Regex to catch ALL formats (Markdown, HTML, angle brackets <http>)
# ----------------------------------------------------------------------
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^\s\)\"\']+)\)(?:\s*(?:—|-|:)\s*(.+))?')
RAW_URL_RE = re.compile(r'(?:<)?(https?://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)(?:>)?')

# Ignore non-project URLs
IGNORE_DOMAINS = [
    'shields.io', 'badge.svg', 'license', 'github.com/login',
    'actions/workflows', 'contrib.rocks', 't.me/whosthefr',
    'twitter.com', 'ko-fi.com', 'patreon.com', 'raw.githubusercontent.com'
]

def clean_str(s):
    if not s:
        return ""
    # Strip emojis and markup
    s = re.sub(r'[^\x00-\x7F]+', '', s)
    s = s.replace('**', '').replace('__', '').replace('`', '').strip()
    return s

def extract_from_line(line):
    line = line.strip()
    if not line:
        return None, None, None

    # Try Markdown format: [Name](URL) - Description
    md_match = MD_LINK_RE.search(line)
    if md_match:
        name = md_match.group(1).strip()
        url = md_match.group(2).strip()
        desc = md_match.group(3).strip() if md_match.group(3) else ""
        return name, url, desc

    # Try Raw GitHub URL format: <https://github.com/user/repo> or plain text
    raw_match = RAW_URL_RE.search(line)
    if raw_match:
        url = raw_match.group(1).strip()
        # Extract repo name from URL
        repo_name = url.split('/')[-1]
        desc = line.replace(raw_match.group(0), '').replace('<', '').replace('>', '').strip()
        desc = desc.lstrip(':-—#* \t')
        return repo_name, url, desc

    return None, None, None

def parse_all_files():
    repos = {}
    valid_extensions = ('.md', '.txt')
    
    # Target candidate files in the repo
    files_to_read = []
    for root, _, files in os.walk('.'):
        # Ignore .git and workflow directories
        if '/.' in root or '\\.' in root:
            continue
        for file in files:
            if file.endswith(valid_extensions):
                files_to_read.append(os.path.join(root, file))

    print(f"Scanning {len(files_to_read)} files for repository links...")

    for file_path in files_to_read:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    name, url, desc = extract_from_line(line)
                    if not url:
                        continue

                    # Filter junk/badge links
                    if any(bad in url.lower() for bad in IGNORE_DOMAINS):
                        continue
                    if url.endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
                        continue

                    if url not in repos:
                        clean_n = clean_str(name).split('/')[-1].strip()
                        clean_d = clean_str(desc)
                        
                        # Generate brief description if empty
                        if not clean_d or len(clean_d) < 3:
                            clean_d = "Open-source software and utility."
                        else:
                            words = clean_d.split()
                            clean_d = ' '.join(words[:7])
                            if not clean_d.endswith('.'):
                                clean_d += '.'

                        repos[url] = {
                            'name': clean_n if clean_n else name,
                            'url': url,
                            'desc': clean_d,
                            'raw': line.lower()
                        }
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return repos

# ----------------------------------------------------------------------
# 2. Granular Platform & Category Engine
# ----------------------------------------------------------------------
def categorize(repos):
    data = {
        'Android': defaultdict(list),
        'iOS': defaultdict(list),
        'Windows': defaultdict(list),
        'macOS': defaultdict(list)
    }

    for url, item in repos.items():
        text = (item['name'] + ' ' + item['desc'] + ' ' + item['raw'] + ' ' + url).lower()

        # 1. ANDROID
        if any(k in text for k in ['android', 'apk', 'f-droid', 'magisk', 'kernelsu', 'xposed', 'monet', 'material you', 'shizuku']):
            if any(k in text for k in ['store', 'f-droid', 'market', 'obtainium', 'sideload', 'installer']):
                data['Android']['App Stores & Sideloading'].append(item)
            elif any(k in text for k in ['patch', 'mod', 'telegram', 'instagram', 'reddit', 'piko']):
                data['Android']['App Mods & Patches'].append(item)
            elif any(k in text for k in ['revanced', 'morphe', 'xposed', 'lsposed', 'microg']):
                data['Android']['Patching Engines & Frameworks'].append(item)
            elif any(k in text for k in ['youtube', 'stream', 'anime', 'manga', 'newpipe', 'cloudstream', 'tv']):
                data['Android']['Online Video Streamers'].append(item)
            elif any(k in text for k in ['mpv', 'player', 'vlc', 'exoplayer', 'video player']):
                data['Android']['Offline Video Players'].append(item)
            elif any(k in text for k in ['video editor', 'cutter', 'trim', 'screen recorder']):
                data['Android']['Video Editors & Recorders'].append(item)
            elif any(k in text for k in ['spotify', 'music streaming', 'innertune', 'simpmusic', 'spotube']):
                data['Android']['Online Music Streamers'].append(item)
            elif any(k in text for k in ['audio player', 'music player', 'offline music', 'auxio', 'flac']):
                data['Android']['Offline Audio Players'].append(item)
            elif any(k in text for k in ['tts', 'speech', 'tag', 'lyrics', 'shazam', 'voice']):
                data['Android']['Audio Tools, Tagging & Speech'].append(item)
            elif any(k in text for k in ['download', 'torrent', 'aria2', 'ytdl']):
                data['Android']['Download Managers'].append(item)
            elif any(k in text for k in ['browser', 'chromium', 'firefox', 'gecko']):
                data['Android']['Web Browsers'].append(item)
            elif any(k in text for k in ['root', 'magisk', 'kernelsu', 'apatch', 'recovery', 'twrp']):
                data['Android']['Root Solutions & Kernels'].append(item)
            elif any(k in text for k in ['debloat', 'freeze', 'canta', 'uninstaller', 'appmanager']):
                data['Android']['System Debloaters & Package Tools'].append(item)
            elif any(k in text for k in ['firewall', 'adblock', 'dns', 'adaway', 'rethink']):
                data['Android']['Ad Blockers, Firewalls & DNS'].append(item)
            elif any(k in text for k in ['vpn', 'wireguard', 'tailscale', 'proxy', 'v2ray', 'tor']):
                data['Android']['VPNs, Proxies & Anonymity'].append(item)
            elif any(k in text for k in ['password', '2fa', 'authenticator', 'keepass', 'bitwarden']):
                data['Android']['Password Managers & 2FA'].append(item)
            elif any(k in text for k in ['file manager', 'explorer', 'archive', '7z', 'storage']):
                data['Android']['File Managers & Archivers'].append(item)
            elif any(k in text for k in ['pdf', 'scanner', 'ocr', 'reader', 'ebook', 'epub', 'koreader']):
                data['Android']['Document & E-Book Readers'].append(item)
            elif any(k in text for k in ['transfer', 'localsend', 'kde connect', 'remote', 'rustdesk']):
                data['Android']['File Transfer & Remote Control'].append(item)
            elif any(k in text for k in ['notes', 'markdown', 'logseq', 'joplin', 'knowledge', 'office']):
                data['Android']['Notes, Office & Productivity'].append(item)
            elif any(k in text for k in ['gallery', 'photo', 'camera', 'vault']):
                data['Android']['Photo Galleries & Vaults'].append(item)
            elif any(k in text for k in ['chat', 'messenger', 'matrix', 'simplex', 'mail', 'email']):
                data['Android']['Chat, Mail & Messaging'].append(item)
            elif any(k in text for k in ['keyboard', 'input', 'ime', 'heliboard', 'launcher']):
                data['Android']['Keyboards & Launchers'].append(item)
            elif any(k in text for k in ['map', 'navigation', 'gps', 'osm']):
                data['Android']['Maps & Navigation'].append(item)
            elif any(k in text for k in ['finance', 'budget', 'expense', 'money', 'health', 'fitness']):
                data['Android']['Finance & Health'].append(item)
            elif any(k in text for k in ['quran', 'islam', 'prayer', 'adhan', 'taqwa']):
                data['Android']['Religion & Islamic Apps'].append(item)
            elif any(k in text for k in ['weather', 'forecast']):
                data['Android']['Weather Apps'].append(item)
            elif any(k in text for k in ['emulator', 'retroarch', 'game']):
                data['Android']['Gaming & Emulation'].append(item)
            elif any(k in text for k in ['termux', 'ide', 'terminal', 'compiler', 'code']):
                data['Android']['Terminals & IDEs'].append(item)
            else:
                data['Android']['General Utilities'].append(item)

        # 2. IOS
        elif any(k in text for k in ['ios', 'iphone', 'ipad', 'ipa', 'swiftui', 'xcode', 'cocoapods']):
            if any(k in text for k in ['tweak', 'mod', 'jailbreak', 'ytkace', 'maxtube']):
                data['iOS']['App Mods & Tweaks'].append(item)
            elif any(k in text for k in ['sideload', 'ipatool', 'altstore', 'installer']):
                data['iOS']['Sideloading & Package Installers'].append(item)
            elif any(k in text for k in ['stream', 'video', 'player', 'youtube', 'vlc']):
                data['iOS']['Media & Video Players'].append(item)
            elif any(k in text for k in ['audio', 'sound', 'music', 'dsp', 'speech']):
                data['iOS']['Audio Synthesis & Speech'].append(item)
            elif any(k in text for k in ['networking', 'http', 'alamofire', 'socket', 'api']):
                data['iOS']['Networking & API Clients'].append(item)
            elif any(k in text for k in ['database', 'realm', 'sqlite', 'coredata', 'storage']):
                data['iOS']['Databases & Local Storage'].append(item)
            elif any(k in text for k in ['security', 'keychain', 'crypto', 'lock']):
                data['iOS']['Security, Crypto & Keychain'].append(item)
            elif any(k in text for k in ['layout', 'autolayout', 'snapkit', 'ui', 'view']):
                data['iOS']['UI Layout Engines & Components'].append(item)
            elif any(k in text for k in ['animation', 'lottie', 'transition']):
                data['iOS']['Animation & Transitions'].append(item)
            elif any(k in text for k in ['xcode', 'extension', 'plugin', 'linter']):
                data['iOS']['Xcode Extensions & Tooling'].append(item)
            else:
                data['iOS']['General iOS Utilities'].append(item)

        # 3. WINDOWS
        elif any(k in text for k in ['windows', 'win11', 'win10', 'powershell', 'reg add', 'defender', 'rufus']):
            if any(k in text for k in ['debloat', 'winutil', 'sophia', 'tweaker', 'optimizer']):
                data['Windows']['System Debloaters & Setup Tools'].append(item)
            elif any(k in text for k in ['defender', 'security', 'hardening', 'firewall']):
                data['Windows']['Windows Defender & Security Hardening'].append(item)
            elif any(k in text for k in ['update', 'store', 'wumgr', 'winget']):
                data['Windows']['Windows Update & Store Managers'].append(item)
            elif any(k in text for k in ['media', 'player', 'mpv', 'audio', 'stream', 'music']):
                data['Windows']['Media Players & Audio Streamers'].append(item)
            elif any(k in text for k in ['screen', 'recording', 'obs', 'editor', 'video']):
                data['Windows']['Video Editors & Screen Recorders'].append(item)
            elif any(k in text for k in ['ai', 'agent', 'llm', 'chatgpt', 'claude', 'coding']):
                data['Windows']['AI Coding Agents & Local LLMs'].append(item)
            elif any(k in text for k in ['download', 'torrent', 'idm', 'yt-dlp']):
                data['Windows']['Download Accelerators & Scrapers'].append(item)
            elif any(k in text for k in ['quran', 'islam', 'adhan']):
                data['Windows']['Islamic Apps'].append(item)
            else:
                data['Windows']['General Windows Tools'].append(item)

        # 4. MACOS
        else:
            if any(k in text for k in ['audio', 'sound', 'music', 'equalizer', 'daw', 'player']):
                data['macOS']['Audio, Players & Recording'].append(item)
            elif any(k in text for k in ['video', 'screen', 'obs', 'cut', 'transcode', 'movie']):
                data['macOS']['Video Players & Editors'].append(item)
            elif any(k in text for k in ['browser', 'safari', 'extension', 'pip']):
                data['macOS']['Browsers & Safari Extensions'].append(item)
            elif any(k in text for k in ['chat', 'message', 'mail', 'email', 'irc']):
                data['macOS']['Communication & Email'].append(item)
            elif any(k in text for k in ['database', 'sql', 'redis', 'postgres', 'mongo']):
                data['macOS']['Database Management Clients'].append(item)
            elif any(k in text for k in ['git', 'github', 'repo', 'version']):
                data['macOS']['Git GUI Clients'].append(item)
            elif any(k in text for k in ['api', 'developer', 'http', 'debug', 'json']):
                data['macOS']['API & Developer Tools'].append(item)
            elif any(k in text for k in ['download', 'torrent', 'transfer', 'sharing', 'cask']):
                data['macOS']['Downloaders & File Sharing'].append(item)
            elif any(k in text for k in ['editor', 'ide', 'code', 'markdown', 'notes', 'latex']):
                data['macOS']['Code, Text & Markdown Editors'].append(item)
            elif any(k in text for k in ['finder', 'cleaner', 'monitor', 'stats', 'system']):
                data['macOS']['System Monitors & Finder Tools'].append(item)
            elif any(k in text for k in ['menubar', 'status bar', 'menu']):
                data['macOS']['Menubar Utilities'].append(item)
            elif any(k in text for k in ['security', 'firewall', 'encrypt', 'vpn']):
                data['macOS']['Security & Firewalls'].append(item)
            elif any(k in text for k in ['terminal', 'emulator', 'shell']):
                data['macOS']['Terminal Emulators'].append(item)
            elif any(k in text for k in ['window', 'tile', 'snap', 'alttab']):
                data['macOS']['Window Management'].append(item)
            else:
                data['macOS']['General Utilities'].append(item)

    return data

# ----------------------------------------------------------------------
# 3. Final Formatter (Centered headers, TOC links, exact counts)
# ----------------------------------------------------------------------
def generate_markdown(data):
    lines = []
    
    # Exact header requested
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
            if not items:
                continue
            cat_anchor = f"{platform.lower()}-{re.sub(r'[^a-zA-Z0-9]+', '-', cat).lower().strip('-')}"
            lines.append(f'  - [{cat} ({len(items)})](#{cat_anchor})')
        lines.append('')
        
    lines.append('</details>\n<br>\n<br>\n---\n')
    
    # Platform Sections
    for platform in ['Android', 'iOS', 'Windows', 'macOS']:
        lines.append(f'<h1 align="center" id="{platform.lower()}">{platform}</h1>\n<br>\n')
        for cat, items in sorted(data[platform].items()):
            if not items:
                continue
            cat_anchor = f"{platform.lower()}-{re.sub(r'[^a-zA-Z0-9]+', '-', cat).lower().strip('-')}"
            lines.append(f'<h3 align="center" id="{cat_anchor}">{cat} ({len(items)})</h3>\n')
            
            # Alphabetical sort
            for app in sorted(items, key=lambda x: x['name'].lower()):
                lines.append(f"- [{app['name']}]({app['url']}) - {app['desc']}")
            lines.append('\n<br>\n')
        lines.append('\n---\n')
        
    return '\n'.join(lines)

def main():
    print("Collecting and parsing repository links...")
    repos = parse_all_files()
    total_found = len(repos)
    print(f"-> Total unique tools/apps found: {total_found}")
    
    # SAFETY GUARD: Never overwrite with empty content
    if total_found < 50:
        print("\n[ERROR] Safety guard triggered: Too few repositories found!")
        print("Make sure you committed your source txt/md files (e.g. stars.md, 2.md, etc.) to the repository.")
        print("Aborting without touching README.md.")
        return

    print("Categorizing tools across platforms...")
    categorized = categorize(repos)
    
    print("Rendering formatted Markdown...")
    content = generate_markdown(categorized)
    
    # Backup existing README if present
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8', errors='ignore') as f_old:
            with open('README.md.bak', 'w', encoding='utf-8') as f_bak:
                f_bak.write(f_old.read())
                
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("SUCCESS: README.md generated successfully with all links intact!")

if __name__ == '__main__':
    main()
