#!/bin/bash

###############################################################################
# Bi Ads Database Restore Script
# Restore database từ backup file
###############################################################################

# Configuration
DB_PATH="backend/data/bi_ads.db"
BACKUP_DIR="backups/database"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Bi Ads Database Restore"
echo "=========================================="
echo

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory không tồn tại: $BACKUP_DIR${NC}"
    exit 1
fi

# List available backups
echo -e "${BLUE}📋 Available backups:${NC}\n"
BACKUPS=($(ls -t "$BACKUP_DIR"/bi_ads_*.db.gz 2>/dev/null))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo -e "${RED}❌ Không tìm thấy backup nào${NC}"
    exit 1
fi

# Display backups with numbers
for i in "${!BACKUPS[@]}"; do
    SIZE=$(du -h "${BACKUPS[$i]}" | cut -f1)
    FILENAME=$(basename "${BACKUPS[$i]}")
    echo -e "  ${GREEN}[$((i+1))]${NC} $FILENAME ($SIZE)"
done

echo

# Prompt for selection
read -p "Chọn backup để restore (1-${#BACKUPS[@]}), hoặc 0 để hủy: " choice

if [ "$choice" -eq 0 ] 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Restore cancelled${NC}"
    exit 0
fi

if [ "$choice" -lt 1 ] || [ "$choice" -gt ${#BACKUPS[@]} ] 2>/dev/null; then
    echo -e "${RED}❌ Lựa chọn không hợp lệ${NC}"
    exit 1
fi

SELECTED_BACKUP="${BACKUPS[$((choice-1))]}"
echo -e "\n${BLUE}Selected:${NC} $(basename "$SELECTED_BACKUP")"

# Confirm restore
echo -e "\n${YELLOW}⚠️  WARNING: Current database will be backed up and replaced!${NC}"
read -p "Confirm restore? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}⚠️  Restore cancelled${NC}"
    exit 0
fi

# Backup current database
if [ -f "$DB_PATH" ]; then
    echo -e "\n💾 Backing up current database..."
    CURRENT_BACKUP="$BACKUP_DIR/bi_ads_before_restore_$(date +%Y%m%d_%H%M%S).db"
    cp "$DB_PATH" "$CURRENT_BACKUP"
    gzip "$CURRENT_BACKUP"
    echo -e "${GREEN}✅ Current database backed up to: ${CURRENT_BACKUP}.gz${NC}"
fi

# Decompress backup
echo -e "\n🗜️  Decompressing backup..."
TEMP_FILE="/tmp/bi_ads_restore_temp.db"
gunzip -c "$SELECTED_BACKUP" > "$TEMP_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Decompression failed${NC}"
    exit 1
fi

# Restore database
echo -e "🔄 Restoring database..."
cp "$TEMP_FILE" "$DB_PATH"

if [ $? -eq 0 ]; then
    rm "$TEMP_FILE"
    DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo -e "${GREEN}✅ Database restored successfully!${NC}"
    echo -e "   Size: $DB_SIZE"
else
    echo -e "${RED}❌ Restore failed${NC}"
    rm "$TEMP_FILE"
    exit 1
fi

# Verify database
echo -e "\n🔍 Verifying database..."
python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('$DB_PATH')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM accounts')
    count = cursor.fetchone()[0]
    conn.close()
    print(f'✅ Database verified: {count} accounts')
except Exception as e:
    print(f'❌ Verification failed: {e}')
    exit(1)
"

echo -e "\n${GREEN}✅ Restore completed successfully!${NC}"
echo "=========================================="
