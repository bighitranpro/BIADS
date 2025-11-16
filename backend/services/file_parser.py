"""
Bi Ads - File Parser Utilities
Author: Bi Ads Team
Version: 2.0.0
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime

def parse_via_txt(content: str) -> List[Dict[str, Any]]:
    """
    Parse via.txt format file
    Format: UID|username|2FA|cookies|token|email||date
    
    Example:
    61582525118131|mmm022|BWILM5GU2LODZLOE7KPKBFXROI25ZFNM|c_user=61582525118131;xs=26:38L7ic6hGPLpOg:2:1762880335:-1:-1;fr=08NcdVM3e0ALN7iOb...|EAAAAUaZA8jlABPwUveJtnEocGE3Ja6RwRy1EiyxPT2pG4g6y78hBH8sWy5OyaJDeJgUFtZC2l4gZAcJjsNgQXpGKCww1DjjEWb2Y2EuBXlGLMAYAbWpDYwv8ZAZCNEkIzYUHhQrcdH25oJHvpOnf613dZBRnVNuMAIxmz8SxdX4jUREMqZBipUVcoAlsxxKs5silmhCou8ySQZDZD|adv71b1b93gu@dropinboxes.com||23/10/2025 02:02
    """
    accounts = []
    lines = content.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
        
        try:
            parts = line.split('|')
            
            # Ensure we have at least the minimum required fields
            if len(parts) < 8:
                print(f"⚠️  Line {line_num}: Invalid format, skipping")
                continue
            
            uid = parts[0].strip()
            username = parts[1].strip()
            two_fa_key = parts[2].strip()
            cookies_str = parts[3].strip()
            access_token = parts[4].strip()
            email = parts[5].strip()
            # parts[6] is usually empty
            date_str = parts[7].strip() if len(parts) > 7 else ''
            
            # Parse cookies from string format to dict
            cookies = parse_cookies_string(cookies_str) if cookies_str else None
            
            # Create account dict
            account = {
                'uid': uid,
                'username': username,
                'name': username,  # Use username as default name
                'email': email if email else None,
                'cookies': cookies,
                'access_token': access_token if access_token else None,
                'two_fa_key': two_fa_key if two_fa_key else None,
                'status': 'active',
                'method': 'cookies' if cookies else ('token' if access_token else 'email'),
                'imported_date': date_str
            }
            
            accounts.append(account)
            
        except Exception as e:
            print(f"⚠️  Error parsing line {line_num}: {str(e)}")
            continue
    
    return accounts

def parse_cookies_string(cookies_str: str) -> List[Dict[str, Any]]:
    """
    Parse cookies from string format to list of cookie dicts
    
    Supports formats:
    - c_user=123;xs=abc;fr=xyz
    - [{"name":"c_user","value":"123"}]
    """
    if not cookies_str:
        return []
    
    # Try to parse as JSON first
    if cookies_str.startswith('['):
        try:
            import json
            return json.loads(cookies_str)
        except:
            pass
    
    # Parse as key=value; format
    cookies = []
    pairs = cookies_str.split(';')
    
    for pair in pairs:
        pair = pair.strip()
        if '=' not in pair:
            continue
        
        name, value = pair.split('=', 1)
        name = name.strip()
        value = value.strip()
        
        if name and value:
            cookies.append({
                'name': name,
                'value': value,
                'domain': '.facebook.com',
                'path': '/',
                'secure': True,
                'httpOnly': True
            })
    
    return cookies

def parse_proxy_txt(content: str) -> List[Dict[str, Any]]:
    """
    Parse proxy.txt format file
    
    Supports formats:
    - IP:PORT
    - IP:PORT:USERNAME:PASSWORD
    - http://IP:PORT
    - http://USERNAME:PASSWORD@IP:PORT
    - socks5://IP:PORT
    """
    proxies = []
    lines = content.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
        
        try:
            proxy = parse_proxy_line(line)
            if proxy:
                proxies.append(proxy)
            else:
                print(f"⚠️  Line {line_num}: Invalid proxy format, skipping")
        except Exception as e:
            print(f"⚠️  Error parsing line {line_num}: {str(e)}")
            continue
    
    return proxies

def parse_proxy_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single proxy line into dict"""
    
    # Check for protocol prefix
    protocol = 'http'
    if line.startswith('http://'):
        protocol = 'http'
        line = line[7:]
    elif line.startswith('https://'):
        protocol = 'https'
        line = line[8:]
    elif line.startswith('socks5://'):
        protocol = 'socks5'
        line = line[9:]
    elif line.startswith('socks4://'):
        protocol = 'socks4'
        line = line[9:]
    
    username = None
    password = None
    
    # Check for authentication in URL format: USERNAME:PASSWORD@IP:PORT
    if '@' in line:
        auth_part, server_part = line.split('@', 1)
        if ':' in auth_part:
            username, password = auth_part.split(':', 1)
        line = server_part
    
    # Parse IP:PORT or IP:PORT:USERNAME:PASSWORD
    parts = line.split(':')
    
    if len(parts) < 2:
        return None
    
    ip = parts[0].strip()
    
    try:
        port = int(parts[1].strip())
    except ValueError:
        return None
    
    # Check for username:password at the end
    if len(parts) >= 4 and not username:
        username = parts[2].strip()
        password = parts[3].strip()
    
    # Validate IP format (basic check)
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, ip):
        return None
    
    return {
        'ip': ip,
        'port': port,
        'username': username,
        'password': password,
        'protocol': protocol,
        'status': 'active'
    }

def validate_account_data(account: Dict[str, Any]) -> bool:
    """Validate account data before import"""
    
    # UID is required
    if not account.get('uid'):
        return False
    
    # At least one authentication method is required
    has_cookies = bool(account.get('cookies'))
    has_token = bool(account.get('access_token'))
    has_email = bool(account.get('email'))
    
    if not (has_cookies or has_token or has_email):
        return False
    
    return True

def validate_proxy_data(proxy: Dict[str, Any]) -> bool:
    """Validate proxy data before import"""
    
    # IP and port are required
    if not proxy.get('ip') or not proxy.get('port'):
        return False
    
    # Validate port range
    port = proxy.get('port')
    if not isinstance(port, int) or port < 1 or port > 65535:
        return False
    
    return True

def format_cookies_for_browser(cookies: List[Dict[str, Any]]) -> str:
    """Format cookies list to browser-compatible string"""
    if not cookies:
        return ''
    
    parts = []
    for cookie in cookies:
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        if name and value:
            parts.append(f"{name}={value}")
    
    return '; '.join(parts)

def extract_uid_from_cookies(cookies: List[Dict[str, Any]]) -> Optional[str]:
    """Extract Facebook UID from cookies"""
    for cookie in cookies:
        if cookie.get('name') == 'c_user':
            return cookie.get('value')
    return None

# Statistics helpers
def get_import_stats(accounts: List[Dict[str, Any]], proxies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get statistics about imported data"""
    
    total_accounts = len(accounts)
    accounts_with_cookies = sum(1 for a in accounts if a.get('cookies'))
    accounts_with_token = sum(1 for a in accounts if a.get('access_token'))
    accounts_with_2fa = sum(1 for a in accounts if a.get('two_fa_key'))
    accounts_with_email = sum(1 for a in accounts if a.get('email'))
    
    total_proxies = len(proxies)
    proxies_with_auth = sum(1 for p in proxies if p.get('username'))
    
    return {
        'accounts': {
            'total': total_accounts,
            'with_cookies': accounts_with_cookies,
            'with_token': accounts_with_token,
            'with_2fa': accounts_with_2fa,
            'with_email': accounts_with_email
        },
        'proxies': {
            'total': total_proxies,
            'with_auth': proxies_with_auth,
            'http': sum(1 for p in proxies if p.get('protocol') == 'http'),
            'socks5': sum(1 for p in proxies if p.get('protocol') == 'socks5')
        }
    }
