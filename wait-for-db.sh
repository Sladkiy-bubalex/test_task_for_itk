#!/bin/bash

set -e

# параметры по умолчанию
HOST=${DB_HOST:-db}
PORT=${DB_PORT:-5432}

until nc -z $HOST $PORT; do
  >&2 echo "БД не доступна на $HOST:$PORT - жду..."
  sleep 1
done

>&2 echo "БД на $HOST:$PORT доступна — продолжаем."