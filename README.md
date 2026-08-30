# Бот-ассистент

## Описание проекта

**Бот-ассистент** - Telegram-бот, который отслеживает статус проекта через API Яндекс Практикума, логирует события и отправляет уведомления в Telegram.

## Стек технологий

- **Бэкенд:** Python 3.12;
- **Библиотеки:**
  - **pyTelegramBotAPI** - для работы с Telegram Bot API;
  - **requests** - для взаимодействия с API Яндекс Практикума;
  - **python-dotenv** - для управления переменными окружения.
- **Логирование:** logging;
- **Инструменты:** Git, GitHub, pytest, flake8.

---

## Как запустить бота

### 1. Клонируйте репозиторий и перейдите в него в командной строке

```
git clone https://github.com/russinArtem/assistant-bot.git
cd assistant-bot
```

### 2. Создайте и активируйте виртуальное окружение

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас Windows

    ```
    source venv/Scripts/activate
    ```

### 3. Обновите пакетный менеджер `pip` и установите зависимости из файла `requirements.txt`

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

### 4. Создайте и заполните файл `.env`
В корне проекта создайте файл `.env` и укажите в нем переменные из файла `.env.example`. В `.env` присвойте переменным свои актуальные значения.

### 5. Запустите бота

```
python homework.py
```

---

## Автор

**Артем Руссин**

GitHub: [russinArtem](https://github.com/russinArtem/)

Email: [russinartem@yandex.ru](mailto:russinartem@yandex.ru)

## Лицензия

Проект выполнен в рамках учебного курса [Яндекс.Практикум](https://practicum.yandex.ru/).
