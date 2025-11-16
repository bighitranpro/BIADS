#!/usr/bin/env python3
"""
Simple HTTP Server for Bi Ads Multi Tool PRO Web App
Serves static files from current directory
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 5000
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types and SPA support"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        # Cache control
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def do_GET(self):
        # SPA support - serve index.html for all routes except assets
        if not self.path.startswith(('/css/', '/js/', '/assets/', '/data/')):
            if not Path(DIRECTORY, self.path.lstrip('/')).exists():
                self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Custom log format
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")
        sys.stdout.flush()

def main():
    """Start the web server"""
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), CustomHTTPRequestHandler) as httpd:
            print("=" * 60)
            print(f"🚀 Bi Ads Multi Tool PRO - Web Server")
            print("=" * 60)
            print(f"📁 Serving directory: {DIRECTORY}")
            print(f"🌐 Server running at: http://0.0.0.0:{PORT}")
            print(f"🌐 Local access: http://localhost:{PORT}")
            print(f"🌐 Network access: http://<your-ip>:{PORT}")
            print("=" * 60)
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Error: Port {PORT} is already in use")
            print(f"   Try: lsof -i:{PORT} to find the process")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
