"""
Telegram Bot Integration for Bi Ads Multi Tool PRO
Send notifications and receive commands via Telegram
Author: Bi Ads Team
Version: 3.0.0
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

class TelegramBot:
    """Telegram Bot API wrapper"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', '')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Make request to Telegram API"""
        if not self.bot_token:
            print("⚠️  Telegram bot token not configured")
            return None
        
        url = f"{self.api_url}/{method}"
        
        try:
            if params:
                data = urllib.parse.urlencode(params).encode('utf-8')
                req = urllib.request.Request(url, data=data)
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
        
        except Exception as e:
            print(f"❌ Telegram API error: {e}")
            return None
    
    def send_message(
        self, 
        text: str, 
        chat_id: str = None,
        parse_mode: str = 'HTML',
        disable_notification: bool = False
    ) -> bool:
        """
        Send a message via Telegram
        
        Args:
            text: Message text
            chat_id: Target chat ID (uses default if not provided)
            parse_mode: 'HTML', 'Markdown', or None
            disable_notification: Silent message if True
        
        Returns:
            bool: Success status
        """
        target_chat = chat_id or self.chat_id
        
        if not target_chat:
            print("⚠️  Telegram chat ID not configured")
            return False
        
        params = {
            'chat_id': target_chat,
            'text': text,
            'disable_notification': disable_notification
        }
        
        if parse_mode:
            params['parse_mode'] = parse_mode
        
        result = self._make_request('sendMessage', params)
        
        if result and result.get('ok'):
            print(f"✅ Message sent to Telegram")
            return True
        else:
            print(f"❌ Failed to send Telegram message")
            return False
    
    def send_notification(
        self,
        title: str,
        message: str,
        level: str = 'info',
        extra_data: Dict = None
    ) -> bool:
        """
        Send formatted notification
        
        Args:
            title: Notification title
            message: Notification message
            level: 'success', 'info', 'warning', 'error'
            extra_data: Additional data to include
        
        Returns:
            bool: Success status
        """
        # Emoji based on level
        emoji_map = {
            'success': '✅',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌'
        }
        
        emoji = emoji_map.get(level, 'ℹ️')
        
        # Format message
        formatted_message = f"{emoji} <b>{title}</b>\n\n{message}"
        
        # Add timestamp
        formatted_message += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Add extra data
        if extra_data:
            formatted_message += "\n\n<b>Chi tiết:</b>"
            for key, value in extra_data.items():
                formatted_message += f"\n• {key}: {value}"
        
        return self.send_message(formatted_message)
    
    def send_task_notification(
        self,
        task_type: str,
        account_name: str,
        status: str,
        details: Dict = None
    ) -> bool:
        """
        Send task completion notification
        
        Args:
            task_type: Type of task (join_groups, add_friends, etc.)
            account_name: Account name that executed the task
            status: 'completed', 'failed', 'processing'
            details: Additional details
        
        Returns:
            bool: Success status
        """
        status_emoji = {
            'completed': '✅',
            'failed': '❌',
            'processing': '⏳'
        }
        
        emoji = status_emoji.get(status, '🔄')
        
        title = f"Tác vụ {task_type.replace('_', ' ').title()}"
        message = f"<b>Tài khoản:</b> {account_name}\n<b>Trạng thái:</b> {status}"
        
        extra_data = details or {}
        
        return self.send_notification(title, message, status, extra_data)
    
    def send_webhook_notification(
        self,
        event_type: str,
        event_data: Dict
    ) -> bool:
        """
        Send notification about Facebook webhook event
        
        Args:
            event_type: Type of event
            event_data: Event data from Facebook
        
        Returns:
            bool: Success status
        """
        title = f"Sự kiện Facebook: {event_type}"
        
        # Format message based on event type
        if event_type == 'post':
            message = f"Bài viết mới"
            if event_data.get('message'):
                message += f"\n\n{event_data['message'][:100]}..."
        
        elif event_type == 'comment':
            message = f"Bình luận mới"
            if event_data.get('message'):
                message += f"\n\n{event_data['message'][:100]}..."
        
        elif event_type == 'reaction':
            reaction = event_data.get('reaction_type', 'unknown')
            message = f"Reaction mới: {reaction}"
        
        else:
            message = "Có sự kiện mới"
        
        return self.send_notification(title, message, 'info', event_data)
    
    def send_error_alert(
        self,
        error_message: str,
        context: Dict = None
    ) -> bool:
        """
        Send error alert
        
        Args:
            error_message: Error description
            context: Additional context
        
        Returns:
            bool: Success status
        """
        return self.send_notification(
            "Lỗi hệ thống",
            error_message,
            'error',
            context
        )
    
    def get_updates(self, offset: int = None) -> Optional[List[Dict]]:
        """
        Get updates from Telegram
        
        Args:
            offset: Update ID to start from
        
        Returns:
            List of updates or None
        """
        params = {}
        if offset:
            params['offset'] = offset
        
        result = self._make_request('getUpdates', params)
        
        if result and result.get('ok'):
            return result.get('result', [])
        
        return None
    
    def handle_command(self, command: str, args: List[str]) -> str:
        """
        Handle bot commands
        
        Args:
            command: Command name (without /)
            args: Command arguments
        
        Returns:
            Response message
        """
        if command == 'start':
            return "👋 Xin chào! Tôi là Bi Ads Bot.\n\nSử dụng /help để xem danh sách lệnh."
        
        elif command == 'help':
            return """
📋 <b>Danh sách lệnh:</b>

/start - Bắt đầu
/help - Hiển thị trợ giúp
/status - Kiểm tra trạng thái hệ thống
/tasks - Xem danh sách tasks
/accounts - Xem danh sách accounts
/stats - Xem thống kê
"""
        
        elif command == 'status':
            return "✅ Hệ thống đang hoạt động bình thường"
        
        elif command == 'tasks':
            # TODO: Get from database
            return "📋 Danh sách tasks:\n\n(Chức năng đang phát triển)"
        
        elif command == 'accounts':
            # TODO: Get from database
            return "👤 Danh sách accounts:\n\n(Chức năng đang phát triển)"
        
        elif command == 'stats':
            # TODO: Get from database
            return "📊 Thống kê hệ thống:\n\n(Chức năng đang phát triển)"
        
        else:
            return f"❌ Lệnh không hợp lệ: /{command}\n\nSử dụng /help để xem danh sách lệnh."


# Example usage
if __name__ == "__main__":
    # Test bot
    bot = TelegramBot(
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        chat_id=os.getenv('TELEGRAM_CHAT_ID')
    )
    
    # Test sending message
    if bot.bot_token and bot.chat_id:
        print("Testing Telegram notifications...")
        
        # Simple message
        bot.send_message("🧪 Test message from Bi Ads")
        
        # Formatted notification
        bot.send_notification(
            "Test Notification",
            "This is a test notification",
            'info',
            {'test_key': 'test_value'}
        )
        
        # Task notification
        bot.send_task_notification(
            'join_groups',
            'test_account',
            'completed',
            {'groups_joined': 5, 'success_rate': '100%'}
        )
    else:
        print("⚠️  Bot token or chat ID not configured")
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment")
