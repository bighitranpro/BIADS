#!/bin/bash

###############################################################################
# Bi Ads Database Backup Script
# Tự động backup database với timestamp và giữ N bản backup gần nhất
###############################################################################

# Configuration
DB_PATH="backend/data/bi_ads.db"
BACKUP_DIR="backups/database"
MAX_BACKUPS=30  # Giữ 30 bản backup gần nhất
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="bi_ads_${DATE}.db"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Bi Ads Database Backup"
echo "=========================================="
echo

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}❌ Database không tồn tại: $DB_PATH${NC}"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Get database size
DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
echo -e "📊 Database size: ${GREEN}$DB_SIZE${NC}"

# Backup database
echo -e "💾 Backing up database..."
cp "$DB_PATH" "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup created: $BACKUP_DIR/$BACKUP_FILE${NC}"
    
    # Compress backup
    echo -e "🗜️  Compressing backup..."
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        COMPRESSED_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_FILE}.gz" | cut -f1)
        echo -e "${GREEN}✅ Compressed: ${BACKUP_FILE}.gz (${COMPRESSED_SIZE})${NC}"
    else
        echo -e "${RED}❌ Compression failed${NC}"
    fi
else
    echo -e "${RED}❌ Backup failed${NC}"
    exit 1
fi

# Cleanup old backups
echo -e "\n🧹 Cleaning up old backups..."
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/bi_ads_*.db.gz 2>/dev/null | wc -l)

if [ $BACKUP_COUNT -gt $MAX_BACKUPS ]; then
    OLD_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
    ls -t "$BACKUP_DIR"/bi_ads_*.db.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs rm
    echo -e "${GREEN}✅ Deleted $OLD_COUNT old backup(s)${NC}"
else
    echo -e "${YELLOW}ℹ️  No cleanup needed (${BACKUP_COUNT}/${MAX_BACKUPS} backups)${NC}"
fi

# Show backup list
echo -e "\n📋 Recent backups:"
ls -lth "$BACKUP_DIR"/bi_ads_*.db.gz | head -n 5 | awk '{print "   " $9 " (" $5 ")"}'

echo -e "\n${GREEN}✅ Backup completed successfully!${NC}"
echo "=========================================="
