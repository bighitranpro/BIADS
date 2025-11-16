"""
Bi Ads - Sample Data Generator
Author: Bi Ads Team
Version: 3.0.0
"""

import asyncio
from datetime import datetime, timedelta
import random

from database import AsyncSessionLocal, init_db
import crud

# Sample data pools
VIETNAMESE_NAMES = [
    "Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D", "Hoàng Văn E",
    "Vũ Thị F", "Đặng Văn G", "Bùi Thị H", "Đỗ Văn I", "Ngô Thị K",
    "Dương Văn L", "Phan Thị M", "Võ Văn N", "Hồ Thị O", "Lý Văn P"
]

VIETNAMESE_LOCATIONS = [
    "Hà Nội, Việt Nam", "TP. Hồ Chí Minh, Việt Nam", "Đà Nẵng, Việt Nam",
    "Hải Phòng, Việt Nam", "Cần Thơ, Việt Nam", "Nha Trang, Việt Nam",
    "Huế, Việt Nam", "Vũng Tàu, Việt Nam", "Đà Lạt, Việt Nam", "Hội An, Việt Nam"
]

POST_CONTENTS = [
    "Chúc mọi người một ngày tốt lành! 😊",
    "Hôm nay thật đẹp trời! ☀️",
    "Chia sẻ một số hình ảnh đẹp về cuộc sống 📸",
    "Cảm ơn mọi người đã ủng hộ! 🙏",
    "Sản phẩm mới vừa ra mắt, mời mọi người xem qua! 🎉",
    "Live stream tối nay lúc 8h nhé các bạn! 🎥",
    "Giveaway cho 100 người đầu tiên comment! 🎁",
    "Chia sẻ kinh nghiệm làm marketing Facebook",
    "Tutorial về Facebook Ads cho người mới bắt đầu",
    "Top 10 tips để tăng tương tác trên Facebook"
]

MESSAGE_TEMPLATES = [
    "Xin chào! Bạn có thể cho tôi biết thêm thông tin không?",
    "Cảm ơn bạn đã quan tâm đến sản phẩm của chúng tôi",
    "Bạn cần hỗ trợ gì không?",
    "Chào bạn! Tôi đang online, hãy nhắn tin cho tôi nhé",
    "Thanks for your message! I'll get back to you soon.",
    "Sản phẩm này còn hàng không shop?",
    "Giá bao nhiêu vậy bạn?",
    "Có ship COD không ạ?",
    "Đặt hàng như thế nào?",
    "Cho tôi xem thêm hình ảnh được không?"
]

async def generate_sample_accounts(count=5):
    """Generate sample main accounts"""
    async with AsyncSessionLocal() as db:
        accounts = []
        for i in range(count):
            account_data = {
                'uid': f'100000{i:06d}',
                'name': VIETNAMESE_NAMES[i % len(VIETNAMESE_NAMES)],
                'username': f'user{i}',
                'email': f'user{i}@example.com',
                'status': random.choice(['active', 'active', 'active', 'inactive']),
                'method': 'cookies'
            }
            account = await crud.create_account(db, account_data)
            accounts.append(account)
        
        print(f"✅ Created {len(accounts)} sample accounts")
        return accounts

async def generate_sample_sub_accounts(main_accounts, count=10):
    """Generate sample sub accounts"""
    async with AsyncSessionLocal() as db:
        sub_accounts = []
        for i in range(count):
            main_account = random.choice(main_accounts)
            sub_account_data = {
                'main_account_id': main_account.id,
                'uid': f'200000{i:06d}',
                'name': f"Sub {VIETNAMESE_NAMES[i % len(VIETNAMESE_NAMES)]}",
                'username': f'subuser{i}',
                'status': random.choice(['active', 'active', 'inactive', 'banned']),
                'auto_like': random.choice([True, True, False]),
                'auto_comment': random.choice([True, False, False]),
                'auto_share': random.choice([True, False, False])
            }
            sub_account = await crud.create_sub_account(db, sub_account_data)
            sub_accounts.append(sub_account)
        
        print(f"✅ Created {len(sub_accounts)} sample sub accounts")
        return sub_accounts

async def generate_sample_facebook_ids(accounts, count=50):
    """Generate sample Facebook IDs"""
    async with AsyncSessionLocal() as db:
        fb_ids = []
        sources = ['manual', 'import', 'scan_group', 'scan_post']
        
        for i in range(count):
            account = random.choice(accounts)
            fb_id_data = {
                'uid': f'300000{i:06d}',
                'name': VIETNAMESE_NAMES[i % len(VIETNAMESE_NAMES)],
                'username': f'fbuser{i}',
                'profile_url': f'https://facebook.com/fbuser{i}',
                'status': random.choice(['valid', 'valid', 'valid', 'invalid', 'used']),
                'is_friend': random.choice([True, False, False]),
                'source': random.choice(sources),
                'source_id': f'group_{random.randint(1000, 9999)}' if random.random() > 0.5 else None,
                'collected_by_account_id': account.id
            }
            fb_id = await crud.create_facebook_id(db, fb_id_data)
            fb_ids.append(fb_id)
        
        print(f"✅ Created {len(fb_ids)} sample Facebook IDs")
        return fb_ids

async def generate_sample_ip_addresses(accounts, count=20):
    """Generate sample IP addresses"""
    async with AsyncSessionLocal() as db:
        ips = []
        
        for i in range(count):
            # Generate Vietnamese IP addresses
            ip_parts = [random.randint(1, 255) for _ in range(4)]
            ip_address = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3]}"
            
            used_accounts = [random.choice(accounts).id for _ in range(random.randint(1, 3))]
            
            ip_data = {
                'ip_address': ip_address,
                'location': random.choice(VIETNAMESE_LOCATIONS),
                'country_code': 'VN',
                'status': random.choice(['active', 'active', 'active', 'blocked', 'trusted']),
                'is_proxy': random.choice([True, False, False]),
                'used_by_accounts': used_accounts,
                'is_blocked': random.choice([False, False, False, True]),
                'access_count': random.randint(1, 100)
            }
            ip = await crud.create_ip_address(db, ip_data)
            ips.append(ip)
        
        print(f"✅ Created {len(ips)} sample IP addresses")
        return ips

async def generate_sample_whitelist(accounts, count=30):
    """Generate sample whitelist accounts"""
    async with AsyncSessionLocal() as db:
        whitelists = []
        types = ['vip', 'customer', 'partner', 'admin', 'friend']
        
        for i in range(count):
            account = random.choice(accounts)
            whitelist_data = {
                'uid': f'400000{i:06d}',
                'name': VIETNAMESE_NAMES[i % len(VIETNAMESE_NAMES)],
                'username': f'vipuser{i}',
                'type': random.choice(types),
                'status': random.choice(['active', 'active', 'inactive']),
                'friendship_status': random.choice(['friend', 'friend', 'not_friend', 'pending']),
                'auto_accept_request': random.choice([True, True, False]),
                'auto_like_posts': random.choice([True, True, False]),
                'priority_messaging': random.choice([True, False, False]),
                'never_unfriend': random.choice([True, True, False]),
                'added_by_account_id': account.id
            }
            whitelist = await crud.create_whitelist_account(db, whitelist_data)
            whitelists.append(whitelist)
        
        print(f"✅ Created {len(whitelists)} sample whitelist accounts")
        return whitelists

async def generate_sample_posts(accounts, count=40):
    """Generate sample posted content"""
    async with AsyncSessionLocal() as db:
        posts = []
        post_types = ['text', 'image', 'video', 'link']
        
        for i in range(count):
            account = random.choice(accounts)
            post_data = {
                'post_id': f'post_{i:06d}',
                'account_id': account.id,
                'content': random.choice(POST_CONTENTS),
                'post_url': f'https://facebook.com/{account.uid}/posts/{i}',
                'post_type': random.choice(post_types),
                'like_count': random.randint(0, 1000),
                'comment_count': random.randint(0, 200),
                'share_count': random.randint(0, 100),
                'status': random.choice(['published', 'published', 'published', 'hidden'])
            }
            post = await crud.create_posted_content(db, post_data)
            posts.append(post)
        
        print(f"✅ Created {len(posts)} sample posts")
        return posts

async def generate_sample_messages(accounts, count=100):
    """Generate sample messages"""
    async with AsyncSessionLocal() as db:
        messages = []
        
        # Create some conversations
        num_conversations = 10
        for conv_id in range(num_conversations):
            conversation_id = f'conv_{conv_id:04d}'
            num_messages = random.randint(5, 15)
            
            account = random.choice(accounts)
            other_uid = f'500000{conv_id:06d}'
            other_name = VIETNAMESE_NAMES[conv_id % len(VIETNAMESE_NAMES)]
            
            for msg_id in range(num_messages):
                is_sent_by_me = random.choice([True, False])
                
                message_data = {
                    'conversation_id': conversation_id,
                    'account_id': account.id,
                    'sender_uid': account.uid if is_sent_by_me else other_uid,
                    'sender_name': account.name if is_sent_by_me else other_name,
                    'receiver_uid': other_uid if is_sent_by_me else account.uid,
                    'receiver_name': other_name if is_sent_by_me else account.name,
                    'message_text': random.choice(MESSAGE_TEMPLATES),
                    'message_type': random.choice(['text', 'text', 'text', 'image', 'link']),
                    'is_read': random.choice([True, True, False]),
                    'is_sent_by_me': is_sent_by_me,
                    'sent_at': datetime.now() - timedelta(hours=random.randint(0, 48))
                }
                message = await crud.create_message(db, message_data)
                messages.append(message)
        
        print(f"✅ Created {len(messages)} sample messages in {num_conversations} conversations")
        return messages

async def generate_all_sample_data():
    """Generate all sample data"""
    print("\n" + "="*60)
    print("🎲 GENERATING SAMPLE DATA FOR BI ADS MULTI TOOL PRO v3.0")
    print("="*60 + "\n")
    
    # Initialize database
    print("📊 Initializing database...")
    await init_db()
    
    # Generate data in order (respecting foreign key dependencies)
    print("\n1️⃣ Generating main accounts...")
    accounts = await generate_sample_accounts(5)
    
    print("\n2️⃣ Generating sub accounts...")
    sub_accounts = await generate_sample_sub_accounts(accounts, 10)
    
    print("\n3️⃣ Generating Facebook IDs...")
    fb_ids = await generate_sample_facebook_ids(accounts, 50)
    
    print("\n4️⃣ Generating IP addresses...")
    ips = await generate_sample_ip_addresses(accounts, 20)
    
    print("\n5️⃣ Generating whitelist accounts...")
    whitelists = await generate_sample_whitelist(accounts, 30)
    
    print("\n6️⃣ Generating posted content...")
    posts = await generate_sample_posts(accounts, 40)
    
    print("\n7️⃣ Generating messages...")
    messages = await generate_sample_messages(accounts, 100)
    
    print("\n" + "="*60)
    print("✅ SAMPLE DATA GENERATION COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   - Main Accounts: {len(accounts)}")
    print(f"   - Sub Accounts: {len(sub_accounts)}")
    print(f"   - Facebook IDs: {len(fb_ids)}")
    print(f"   - IP Addresses: {len(ips)}")
    print(f"   - Whitelist Accounts: {len(whitelists)}")
    print(f"   - Posted Content: {len(posts)}")
    print(f"   - Messages: {len(messages)}")
    print(f"\n   TOTAL: {len(accounts) + len(sub_accounts) + len(fb_ids) + len(ips) + len(whitelists) + len(posts) + len(messages)} records")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(generate_all_sample_data())
