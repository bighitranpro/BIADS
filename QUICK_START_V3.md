# 🚀 Bi Ads Multi Tool PRO v3.0 - Quick Start Guide

## 📍 You Are Here: `/home/bighitran1905/webapp`

This is the **CORRECT** directory with all v3.0 upgrades!

**NOT** `/home/bighitran1905/MULTI_TOOL_GUI_PRO` ❌

---

## 🎯 Quick Start (3 Simple Steps)

### Option 1: Automated Startup Script (Recommended) ⭐

```bash
cd /home/bighitran1905/webapp
./START_V3.sh
```

This script will:
- ✅ Check/install Python dependencies automatically
- ✅ Create .env from template if needed
- ✅ Start backend server
- ✅ Start Electron frontend
- ✅ Show all URLs and status

### Option 2: Manual Startup

#### Step 1: Install Dependencies

```bash
cd /home/bighitran1905/webapp

# Install Python dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install Node.js dependencies (if not done yet)
npm install
```

#### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required variables:**
- `FACEBOOK_APP_ID` - Your Facebook app ID
- `FACEBOOK_APP_SECRET` - Your Facebook app secret
- `FACEBOOK_VERIFY_TOKEN` - Token for webhook verification
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

#### Step 3: Start Application

**Terminal 1 - Backend:**
```bash
cd /home/bighitran1905/webapp/backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd /home/bighitran1905/webapp
npm start
```

---

## 🔗 Access URLs

Once running:
- **Frontend**: Electron app window (opens automatically)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🆘 Common Issues

### Issue 1: "No such file or directory"

**Problem**: You're in the wrong directory (`MULTI_TOOL_GUI_PRO`)

**Solution**:
```bash
cd /home/bighitran1905/webapp
```

### Issue 2: "Missing script: start"

**Problem**: You're in the wrong directory

**Solution**:
```bash
cd /home/bighitran1905/webapp
npm start
```

### Issue 3: "No module named 'fastapi'"

**Problem**: Python dependencies not installed

**Solution**:
```bash
cd /home/bighitran1905/webapp/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 4: Backend won't start

**Problem**: Port 8000 already in use

**Solution**:
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
cd /home/bighitran1905/webapp/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

## 📚 Setup Facebook Webhook

1. Go to: https://developers.facebook.com
2. Select your app → **Webhooks**
3. Click **"Edit Subscription"**
4. Configure:
   - **Callback URL**: `https://your-domain.com/webhook`
   - **Verify Token**: (from your .env file)
   - **Subscribe to**: `feed`, `comments`, `reactions`, `mention`
5. Click **"Verify and Save"**

**Note**: For local testing, use ngrok:
```bash
ngrok http 8000
# Use the ngrok URL as callback URL
```

---

## 📱 Setup Telegram Bot

1. Open Telegram, find **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create bot
4. Copy **Bot Token** → Add to `.env`
5. Find **@userinfobot**, message it
6. Copy your **Chat ID** → Add to `.env`
7. Message your bot once to activate it

**Test in app**:
- Go to Settings page
- Click "Test thông báo" button
- Check Telegram for test message

---

## 🎯 What's New in v3.0

### ✨ Major Features

1. **Facebook Webhook** 📡
   - Real-time posts, comments, reactions, mentions
   - Automatic notifications to Telegram

2. **Telegram Bot** 📱
   - Instant notifications
   - Bot commands: /start, /help, /status, /tasks

3. **Settings Page** ⚙️
   - Configure everything in one place
   - Test Telegram notifications
   - Webhook setup guide

4. **Plugin System** 🔌
   - Extensible architecture
   - Plugin store
   - Easy install/enable/disable

5. **Help System** ❓
   - Comprehensive documentation
   - Searchable guides
   - Step-by-step tutorials

6. **Professional UI** 🎨
   - Modern gradient design
   - Smooth animations
   - Responsive layout

---

## 📊 File Structure

```
/home/bighitran1905/webapp/          ← YOU ARE HERE
├── backend/
│   ├── main.py                      ← Backend API
│   ├── facebook_webhook.py          ← NEW: Webhook handler
│   ├── telegram_bot.py              ← NEW: Telegram integration
│   ├── requirements.txt             ← Python dependencies
│   └── venv/                        ← Virtual environment
├── renderer/
│   ├── index.html                   ← Main UI
│   ├── settings.html                ← NEW: Settings page
│   ├── plugins.html                 ← NEW: Plugin manager
│   ├── help.html                    ← NEW: Documentation
│   └── *.js, *.css                  ← Frontend code
├── .env.example                     ← Configuration template
├── package.json                     ← Node dependencies
├── START_V3.sh                      ← Startup script ⭐
└── UPGRADE_V3.0_CHANGELOG.md        ← Full changelog

/home/bighitran1905/MULTI_TOOL_GUI_PRO/   ← OLD DIRECTORY (Don't use!)
```

---

## 🧪 Test Your Installation

### 1. Test Backend API
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "webhook": "active",
  "telegram_configured": true
}
```

### 2. Test Telegram Bot
- Open Settings page in app
- Click "Test thông báo" button
- Check Telegram for message

### 3. Test Webhook
```bash
curl -X GET "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test123"
```

Expected response: `test123`

---

## 📞 Need Help?

### Documentation
- **In-App Help**: Click "❓ Trợ giúp" in the app
- **Changelog**: `UPGRADE_V3.0_CHANGELOG.md`
- **Environment Config**: `.env.example`

### Support
- **Email**: support@biads.com
- **Telegram**: @BiAdsSupport

---

## ✅ Checklist Before First Run

- [ ] In correct directory: `/home/bighitran1905/webapp`
- [ ] Python dependencies installed
- [ ] Node.js dependencies installed  
- [ ] `.env` file created and configured
- [ ] Facebook app credentials added
- [ ] Telegram bot token added
- [ ] Backend starts without errors
- [ ] Frontend opens in Electron

---

## 🎉 You're Ready!

Run the startup script:
```bash
cd /home/bighitran1905/webapp
./START_V3.sh
```

Enjoy **Bi Ads Multi Tool PRO v3.0**! 🚀

---

*Version 3.0.0 Professional Enterprise Edition*
