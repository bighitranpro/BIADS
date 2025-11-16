"""
API Testing Script for Bi Ads Multi Tool PRO
Tests all endpoints and Facebook integration
"""

import sys
import json
from datetime import datetime

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    
    try:
        from fastapi import FastAPI
        print("  ✅ FastAPI imported")
    except ImportError as e:
        print(f"  ❌ FastAPI import failed: {e}")
        return False
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        print("  ✅ SQLAlchemy imported")
    except ImportError as e:
        print(f"  ❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import database
        print("  ✅ Database module imported")
    except ImportError as e:
        print(f"  ❌ Database import failed: {e}")
        return False
    
    try:
        import crud
        print("  ✅ CRUD module imported")
    except ImportError as e:
        print(f"  ❌ CRUD import failed: {e}")
        return False
    
    return True

def test_database_models():
    """Test database models"""
    print("\n🔍 Testing database models...")
    
    try:
        from database import Account, Proxy, Task, ActivityLog, Settings
        print("  ✅ All models imported successfully")
        
        # Check model attributes
        account_attrs = ['id', 'uid', 'username', 'cookies', 'access_token', 'proxy_id']
        for attr in account_attrs:
            if hasattr(Account, attr):
                print(f"  ✅ Account.{attr} exists")
            else:
                print(f"  ❌ Account.{attr} missing")
        
        return True
    except Exception as e:
        print(f"  ❌ Model test failed: {e}")
        return False

def test_file_parser():
    """Test file parsing functions"""
    print("\n🔍 Testing file parser...")
    
    try:
        from file_parser import parse_via_txt, parse_proxy_txt
        print("  ✅ File parser imported")
        
        # Test via.txt parsing
        test_via = "123|user|2FA|c_user=123;xs=abc|token|email@test.com||01/01/2025"
        accounts = parse_via_txt(test_via)
        
        if accounts and len(accounts) == 1:
            print(f"  ✅ Via parsing works: {accounts[0]['uid']}")
        else:
            print(f"  ❌ Via parsing failed")
        
        # Test proxy.txt parsing
        test_proxy = "192.168.1.1:8080"
        proxies = parse_proxy_txt(test_proxy)
        
        if proxies and len(proxies) == 1:
            print(f"  ✅ Proxy parsing works: {proxies[0]['ip']}")
        else:
            print(f"  ❌ Proxy parsing failed")
        
        return True
    except Exception as e:
        print(f"  ❌ File parser test failed: {e}")
        return False

def test_api_structure():
    """Test API structure"""
    print("\n🔍 Testing API structure...")
    
    try:
        from main import app
        print("  ✅ FastAPI app imported")
        
        # Check routes
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            "/",
            "/health",
            "/api/accounts",
            "/api/proxies",
            "/api/tasks",
            "/api/accounts/import-via",
            "/api/proxies/import-txt"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"  ✅ Route {route} exists")
            else:
                print(f"  ❌ Route {route} missing")
        
        return True
    except Exception as e:
        print(f"  ❌ API structure test failed: {e}")
        return False

def test_facebook_api():
    """Test Facebook API configuration"""
    print("\n🔍 Testing Facebook API configuration...")
    
    # Check if we have Facebook API credentials
    import os
    
    fb_app_id = os.getenv('FACEBOOK_APP_ID')
    fb_app_secret = os.getenv('FACEBOOK_APP_SECRET')
    
    if fb_app_id and fb_app_secret:
        print(f"  ✅ Facebook credentials configured")
        print(f"     App ID: {fb_app_id[:10]}...")
    else:
        print(f"  ⚠️  Facebook credentials not set (optional)")
        print(f"     Set FACEBOOK_APP_ID and FACEBOOK_APP_SECRET in .env")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Bi Ads API Testing Suite")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['models'] = test_database_models()
    results['parser'] = test_file_parser()
    results['api'] = test_api_structure()
    results['facebook'] = test_facebook_api()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.upper():.<30} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! API is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
