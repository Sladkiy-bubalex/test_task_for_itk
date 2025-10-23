#!/bin/sh

echo "Ожидание базы данных..."
./wait-for-db.sh

echo "Применение миграций..."
alembic upgrade heads

echo "Запуск Сервера..."
exec "$@"