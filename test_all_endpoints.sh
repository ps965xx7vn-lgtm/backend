#!/bin/bash

BASE_URL="http://127.0.0.1:8001/api"
EMAIL="finaltest@example.com"
PASSWORD="TestPass123!"

echo "🧪 ФИНАЛЬНЫЙ ТЕСТ ВСЕХ ЭНДПОИНТОВ"
echo "=================================="
echo ""

# 1. Health Check
echo "1️⃣ Health Check..."
curl -s $BASE_URL/ping | python3 -m json.tool || echo "❌ FAILED"
echo ""

# 2. Register
echo "2️⃣ Регистрация..."
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"first_name\":\"Final\",\"last_name\":\"Test\"}")
echo "$REGISTER_RESPONSE" | python3 -m json.tool
ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])" 2>/dev/null)
echo "✅ Token: ${ACCESS_TOKEN:0:30}..."
echo ""

# 3. Login
echo "3️⃣ Логин..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo ""

# 4. Get Profile
echo "4️⃣ Получение профиля..."
curl -s -X GET $BASE_URL/auth/profile \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# 5. Update Profile
echo "5️⃣ Обновление профиля..."
curl -s -X PATCH $BASE_URL/auth/profile \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bio":"Final test user","city":"TestCity","country":"US"}' | python3 -m json.tool
echo ""

echo "✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!"
