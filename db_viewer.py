#!/usr/bin/env python3
"""
Bi Ads Database Viewer
Simple tool to view and query database
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent / "backend" / "data" / "bi_ads.db"

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def connect_db():
    """Kết nối database"""
    if not DB_PATH.exists():
        print(f"{Colors.FAIL}❌ Database không tồn tại: {DB_PATH}{Colors.ENDC}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def print_header(title):
    """In header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{Colors.ENDC}\n")

def print_row(columns, widths):
    """In một row"""
    row_str = " | ".join(str(col)[:width].ljust(width) for col, width in zip(columns, widths))
    print(f"| {row_str} |")

def print_table(cursor, title=None):
    """In bảng dữ liệu"""
    if title:
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}{title}{Colors.ENDC}")
    
    # Lấy column names
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    if not rows:
        print(f"{Colors.WARNING}  Không có dữ liệu{Colors.ENDC}")
        return
    
    # Tính width cho mỗi column
    widths = [max(len(str(col)), 15) for col in columns]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Print header
    print(f"\n{Colors.BOLD}", end="")
    print_row(columns, widths)
    print(f"{'-' * (sum(widths) + len(widths) * 3 + 1)}{Colors.ENDC}")
    
    # Print rows
    for row in rows:
        print_row(row, widths)
    
    print(f"\n{Colors.OKGREEN}  Tổng: {len(rows)} rows{Colors.ENDC}")

def view_accounts():
    """Xem tất cả tài khoản"""
    print_header("📱 ACCOUNTS - TÀI KHOẢN FACEBOOK")
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            a.id,
            a.uid,
            a.name,
            a.username,
            a.status,
            a.method,
            CASE WHEN a.proxy_id IS NOT NULL THEN 'Yes' ELSE 'No' END as has_proxy,
            a.created_at
        FROM accounts a
        ORDER BY a.id
    """)
    
    print_table(cursor, "Danh sách tài khoản")
    
    # Statistics
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count
        FROM accounts
        GROUP BY status
    """)
    
    print_table(cursor, "📊 Thống kê theo status")
    
    conn.close()

def view_proxies():
    """Xem tất cả proxy"""
    print_header("🌐 PROXIES - DANH SÁCH PROXY")
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.id,
            p.ip || ':' || p.port as address,
            p.protocol,
            p.username,
            p.status,
            p.location,
            COUNT(a.id) as accounts_using
        FROM proxies p
        LEFT JOIN accounts a ON p.id = a.proxy_id
        GROUP BY p.id
        ORDER BY p.id
    """)
    
    print_table(cursor, "Danh sách proxy")
    conn.close()

def view_tasks():
    """Xem tasks"""
    print_header("⚙️  TASKS - TÁC VỤ AUTOMATION")
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            t.id,
            t.task_id,
            a.name as account_name,
            t.task_type,
            t.status,
            t.progress || '%' as progress,
            t.created_at
        FROM tasks t
        LEFT JOIN accounts a ON t.account_id = a.id
        ORDER BY t.created_at DESC
        LIMIT 20
    """)
    
    print_table(cursor, "20 tasks gần nhất")
    
    # Statistics
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count
        FROM tasks
        GROUP BY status
    """)
    
    print_table(cursor, "📊 Thống kê theo status")
    conn.close()

def view_logs(limit=30):
    """Xem logs"""
    print_header("📝 ACTIVITY LOGS - NHẬT KÝ HOẠT ĐỘNG")
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute(f"""
        SELECT 
            l.id,
            l.level,
            a.name as account,
            l.action,
            l.message,
            l.created_at
        FROM activity_logs l
        LEFT JOIN accounts a ON l.account_id = a.id
        ORDER BY l.created_at DESC
        LIMIT {limit}
    """)
    
    print_table(cursor, f"{limit} logs gần nhất")
    
    # Statistics
    cursor.execute("""
        SELECT 
            level,
            COUNT(*) as count
        FROM activity_logs
        WHERE created_at > datetime('now', '-24 hours')
        GROUP BY level
    """)
    
    print_table(cursor, "📊 Logs trong 24h qua")
    conn.close()

def view_stats():
    """Xem statistics tổng quan"""
    print_header("📊 DATABASE STATISTICS - THỐNG KÊ TỔNG QUAN")
    conn = connect_db()
    cursor = conn.cursor()
    
    # Row counts
    cursor.execute("""
        SELECT 'accounts' as table_name, COUNT(*) as rows FROM accounts
        UNION ALL
        SELECT 'proxies', COUNT(*) FROM proxies
        UNION ALL
        SELECT 'tasks', COUNT(*) FROM tasks
        UNION ALL
        SELECT 'activity_logs', COUNT(*) FROM activity_logs
        UNION ALL
        SELECT 'sub_accounts', COUNT(*) FROM sub_accounts
        UNION ALL
        SELECT 'facebook_ids', COUNT(*) FROM facebook_ids
        UNION ALL
        SELECT 'posted_content', COUNT(*) FROM posted_content
        UNION ALL
        SELECT 'messages', COUNT(*) FROM messages
    """)
    
    print_table(cursor, "Số lượng records")
    
    # Database info
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}Database Information{Colors.ENDC}")
    print(f"  Path: {DB_PATH}")
    print(f"  Size: {DB_PATH.stat().st_size / 1024:.2f} KB")
    print(f"  Last Modified: {datetime.fromtimestamp(DB_PATH.stat().st_mtime)}")
    
    conn.close()

def custom_query():
    """Chạy custom SQL query"""
    print_header("💻 CUSTOM SQL QUERY")
    print(f"{Colors.WARNING}Nhập câu lệnh SQL (hoặc 'exit' để thoát):{Colors.ENDC}")
    print(f"{Colors.WARNING}Ví dụ: SELECT * FROM accounts LIMIT 5{Colors.ENDC}\n")
    
    conn = connect_db()
    
    while True:
        try:
            query = input(f"{Colors.OKBLUE}SQL> {Colors.ENDC}").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                break
            
            if not query:
                continue
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            if cursor.description:  # SELECT query
                print_table(cursor)
            else:  # INSERT/UPDATE/DELETE
                conn.commit()
                print(f"{Colors.OKGREEN}✅ Query executed successfully. Rows affected: {cursor.rowcount}{Colors.ENDC}")
        
        except sqlite3.Error as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Interrupted{Colors.ENDC}")
            break
    
    conn.close()

def show_menu():
    """Hiển thị menu"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           BI ADS DATABASE VIEWER v1.0                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print(f"{Colors.OKCYAN}Chọn chức năng:{Colors.ENDC}")
    print(f"  {Colors.BOLD}1.{Colors.ENDC} Xem Accounts (Tài khoản)")
    print(f"  {Colors.BOLD}2.{Colors.ENDC} Xem Proxies (Proxy)")
    print(f"  {Colors.BOLD}3.{Colors.ENDC} Xem Tasks (Tác vụ)")
    print(f"  {Colors.BOLD}4.{Colors.ENDC} Xem Logs (Nhật ký)")
    print(f"  {Colors.BOLD}5.{Colors.ENDC} Xem Statistics (Thống kê)")
    print(f"  {Colors.BOLD}6.{Colors.ENDC} Custom SQL Query")
    print(f"  {Colors.BOLD}0.{Colors.ENDC} Thoát")

def main():
    """Main function"""
    while True:
        show_menu()
        
        try:
            choice = input(f"\n{Colors.OKGREEN}Nhập lựa chọn (0-6): {Colors.ENDC}").strip()
            
            if choice == '1':
                view_accounts()
            elif choice == '2':
                view_proxies()
            elif choice == '3':
                view_tasks()
            elif choice == '4':
                view_logs()
            elif choice == '5':
                view_stats()
            elif choice == '6':
                custom_query()
            elif choice == '0':
                print(f"\n{Colors.OKGREEN}👋 Tạm biệt!{Colors.ENDC}\n")
                break
            else:
                print(f"{Colors.FAIL}❌ Lựa chọn không hợp lệ!{Colors.ENDC}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKGREEN}👋 Tạm biệt!{Colors.ENDC}\n")
            break
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()
