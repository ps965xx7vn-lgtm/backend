#!/bin/sh
set -e

echo "🚀 Starting Pyland Backend..."

# PostgreSQL и Redis проверяются через healthcheck в docker-compose
# Контейнер стартует только когда зависимости готовы

# Применяем миграции (только для web сервиса и если не установлен SKIP_MIGRATIONS)
if [ "$SKIP_MIGRATIONS" != "true" ] && [ "$1" = "gunicorn" ] || [ "$1" = "python" ]; then
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
