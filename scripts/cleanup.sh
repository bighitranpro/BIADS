#!/bin/bash
# Bi Ads Cleanup Script - Phase 1: Safe Cleanup
# This script removes duplicate/temporary/cache files safely

set -e  # Exit on error

echo "🧹 Bi Ads Multi Tool PRO - Cleanup Script"
echo "=========================================="
echo ""

# Save current size
BEFORE_SIZE=$(du -sh . | cut -f1)
echo "📊 Current size: $BEFORE_SIZE"
echo ""

# Phase 1: Remove duplicate backend venv (WRONG LOCATION)
echo "🗑️  Phase 1: Removing duplicate backend/venv..."
if [ -d "backend/venv" ]; then
    SIZE=$(du -sh backend/venv | cut -f1)
    rm -rf backend/venv
    echo "   ✅ Removed backend/venv ($SIZE)"
else
    echo "   ℹ️  backend/venv not found"
fi

# Phase 2: Clean all __pycache__
echo ""
echo "🗑️  Phase 2: Cleaning __pycache__ directories..."
PYCACHE_COUNT=$(find . -type d -name "__pycache__" | wc -l)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "   ✅ Removed $PYCACHE_COUNT __pycache__ directories"

# Phase 3: Remove .env (sensitive file)
echo ""
echo "🗑️  Phase 3: Removing sensitive .env file..."
if [ -f ".env" ]; then
    rm .env
    echo "   ✅ Removed .env (use .env.example instead)"
else
    echo "   ℹ️  .env not found"
fi

# Phase 4: Remove temporary test file
echo ""
echo "🗑️  Phase 4: Removing temporary test file..."
if [ -f "test-accounts.html" ]; then
    mkdir -p tests/frontend
    mv test-accounts.html tests/frontend/
    echo "   ✅ Moved test-accounts.html to tests/frontend/"
else
    echo "   ℹ️  test-accounts.html not found"
fi

# Phase 5: Archive old documentation
echo ""
echo "📦 Phase 5: Archiving old documentation..."
mkdir -p docs/archive

DOCS_TO_ARCHIVE=(
    "HUONG_DAN_BI_ADS_V2.md"
    "HUONG_DAN_SU_DUNG.md"
    "ADVANCED_DEVELOPMENT_PLAN.md"
    "IMPLEMENTATION_SUMMARY.md"
    "PR_DESCRIPTION.md"
    "BUGFIX_SUMMARY.md"
    "NANG_CAP_UNG_DUNG.md"
    "QUICK_START_GUIDE.md"
    "TOM_TAT_DE_XUAT.md"
)

ARCHIVED=0
for doc in "${DOCS_TO_ARCHIVE[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" docs/archive/
        echo "   ✅ Archived $doc"
        ARCHIVED=$((ARCHIVED + 1))
    fi
done
echo "   📁 Archived $ARCHIVED documentation files"

# Phase 6: Clean obsolete files
echo ""
echo "🗑️  Phase 6: Removing obsolete files..."
if [ -f "COMMANDS.txt" ]; then
    rm COMMANDS.txt
    echo "   ✅ Removed COMMANDS.txt"
fi

if [ -f ".electron-version" ]; then
    rm .electron-version
    echo "   ✅ Removed .electron-version"
fi

# Show results
echo ""
echo "✅ Cleanup Complete!"
echo "===================="
AFTER_SIZE=$(du -sh . | cut -f1)
echo "📊 Before: $BEFORE_SIZE"
echo "📊 After:  $AFTER_SIZE"
echo ""
echo "🎉 Next steps:"
echo "   1. Review changes with: git status"
echo "   2. Test backend: cd backend && python main.py"
echo "   3. Test frontend: npm start"
echo "   4. Commit changes: git add . && git commit -m 'chore: cleanup and reorganization'"
