#!/bin/bash

echo "🔄 Синхронизация с GitHub..."

# Добавляем все изменения
git add .

# Получаем текущую дату и время
current_date=$(date "+%Y-%m-%d %H:%M:%S")

# Создаем коммит с датой
git commit -m "Update: Автоматическое обновление ($current_date)"

# Отправляем изменения
git push

echo "✅ Синхронизация завершена!" 