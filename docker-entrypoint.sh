#!/bin/sh
set -e

echo "🚀 Starting Pyland Backend..."

# Ждём готовности PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready!"

# Ждём готовности Redis
echo "⏳ Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  sleep 0.1
done
echo "✅ Redis is ready!"

# Применяем миграции (только для web сервиса)
if [ "$1" = "gunicorn" ] || [ "$1" = "python" ]; then
    echo "📦 Running migrations..."
    python manage.py migrate --noinput || echo "⚠️ Migrations failed"

    echo "👥 Creating user roles..."
    python manage.py create_roles || echo "⚠️ Roles already exist"

    echo "🌍 Compiling translations..."
    python manage.py compilemessages || echo "⚠️ Translation compilation failed"

    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput || echo "⚠️ Static collection failed"
fi

echo "✅ Entrypoint completed. Starting application..."

# Выполняем команду из CMD
exec "$@"
