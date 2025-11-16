"""
Chrome Manager Service
Manages Chrome instances with Selenium WebDriver for Facebook automation
"""

import asyncio
import json
from typing import Dict, Optional, List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

logger = logging.getLogger(__name__)


class ChromeSession:
    """Represents a Chrome browser session for a Facebook account"""
    
    def __init__(self, account_id: int, account_uid: str, proxy: Optional[Dict] = None):
        self.account_id = account_id
        self.account_uid = account_uid
        self.proxy = proxy
        self.driver: Optional[webdriver.Chrome] = None
        self.is_headless = True
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.status = 'initializing'  # initializing, ready, busy, error, closed
        
    def create_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Create Chrome WebDriver instance"""
        chrome_options = Options()
        
        # Basic options
        if headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Proxy configuration
        if self.proxy:
            proxy_string = self._build_proxy_string()
            chrome_options.add_argument(f'--proxy-server={proxy_string}')
        
        # Window size
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Disable images for faster loading (optional)
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        
        # Create driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        # Execute CDP commands to hide webdriver
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver = driver
        self.is_headless = headless
        self.status = 'ready'
        
        return driver
    
    def _build_proxy_string(self) -> str:
        """Build proxy string from proxy dict"""
        if not self.proxy:
            return ''
        
        protocol = self.proxy.get('protocol', 'http')
        ip = self.proxy['ip']
        port = self.proxy['port']
        
        if self.proxy.get('username') and self.proxy.get('password'):
            return f"{protocol}://{self.proxy['username']}:{self.proxy['password']}@{ip}:{port}"
        else:
            return f"{protocol}://{ip}:{port}"
    
    async def login_facebook(self, cookies: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None, two_fa_key: Optional[str] = None) -> bool:
        """Login to Facebook using cookies or credentials"""
        try:
            if not self.driver:
                self.create_driver(headless=True)
            
            self.status = 'busy'
            self.driver.get('https://www.facebook.com')
            
            # Login with cookies (preferred method)
            if cookies:
                try:
                    cookies_list = json.loads(cookies)
                    for cookie in cookies_list:
                        self.driver.add_cookie(cookie)
                    
                    self.driver.refresh()
                    await asyncio.sleep(2)
                    
                    # Check if logged in
                    if self._is_logged_in():
                        self.status = 'ready'
                        logger.info(f"Account {self.account_uid} logged in successfully with cookies")
                        return True
                except Exception as e:
                    logger.error(f"Cookie login failed: {e}")
            
            # Login with email/password
            if email and password:
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "email"))
                    )
                    email_field.send_keys(email)
                    
                    pass_field = self.driver.find_element(By.ID, "pass")
                    pass_field.send_keys(password)
                    
                    login_button = self.driver.find_element(By.NAME, "login")
                    login_button.click()
                    
                    await asyncio.sleep(3)
                    
                    # Check for 2FA prompt
                    if two_fa_key and self._check_2fa_prompt():
                        logger.info(f"2FA prompt detected for account {self.account_uid}")
                        if await self._handle_2fa(two_fa_key):
                            logger.info(f"2FA handled successfully for account {self.account_uid}")
                            await asyncio.sleep(2)
                    
                    if self._is_logged_in():
                        self.status = 'ready'
                        logger.info(f"Account {self.account_uid} logged in successfully with credentials")
                        return True
                    else:
                        logger.warning(f"Account {self.account_uid} login failed - checkpoint or wrong credentials")
                        self.status = 'error'
                        return False
                except Exception as e:
                    logger.error(f"Credential login failed: {e}")
                    self.status = 'error'
                    return False
            
            self.status = 'error'
            return False
            
        except Exception as e:
            logger.error(f"Login error for account {self.account_uid}: {e}")
            self.status = 'error'
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if successfully logged in to Facebook"""
        try:
            # Check for logged-in indicators
            current_url = self.driver.current_url
            
            # If redirected to checkpoint or login page, not logged in
            if 'checkpoint' in current_url or 'login' in current_url:
                return False
            
            # Check for navigation elements that only appear when logged in
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="navigation"]')
            return len(nav_elements) > 0
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def _check_2fa_prompt(self) -> bool:
        """Check if 2FA prompt is shown"""
        try:
            # Check for 2FA code input field
            two_fa_selectors = [
                "input[name='approvals_code']",
                "input[id='approvals_code']",
                "input[placeholder*='code']",
                "input[placeholder*='mã']"
            ]
            
            for selector in two_fa_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info("2FA prompt detected")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking 2FA prompt: {e}")
            return False
    
    async def _handle_2fa(self, two_fa_key: str) -> bool:
        """Handle 2FA authentication"""
        try:
            import pyotp
            
            # Generate TOTP code from secret key
            totp = pyotp.TOTP(two_fa_key)
            code = totp.now()
            
            logger.info(f"Generated 2FA code: {code}")
            
            # Find 2FA input field
            two_fa_selectors = [
                "input[name='approvals_code']",
                "input[id='approvals_code']",
                "input[placeholder*='code']",
                "input[placeholder*='mã']"
            ]
            
            code_input = None
            for selector in two_fa_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    code_input = elements[0]
                    break
            
            if not code_input:
                logger.error("2FA input field not found")
                return False
            
            # Enter 2FA code
            code_input.clear()
            code_input.send_keys(code)
            await asyncio.sleep(1)
            
            # Find and click submit button
            submit_selectors = [
                "button[name='submit[Continue]']",
                "button[type='submit']",
                "button:contains('Continue')",
                "button:contains('Tiếp tục')",
                "input[type='submit']"
            ]
            
            for selector in submit_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if buttons:
                        buttons[0].click()
                        logger.info("2FA submit button clicked")
                        await asyncio.sleep(3)
                        return True
                except:
                    continue
            
            # If no submit button found, try pressing Enter
            from selenium.webdriver.common.keys import Keys
            code_input.send_keys(Keys.RETURN)
            logger.info("2FA code submitted via Enter key")
            await asyncio.sleep(3)
            
            return True
            
        except ImportError:
            logger.error("pyotp library not installed. Install with: pip install pyotp")
            return False
        except Exception as e:
            logger.error(f"Error handling 2FA: {e}")
            return False
    
    async def toggle_headless(self) -> bool:
        """Toggle between headless and visible mode"""
        if not self.driver:
            return False
        
        try:
            # Save current cookies and URL
            current_url = self.driver.current_url
            cookies = self.driver.get_cookies()
            
            # Close current driver
            self.driver.quit()
            
            # Create new driver with opposite mode
            new_headless = not self.is_headless
            self.create_driver(headless=new_headless)
            
            # Restore session
            self.driver.get('https://www.facebook.com')
            await asyncio.sleep(1)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Failed to add cookie: {e}")
            
            await asyncio.sleep(1)
            self.driver.get(current_url)
            await asyncio.sleep(2)
            
            logger.info(f"Account {self.account_uid} toggled to {'headless' if new_headless else 'visible'} mode")
            return True
            
        except Exception as e:
            logger.error(f"Error toggling headless mode: {e}")
            return False
    
    def close(self):
        """Close the browser session"""
        if self.driver:
            try:
                self.driver.quit()
                self.status = 'closed'
                logger.info(f"Chrome session closed for account {self.account_uid}")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
        
        self.driver = None
    
    def to_dict(self) -> Dict:
        """Convert session info to dictionary"""
        return {
            'account_id': self.account_id,
            'account_uid': self.account_uid,
            'is_headless': self.is_headless,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'has_proxy': self.proxy is not None,
            'proxy_ip': self.proxy.get('ip') if self.proxy else None
        }


class ChromeManager:
    """Manages multiple Chrome sessions for different accounts"""
    
    def __init__(self):
        self.sessions: Dict[int, ChromeSession] = {}  # account_id -> ChromeSession
        self.lock = asyncio.Lock()
    
    async def create_session(self, account_id: int, account_uid: str, 
                           cookies: Optional[str] = None, 
                           email: Optional[str] = None, 
                           password: Optional[str] = None,
                           two_fa_key: Optional[str] = None,
                           proxy: Optional[Dict] = None,
                           headless: bool = True) -> ChromeSession:
        """Create and login a new Chrome session"""
        async with self.lock:
            # Close existing session if any
            if account_id in self.sessions:
                await self.close_session(account_id)
            
            # Create new session
            session = ChromeSession(account_id, account_uid, proxy)
            session.create_driver(headless=headless)
            
            # Login
            success = await session.login_facebook(cookies, email, password, two_fa_key)
            
            if success:
                self.sessions[account_id] = session
                logger.info(f"Chrome session created for account {account_uid}")
            else:
                session.close()
                raise Exception(f"Failed to login account {account_uid}")
            
            return session
    
    async def get_session(self, account_id: int) -> Optional[ChromeSession]:
        """Get existing session by account ID"""
        return self.sessions.get(account_id)
    
    async def close_session(self, account_id: int):
        """Close a specific session"""
        if account_id in self.sessions:
            self.sessions[account_id].close()
            del self.sessions[account_id]
            logger.info(f"Session closed for account_id {account_id}")
    
    async def close_all_sessions(self):
        """Close all active sessions"""
        for account_id in list(self.sessions.keys()):
            await self.close_session(account_id)
        
        logger.info("All Chrome sessions closed")
    
    async def toggle_session_visibility(self, account_id: int) -> bool:
        """Toggle headless/visible mode for a session"""
        session = self.sessions.get(account_id)
        if session:
            return session.toggle_headless()
        return False
    
    def get_all_sessions(self) -> List[Dict]:
        """Get info of all active sessions"""
        return [session.to_dict() for session in self.sessions.values()]
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)


# Global Chrome Manager instance
chrome_manager = ChromeManager()
