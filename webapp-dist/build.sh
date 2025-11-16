#!/bin/bash
# Build script for Bi Ads Multi Tool PRO Web App

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
DIST_FILE="bi-ads-webapp-v3.0.0.tar.gz"

echo "================================"
echo "🏗️  Building Bi Ads Web App"
echo "================================"

# Clean previous build
if [ -d "$BUILD_DIR" ]; then
    echo "🗑️  Cleaning previous build..."
    rm -rf "$BUILD_DIR"
fi

# Create build directory
echo "📁 Creating build directory..."
mkdir -p "$BUILD_DIR/bi-ads-webapp"

# Copy files
echo "📦 Copying files..."
cp -r "$SCRIPT_DIR/css" "$BUILD_DIR/bi-ads-webapp/"
cp -r "$SCRIPT_DIR/js" "$BUILD_DIR/bi-ads-webapp/"
cp "$SCRIPT_DIR/index.html" "$BUILD_DIR/bi-ads-webapp/"
cp "$SCRIPT_DIR/server.py" "$BUILD_DIR/bi-ads-webapp/"

# Create README
echo "📝 Creating README..."
cat > "$BUILD_DIR/bi-ads-webapp/README.md" << 'EOF'
# Bi Ads Multi Tool PRO - Web Application v3.0.0

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Backend API running on port 8000

### Installation

1. Extract the archive:
```bash
tar -xzf bi-ads-webapp-v3.0.0.tar.gz
cd bi-ads-webapp
```

2. Start the web server:
```bash
python3 server.py
```

3. Open your browser:
```
http://localhost:3000
```

## 📋 Requirements

The web app requires the backend API to be running. Make sure backend is accessible at:
- Local: http://localhost:8000
- Network: http://<backend-ip>:8000

## 🔧 Configuration

Edit `js/config.js` to change API URL if needed.

## 📖 Features

- ✅ Dashboard with statistics
- ✅ Account management
- ✅ Proxy management
- ✅ Task management
- ✅ Activity logs
- ✅ Import/Export data
- ✅ Responsive design

## 🆘 Support

For issues and questions:
- Check backend is running: http://localhost:8000/health
- Check browser console for errors
- Ensure CORS is enabled on backend

## 📦 Package Contents

- `index.html` - Main HTML file
- `css/` - Stylesheets
- `js/` - JavaScript modules
- `server.py` - Simple HTTP server
- `README.md` - This file

## 🔐 Security Notes

- This is a development server, not for production
- For production, use nginx or apache
- Configure proper CORS and authentication

---
**Version:** 3.0.0
**Author:** Bi Ads Team
**License:** Proprietary
EOF

# Create start script
echo "📝 Creating start script..."
cat > "$BUILD_DIR/bi-ads-webapp/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 Starting Bi Ads Web App..."
python3 server.py
EOF
chmod +x "$BUILD_DIR/bi-ads-webapp/start.sh"

# Create start script for Windows
cat > "$BUILD_DIR/bi-ads-webapp/start.bat" << 'EOF'
@echo off
echo Starting Bi Ads Web App...
python server.py
pause
EOF

# Create package
echo "📦 Creating archive..."
cd "$BUILD_DIR"
tar -czf "$DIST_FILE" bi-ads-webapp/

# Calculate size
SIZE=$(du -h "$DIST_FILE" | cut -f1)

echo ""
echo "================================"
echo "✅ Build completed successfully!"
echo "================================"
echo "📦 Package: $BUILD_DIR/$DIST_FILE"
echo "📊 Size: $SIZE"
echo ""
echo "To deploy:"
echo "  1. Extract: tar -xzf $DIST_FILE"
echo "  2. Run: cd bi-ads-webapp && ./start.sh"
echo ""
