#!/bin/bash

# AI Chat Platform - Project Verification Script
# This script checks that all required files are in place

echo "🔍 Verifying AI Chat Platform Project Structure..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $1 (MISSING)"
        ((FAILED++))
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $1/"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $1/ (MISSING)"
        ((FAILED++))
    fi
}

echo "📁 Backend Structure:"
check_dir "backend/app"
check_dir "backend/app/api"
check_dir "backend/app/models"
check_dir "backend/app/schemas"
check_dir "backend/app/services"
check_dir "backend/app/core"
check_file "backend/app/main.py"
check_file "backend/app/api/auth.py"
check_file "backend/app/api/chats.py"
check_file "backend/app/api/messages.py"
check_file "backend/requirements.txt"
check_file "backend/Dockerfile"
check_file "backend/.env.example"

echo ""
echo "📁 Frontend Structure:"
check_dir "frontend/src"
check_dir "frontend/src/api"
check_dir "frontend/src/components"
check_dir "frontend/src/hooks"
check_dir "frontend/src/pages"
check_dir "frontend/src/store"
check_dir "frontend/src/types"
check_file "frontend/src/App.tsx"
check_file "frontend/src/main.tsx"
check_file "frontend/package.json"
check_file "frontend/vite.config.ts"
check_file "frontend/tailwind.config.js"
check_file "frontend/.env.example"

echo ""
echo "📁 Root Level:"
check_file "docker-compose.yml"
check_file "README.md"
check_file "DEPLOYMENT.md"
check_file "PROJECT_SUMMARY.md"
check_file "TEST_LOCAL.md"
check_file ".gitignore"
check_dir ".git"

echo ""
echo "═══════════════════════════════════════════"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo "═══════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✨ All files present! Project is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Read TEST_LOCAL.md for local testing"
    echo "2. Read DEPLOYMENT.md for production deployment"
    echo "3. Add ANTHROPIC_API_KEY to backend/.env"
    echo "4. Run: docker-compose up"
    exit 0
else
    echo -e "${RED}⚠️  Some files are missing!${NC}"
    exit 1
fi
