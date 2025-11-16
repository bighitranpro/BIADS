#!/usr/bin/env python3
"""
Quick Database Viewer - Simple one-time view
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "backend" / "data" / "bi_ads.db"

def main():
    print("\n" + "="*80)
    print("  BI ADS DATABASE - QUICK VIEW")
    print("="*80 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Database Info
    print("📊 DATABASE INFO:")
    print(f"   Path: {DB_PATH}")
    print(f"   Size: {DB_PATH.stat().st_size / 1024:.2f} KB")
    
    # 2. Tables
    print("\n📋 TABLES:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]}: {count} rows")
    
    # 3. Accounts
    print("\n👥 ACCOUNTS (Top 10):")
    cursor.execute("""
        SELECT id, uid, name, status, 
               CASE WHEN proxy_id IS NOT NULL THEN '✓' ELSE '✗' END as proxy
        FROM accounts 
        LIMIT 10
    """)
    print(f"   {'ID':<5} {'UID':<20} {'Name':<25} {'Status':<10} {'Proxy'}")
    print(f"   {'-'*75}")
    for row in cursor.fetchall():
        print(f"   {row[0]:<5} {row[1]:<20} {row[2][:25]:<25} {row[3]:<10} {row[4]}")
    
    # 4. Proxies
    print("\n🌐 PROXIES:")
    cursor.execute("""
        SELECT p.id, p.ip || ':' || p.port as address, p.protocol, 
               COUNT(a.id) as accounts_using
        FROM proxies p
        LEFT JOIN accounts a ON p.id = a.proxy_id
        GROUP BY p.id
    """)
    print(f"   {'ID':<5} {'Address':<25} {'Protocol':<10} {'Accounts'}")
    print(f"   {'-'*50}")
    for row in cursor.fetchall():
        print(f"   {row[0]:<5} {row[1]:<25} {row[2]:<10} {row[3]}")
    
    # 5. Recent Tasks
    print("\n⚙️  RECENT TASKS (Last 10):")
    cursor.execute("""
        SELECT t.id, t.task_type, t.status, t.progress, 
               datetime(t.created_at, 'localtime') as created
        FROM tasks t
        ORDER BY t.created_at DESC
        LIMIT 10
    """)
    print(f"   {'ID':<5} {'Type':<20} {'Status':<12} {'Progress':<10} {'Created'}")
    print(f"   {'-'*75}")
    for row in cursor.fetchall():
        print(f"   {row[0]:<5} {row[1]:<20} {row[2]:<12} {row[3]}%{'':<7} {row[4]}")
    
    # 6. Recent Logs
    print("\n📝 RECENT LOGS (Last 10):")
    cursor.execute("""
        SELECT l.level, l.action, l.message, 
               datetime(l.created_at, 'localtime') as created
        FROM activity_logs l
        ORDER BY l.created_at DESC
        LIMIT 10
    """)
    print(f"   {'Level':<10} {'Action':<20} {'Message':<30} {'Created'}")
    print(f"   {'-'*90}")
    for row in cursor.fetchall():
        msg = row[2][:30] if len(row[2]) > 30 else row[2]
        print(f"   {row[0]:<10} {row[1]:<20} {msg:<30} {row[3]}")
    
    # 7. Statistics
    print("\n📈 STATISTICS:")
    cursor.execute("SELECT status, COUNT(*) FROM accounts GROUP BY status")
    print("   Accounts by status:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]}")
    
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    print("   Tasks by status:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("  Để xem chi tiết hơn, sử dụng: python3 db_viewer.py")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
