from http import HTTPStatus
import logging
import os
import requests
from requests.exceptions import ConnectionError
import sys
import time

from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (
    APIRequestError, APIServerError, BadRequestError,
    ForbiddenError, UnauthorizedError
)


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
KEY_ERROR_FROM_DATE = 'error'
KEY_MESSAGE_ERROR_PRACTICUM_TOKEN = 'message'
KEY_HOMEWORKS = 'homeworks'
KEY_CURRENT_DATE = 'current_date'
KEY_HOMEWORK_NAME = 'homework_name'
KEY_STATUS = 'status'
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

OK = HTTPStatus.OK
BAD_REQUEST = HTTPStatus.BAD_REQUEST
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
NOT_FOUND = HTTPStatus.NOT_FOUND
INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def check_tokens():
    """
    Проверяет доступность переменных окружения для работы программы.
    Если отсутствует хотя бы одна переменная окружения — продолжать
    работу бота нет смысла.
    """
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logger.critical(
            'Отсутствуют обязательные переменные окружения.'
        )
        raise SystemExit(
            'Программа остановлена из-за отсутствия переменных окружения'
        )


def send_message(bot, message):
    """
    Отправляет сообщение в чат, определяемый константой TELEGRAM_CHAT_ID.
    Принимает на вход два параметра: экземпляр класса TeleBot и
    строку с текстом сообщения.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Бот отправил сообщение: {message}')
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(timestamp):
    """Делает запрос к API сервиса Практикум Домашка.
    В качестве параметра в функцию передаётся временная метка.
    В случае успешного запроса должна вернуть ответ API,
    приведя его из формата JSON к типам данных Python.
    """
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        status_code = response.status_code
        if status_code != OK:
            if status_code == BAD_REQUEST:
                raise BadRequestError(
                    f'Некорректный запрос: {status_code}, '
                    f'ошибка: {response.json().get(KEY_ERROR_FROM_DATE, {})}.'
                )
            elif status_code == UNAUTHORIZED:
                raise UnauthorizedError(
                    f'Ошибка аутентификации: {status_code}, '
                    f'сообщение об ошибке: {response.json().get(
                        KEY_MESSAGE_ERROR_PRACTICUM_TOKEN,
                        'Не удалось получить сообщение об ошибке'
                    )}.'
                )
            elif status_code == NOT_FOUND:
                raise ForbiddenError(
                    f'Эндпоинт {ENDPOINT} недоступен. '
                    f'Код ответа API: {NOT_FOUND}.'
                )
            elif status_code >= INTERNAL_SERVER_ERROR:
                raise APIServerError(
                    f'Внутренняя ошибка сервера: {status_code}.'
                )
            else:
                raise APIRequestError(f'Ошибка запроса: {status_code}.')
        else:
            return response.json()
    except ConnectionError as error:
        raise ConnectionError(f'Ошибка подключения к серверу. {error}.')
    except requests.RequestException as error:
        raise Exception(f'Произошла ошибка при запросе к API. {error}.')


def check_response(response):
    """
    Проверяет ответ API на соответствие документации.
    В качестве параметра функция получает ответ API, приведённый
    к типам данных Python.
    """
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем.')
    for key in [KEY_HOMEWORKS, KEY_CURRENT_DATE]:
        if key not in response:
            raise KeyError(f'В ответе API отсутствует ключ {key}.')
    homeworks = response[KEY_HOMEWORKS]
    if not isinstance(homeworks, list):
        raise TypeError(
            'Значение ключа homeworks в ответе API не является списком.'
        )
    return homeworks, response[KEY_CURRENT_DATE]


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент из списка
    домашних работ. В случае успеха функция возвращает подготовленную
    для отправки в Telegram строку, содержащую один из вердиктов
    словаря HOMEWORK_VERDICTS.
    """
    if not isinstance(homework, dict):
        raise TypeError(
            'Объект не является словарем, ожидается словарь для работы'
            'с данными домашней работы.'
        )
    for key in [
        KEY_HOMEWORK_NAME,
        KEY_STATUS,
    ]:
        if key not in homework:
            raise KeyError(
                f'Для работы с данными домашней работы отсутствует ключ {key}.'
            )
    status = homework[KEY_STATUS]
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус домашней работы: "{status}".')
    return (
        f'Изменился статус проверки работы "{homework[KEY_HOMEWORK_NAME]}". '
        f'{HOMEWORK_VERDICTS[status]}'
    )


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_error_message = None
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks, timestamp = check_response(response)
            if homeworks:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
            else:
                logger.debug('В ответе API отсутствуют новые статусы.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != last_error_message:
                send_message(bot, message)
                last_error_message = message
        finally:
            time.sleep(RETRY_PERIOD)
            check_tokens()


if __name__ == '__main__':
    main()
