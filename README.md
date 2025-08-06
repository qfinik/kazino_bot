# Telegram Казино-бот 🎰

## Запуск 24/7 на Render (с телефона)

1. Создай аккаунт на GitHub и загрузи туда файлы:
   - bot.py
   - requirements.txt
   - start.sh

2. Перейди на https://render.com
3. Авторизуйся через GitHub
4. Нажми **New → Web Service**
5. Выбери свой репозиторий с ботом
6. В настройках:
   - **Environment**: Python 3
   - **Build Command**: pip install -r requirements.txt
   - **Start Command**: bash start.sh
7. Нажми **Deploy** — бот запустится 24/7
