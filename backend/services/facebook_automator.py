"""
Facebook Automation Service
Real Facebook automation tasks using Selenium
"""

import asyncio
import time
import json
import base64
from typing import Dict, List, Optional
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

from services.chrome_manager import ChromeSession

logger = logging.getLogger(__name__)


class FacebookAutomator:
    """Facebook automation operations"""
    
    def __init__(self, chrome_session: ChromeSession):
        self.session = chrome_session
        self.driver = chrome_session.driver
        
    async def check_account_live(self) -> Dict:
        """Check if account is live/die/checkpoint"""
        try:
            logger.info(f"Checking account {self.session.account_uid} status...")
            
            # Navigate to profile
            self.driver.get('https://www.facebook.com/me')
            await asyncio.sleep(2)
            
            current_url = self.driver.current_url
            
            # Check for checkpoint
            if 'checkpoint' in current_url:
                screenshot = self._take_screenshot()
                return {
                    'success': True,
                    'status': 'checkpoint',
                    'message': 'Account in checkpoint',
                    'screenshot': screenshot
                }
            
            # Check for login page (dead cookies)
            if 'login' in current_url:
                screenshot = self._take_screenshot()
                return {
                    'success': True,
                    'status': 'die',
                    'message': 'Account cookies expired or invalid',
                    'screenshot': screenshot
                }
            
            # Try to get profile name
            try:
                name_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
                )
                account_name = name_element.text
                
                return {
                    'success': True,
                    'status': 'live',
                    'message': f'Account is active: {account_name}',
                    'account_name': account_name
                }
                
            except TimeoutException:
                screenshot = self._take_screenshot()
                return {
                    'success': True,
                    'status': 'unknown',
                    'message': 'Could not determine account status',
                    'screenshot': screenshot
                }
                
        except Exception as e:
            logger.error(f"Error checking account status: {e}")
            screenshot = self._take_screenshot()
            return {
                'success': False,
                'status': 'error',
                'message': str(e),
                'screenshot': screenshot
            }
    
    async def scan_groups(self, keyword: str, max_results: int = 20) -> List[Dict]:
        """Scan Facebook groups by keyword"""
        try:
            logger.info(f"Scanning groups for keyword: {keyword}")
            groups = []
            
            # Navigate to search
            search_url = f"https://www.facebook.com/search/groups/?q={keyword}"
            self.driver.get(search_url)
            await asyncio.sleep(3)
            
            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Find group elements
            group_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/groups/"]')
            
            seen_urls = set()
            for link in group_links[:max_results]:
                try:
                    href = link.get_attribute('href')
                    if href and '/groups/' in href and href not in seen_urls:
                        seen_urls.add(href)
                        
                        # Extract group ID from URL
                        group_id = href.split('/groups/')[-1].split('/')[0].split('?')[0]
                        
                        # Get group name
                        try:
                            name = link.text.strip()
                        except:
                            name = f"Group {group_id}"
                        
                        if name and group_id:
                            groups.append({
                                'id': group_id,
                                'name': name,
                                'url': href
                            })
                            
                except Exception as e:
                    logger.warning(f"Error parsing group: {e}")
                    continue
            
            logger.info(f"Found {len(groups)} groups for keyword: {keyword}")
            return groups
            
        except Exception as e:
            logger.error(f"Error scanning groups: {e}")
            raise
    
    async def join_group(self, group_id: str) -> Dict:
        """Join a Facebook group"""
        try:
            logger.info(f"Joining group: {group_id}")
            
            # Navigate to group
            group_url = f"https://www.facebook.com/groups/{group_id}"
            self.driver.get(group_url)
            await asyncio.sleep(3)
            
            # Find and click join button
            try:
                # Try multiple selectors for join button
                join_selectors = [
                    "//span[contains(text(), 'Join') or contains(text(), 'Tham gia')]",
                    "//div[@aria-label='Join group' or @aria-label='Tham gia nhóm']",
                    "//a[contains(@href, 'join')]"
                ]
                
                join_button = None
                for selector in join_selectors:
                    try:
                        join_button = self.driver.find_element(By.XPATH, selector)
                        if join_button:
                            break
                    except:
                        continue
                
                if join_button:
                    join_button.click()
                    await asyncio.sleep(2)
                    
                    # Handle any popup/confirmation
                    try:
                        confirm_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Join')]"))
                        )
                        confirm_button.click()
                        await asyncio.sleep(1)
                    except:
                        pass
                    
                    return {
                        'success': True,
                        'group_id': group_id,
                        'message': 'Successfully joined group'
                    }
                else:
                    # Check if already member
                    if 'Joined' in self.driver.page_source or 'Đã tham gia' in self.driver.page_source:
                        return {
                            'success': True,
                            'group_id': group_id,
                            'message': 'Already a member of this group'
                        }
                    else:
                        screenshot = self._take_screenshot()
                        return {
                            'success': False,
                            'group_id': group_id,
                            'message': 'Join button not found',
                            'screenshot': screenshot
                        }
                        
            except Exception as e:
                screenshot = self._take_screenshot()
                return {
                    'success': False,
                    'group_id': group_id,
                    'message': f'Error clicking join button: {str(e)}',
                    'screenshot': screenshot
                }
                
        except Exception as e:
            logger.error(f"Error joining group {group_id}: {e}")
            screenshot = self._take_screenshot()
            return {
                'success': False,
                'group_id': group_id,
                'message': str(e),
                'screenshot': screenshot
            }
    
    async def add_friend(self, profile_id: str) -> Dict:
        """Send friend request to a profile"""
        try:
            logger.info(f"Adding friend: {profile_id}")
            
            # Navigate to profile
            profile_url = f"https://www.facebook.com/{profile_id}"
            self.driver.get(profile_url)
            await asyncio.sleep(3)
            
            # Find and click add friend button
            try:
                add_friend_selectors = [
                    "//span[contains(text(), 'Add Friend') or contains(text(), 'Kết bạn')]",
                    "//div[@aria-label='Add Friend' or @aria-label='Thêm bạn bè']"
                ]
                
                add_button = None
                for selector in add_friend_selectors:
                    try:
                        add_button = self.driver.find_element(By.XPATH, selector)
                        if add_button:
                            break
                    except:
                        continue
                
                if add_button:
                    add_button.click()
                    await asyncio.sleep(2)
                    
                    return {
                        'success': True,
                        'profile_id': profile_id,
                        'message': 'Friend request sent'
                    }
                else:
                    # Check if already friends
                    if 'Friends' in self.driver.page_source or 'Bạn bè' in self.driver.page_source:
                        return {
                            'success': True,
                            'profile_id': profile_id,
                            'message': 'Already friends'
                        }
                    else:
                        screenshot = self._take_screenshot()
                        return {
                            'success': False,
                            'profile_id': profile_id,
                            'message': 'Add friend button not found',
                            'screenshot': screenshot
                        }
                        
            except Exception as e:
                screenshot = self._take_screenshot()
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'message': f'Error clicking add friend: {str(e)}',
                    'screenshot': screenshot
                }
                
        except Exception as e:
            logger.error(f"Error adding friend {profile_id}: {e}")
            screenshot = self._take_screenshot()
            return {
                'success': False,
                'profile_id': profile_id,
                'message': str(e),
                'screenshot': screenshot
            }
    
    async def post_to_timeline(self, content: str, images: Optional[List[str]] = None) -> Dict:
        """Post content to timeline"""
        try:
            logger.info("Posting to timeline")
            
            # Navigate to home
            self.driver.get('https://www.facebook.com')
            await asyncio.sleep(3)
            
            # Click on "What's on your mind?" post box
            try:
                post_box = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), \"What's on your mind\") or contains(text(), 'Bạn đang nghĩ gì')]"))
                )
                post_box.click()
                await asyncio.sleep(2)
                
                # Find text area
                text_area = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
                )
                
                # Type content
                text_area.send_keys(content)
                await asyncio.sleep(2)
                
                # TODO: Handle image upload if needed
                
                # Click Post button
                post_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Post') or contains(text(), 'Đăng')]")
                post_button.click()
                await asyncio.sleep(3)
                
                return {
                    'success': True,
                    'message': 'Post created successfully',
                    'content': content
                }
                
            except Exception as e:
                screenshot = self._take_screenshot()
                return {
                    'success': False,
                    'message': f'Error creating post: {str(e)}',
                    'screenshot': screenshot
                }
                
        except Exception as e:
            logger.error(f"Error posting to timeline: {e}")
            screenshot = self._take_screenshot()
            return {
                'success': False,
                'message': str(e),
                'screenshot': screenshot
            }
    
    async def comment_on_post(self, post_url: str, comment_text: str) -> Dict:
        """Comment on a Facebook post"""
        try:
            logger.info(f"Commenting on post: {post_url}")
            
            # Navigate to post
            self.driver.get(post_url)
            await asyncio.sleep(3)
            
            # Find comment box
            try:
                comment_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='comment' i]"))
                )
                
                comment_box.click()
                await asyncio.sleep(1)
                
                comment_box.send_keys(comment_text)
                await asyncio.sleep(1)
                
                # Press Enter to submit
                comment_box.send_keys(Keys.RETURN)
                await asyncio.sleep(2)
                
                return {
                    'success': True,
                    'message': 'Comment posted successfully',
                    'post_url': post_url,
                    'comment': comment_text
                }
                
            except Exception as e:
                screenshot = self._take_screenshot()
                return {
                    'success': False,
                    'message': f'Error posting comment: {str(e)}',
                    'screenshot': screenshot
                }
                
        except Exception as e:
            logger.error(f"Error commenting on post: {e}")
            screenshot = self._take_screenshot()
            return {
                'success': False,
                'message': str(e),
                'screenshot': screenshot
            }
    
    async def react_to_post(self, post_url: str, reaction_type: str = 'LIKE') -> Dict:
        """React to a Facebook post"""
        try:
            logger.info(f"Reacting to post: {post_url} with {reaction_type}")
            
            # Navigate to post
            self.driver.get(post_url)
            await asyncio.sleep(3)
            
            # Find like button
            try:
                like_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Like') or contains(text(), 'Thích')]"))
                )
                
                if reaction_type != 'LIKE':
                    # Hover to show reaction options
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(like_button).perform()
                    await asyncio.sleep(1)
                    
                    # Click specific reaction
                    reaction_map = {
                        'LOVE': 'Love',
                        'HAHA': 'Haha',
                        'WOW': 'Wow',
                        'SAD': 'Sad',
                        'ANGRY': 'Angry'
                    }
                    
                    if reaction_type in reaction_map:
                        reaction_button = self.driver.find_element(
                            By.XPATH, 
                            f"//span[contains(@aria-label, '{reaction_map[reaction_type]}')]"
                        )
                        reaction_button.click()
                else:
                    like_button.click()
                
                await asyncio.sleep(2)
                
                return {
                    'success': True,
                    'message': f'{reaction_type} reaction added',
                    'post_url': post_url,
                    'reaction': reaction_type
                }
                
            except Exception as e:
                screenshot = self._take_screenshot()
                return {
                    'success': False,
                    'message': f'Error reacting to post: {str(e)}',
                    'screenshot': screenshot
                }
                
        except Exception as e:
            logger.error(f"Error reacting to post: {e}")
            screenshot = self._take_screenshot()
            return {
                'success': False,
                'message': str(e),
                'screenshot': screenshot
            }
    
    def _take_screenshot(self) -> str:
        """Take screenshot and return as base64 string"""
        try:
            screenshot = self.driver.get_screenshot_as_png()
            screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
            logger.info(f"Screenshot captured for account {self.session.account_uid}")
            return screenshot_base64
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return ''
