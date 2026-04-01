from http import HTTPStatus
import logging
import os
import sys
import time

from dotenv import load_dotenv
import requests
from telebot import TeleBot

from exceptions import (APIDataError, APIRequestError)


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
NAME_TOKENS = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

OK = HTTPStatus.OK

MISSING_TOKENS_MSG = (
    'Отсутствуют обязательные переменные окружения: {missing_tokens}. '
    'Программа принудительно остановлена.'
)
SUCCESS_MESSAGE_MSG = 'Бот отправил сообщение: {message}'
ERROR_SUCCESS_MESSAGE_MSG = (
    'Ошибка при отправке сообщения "{message}": {error}'
)
API_ERROR_COMMON_MSG = (
    'URL: {endpoint}. '
    'Заголовки: {headers}. '
    'Параметры запроса: {params}.'
)
API_REQUEST_ERROR_MSG = (
    'Ошибка при запросе к API. {error}. ' + API_ERROR_COMMON_MSG
)
API_STATUS_ERROR_MSG = (
    'Ошибка при запросе к API: {status_code}. ' + API_ERROR_COMMON_MSG
)
API_DATA_ERROR_MSG = (
    'Ошибка в ответе API. Код ошибки: {code}. Сообщение: {error_msg}. '
    + API_ERROR_COMMON_MSG
)
TYPE_ERROR_RESPONSE_NOT_DICT_MSG = (
    'Ответ API не является словарем, получен тип {type_response}'
)
KEY_ERROR_HOMEWORKS_MISSING_MSG = 'В ответе API отсутствует ключ "homeworks".'
TYPE_ERROR_HOMEWORKS_NOT_LIST_MSG = (
    'Значение ключа "homeworks" в ответе API не является списком, '
    'получен тип {type_homeworks}'
)
KEY_ERROR_DATA_HOMEWORK_MISSING_MSG = (
    'Для работы с данными домашней работы отсутствует ключ {key}'
)
VALUE_ERROR_UNKNOWN_STATUS_MSG = (
    'Неизвестный статус домашней работы: "{status}"'
)
STATUS_CHANGED_HOMEWORK_MSG = (
    'Изменился статус проверки работы "{homework_name}". {verdict}'
)
NO_NEW_STATUSES_MSG = 'В ответе API отсутствуют новые статусы.'
PROGRAM_FAILURE_MSG = 'Сбой в работе программы: {error}'


logger = logging.getLogger(__name__)


def check_tokens():
    """
    Проверяет доступность переменных окружения для работы программы.
    Если отсутствует хотя бы одна переменная окружения — продолжать
    работу бота нет смысла.
    """
    missing_tokens = [name for name in NAME_TOKENS if not globals()[name]]
    if missing_tokens:
        logger.critical(
            MISSING_TOKENS_MSG.format(missing_tokens=', '.join(missing_tokens))
        )
        return False
    return True


def send_message(bot, message):
    """
    Отправляет сообщение в чат, определяемый константой TELEGRAM_CHAT_ID.
    Принимает на вход два параметра: экземпляр класса TeleBot и
    строку с текстом сообщения.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(SUCCESS_MESSAGE_MSG.format(message=message))
        return True
    except Exception as error:
        logger.error(
            ERROR_SUCCESS_MESSAGE_MSG.format(message=message, error=error),
            exc_info=True
        )
        return False


def get_api_answer(timestamp):
    """Делает запрос к API сервиса Практикум Домашка.
    В качестве параметра в функцию передаётся временная метка.
    В случае успешного запроса должна вернуть ответ API,
    приведя его из формата JSON к типам данных Python.
    """
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.RequestException as error:
        raise APIRequestError(API_REQUEST_ERROR_MSG.format(
            error=error, endpoint=ENDPOINT, headers=HEADERS, params=params
        ))
    status_code = response.status_code
    if status_code != OK:
        raise APIRequestError(API_STATUS_ERROR_MSG.format(
            status_code=status_code,
            endpoint=ENDPOINT,
            headers=HEADERS,
            params=params
        ))
    data = response.json()
    if 'code' in data or 'error' in data:
        raise APIDataError(API_DATA_ERROR_MSG.format(
            code=data.get('code', 'не указан'),
            error_msg=data.get('error', 'не указано'),
            endpoint=ENDPOINT,
            headers=HEADERS,
            params=params
        ))
    return data


def check_response(response):
    """
    Проверяет ответ API на соответствие документации.
    В качестве параметра функция получает ответ API, приведённый
    к типам данных Python.
    """
    if not isinstance(response, dict):
        raise TypeError(TYPE_ERROR_RESPONSE_NOT_DICT_MSG.format(
            type_response=type(response)
        ))
    if 'homeworks' not in response:
        raise KeyError(KEY_ERROR_HOMEWORKS_MISSING_MSG)
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError(TYPE_ERROR_HOMEWORKS_NOT_LIST_MSG.format(
            type_homeworks=type(homeworks)
        ))
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент из списка
    домашних работ. В случае успеха функция возвращает подготовленную
    для отправки в Telegram строку, содержащую один из вердиктов
    словаря HOMEWORK_VERDICTS.
    """
    for key in [
        'homework_name',
        'status',
    ]:
        if key not in homework:
            raise KeyError(KEY_ERROR_DATA_HOMEWORK_MISSING_MSG.format(key=key))
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(VALUE_ERROR_UNKNOWN_STATUS_MSG.format(status=status))
    return STATUS_CHANGED_HOMEWORK_MSG.format(
        homework_name=homework['homework_name'],
        verdict=HOMEWORK_VERDICTS[status]
    )


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_error_message = None
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks and send_message(bot, parse_status(homeworks[0])):
                if 'current_date' in response:
                    timestamp = response['current_date']
            else:
                logger.debug(NO_NEW_STATUSES_MSG)
        except Exception as error:
            message = PROGRAM_FAILURE_MSG.format(error=error)
            logger.error(message)
            if message != last_error_message and send_message(bot, message):
                last_error_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format=('%(asctime)s [%(levelname)s] %(message)s — %(filename)s: '
                '%(lineno)d в функции %(funcName)s'
                ),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'{__file__}.log', encoding='utf-8')
        ]
    )
    main()
