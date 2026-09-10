# Бот-ассистент - телеграм-бот

## Описание проекта

**Бот-ассистент** - Telegram-бот, который отслеживает статус проекта через API Яндекс Практикума, логирует события и отправляет уведомления в Telegram.

## Стек технологий

**Бэкенд:**
![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=flat-square&logo=python&logoColor=white)

**Библиотеки:**
![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![requests](https://img.shields.io/badge/requests-3776AB?style=flat-square&logo=python&logoColor=white)
![python-dotenv](https://img.shields.io/badge/python--dotenv-ECD53F?style=flat-square&logo=python&logoColor=black)

**Логирование:**
![logging](https://img.shields.io/badge/logging-3776AB?style=flat-square&logo=python&logoColor=white)

**Инструменты:**
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![flake8](https://img.shields.io/badge/flake8-3776AB?style=flat-square&logo=python&logoColor=white)

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
