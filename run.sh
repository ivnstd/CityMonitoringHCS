#!/bin/bash

# Функция для остановки сервисов при получении сигнала SIGINT
stop_services() {
    echo "Stopping services..."
    pkill -P $$  # Остановить все процессы, запущенные из этого скрипта
    exit 0
}

# Зарегистрировать функцию stop_services для обработки сигнала SIGINT
trap stop_services SIGINT

# Запуск первого сервиса
uvicorn src.supervisor.app.main:app --host 0.0.0.0 --port 8000 --reload &

# Запуск второго сервиса
uvicorn src.parser_service.app.main:app --host 0.0.0.0 --port 8001 --reload &

# Запуск третьего сервиса
#uvicorn src.nlp_service.app.main:app --host 0.0.0.0 --port 8002 --reload &

# Ожидание завершения скрипта
wait