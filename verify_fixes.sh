#!/bin/bash

echo "==============================================="
echo "ПРОВЕРКА ИСПРАВЛЕНИЙ 502 ОШИБКИ"
echo "==============================================="
echo ""

echo "1. Проверка messages.py..."
if grep -q "from datetime import datetime" backend/app/api/messages.py; then
    echo "   ✓ Import datetime найден"
else
    echo "   ✗ Import datetime НЕ найден"
    exit 1
fi

if grep -q "__import__" backend/app/api/messages.py; then
    echo "   ✗ __import__() все еще присутствует!"
    exit 1
else
    echo "   ✓ __import__() удален"
fi

if grep -q "datetime.utcnow()" backend/app/api/messages.py; then
    echo "   ✓ datetime.utcnow() используется правильно"
else
    echo "   ✗ datetime.utcnow() не найден"
    exit 1
fi

echo ""
echo "2. Проверка chats.py..."
if grep -q "from sqlalchemy import.*delete" backend/app/api/chats.py; then
    echo "   ✓ Import delete найден"
else
    echo "   ✗ Import delete НЕ найден"
    exit 1
fi

if grep -q "delete(Chat).where(Chat.id == chat_id)" backend/app/api/chats.py; then
    echo "   ✓ Правильный delete statement используется"
else
    echo "   ✗ delete(Chat) не найден"
    exit 1
fi

echo ""
echo "3. Проверка main.py..."
if grep -q "Database connection successful" backend/app/main.py; then
    echo "   ✓ DB connection check добавлен в startup"
else
    echo "   ✗ DB connection check НЕ найден"
    exit 1
fi

echo ""
echo "==============================================="
echo "ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ ✓"
echo "==============================================="
echo ""
echo "Готово к deployment на Railway!"
