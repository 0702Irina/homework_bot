import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv('TOKEN_PR')
TELEGRAM_TOKEN = os.getenv('TOKEN_TL')
TELEGRAM_CHAT_ID = os.getenv('ID')

RETRY_PERIOD = 600
ENDPOINT = os.getenv('URL')
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверяет переменные окружения."""
    """При отсутствии одной из переменных выдается ошибка."""
    if (
        PRACTICUM_TOKEN is None
        or TELEGRAM_TOKEN is None
        or TELEGRAM_CHAT_ID
    ):
        raise Exception('Проверьте правильно ли указаны токены и id чата')


def send_message(bot, message):
    """Функция отправки сообщений."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Сообщение в чат {TELEGRAM_CHAT_ID}: {message}')
    except Exception as error:
        raise SystemError('Ошибка отправки сообщения в Telegramm') from error


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
    try:
        if response.status_code != HTTPStatus.OK:
            raise logging.error(f'Ошибка {response.status_code}')
        return response.json()
    except Exception as error:
        raise SystemError(f'Ошибка при запросе: {error}')


def check_response(response):
    """Проверяет соответствие ответа API документации."""
    try:
        homework = response['homeworks']
    except KeyError as error:
        logging.error(f'Ошибка доступа по ключу homeworks: {error}')
    if not isinstance(homework, list):
        logging.error('Homeworks не в виде списка')
        raise TypeError('Homeworks не в виде списка')
    return homework


def parse_status(homework):

#   return f'Изменился статус проверки работы "{homework_name}". {verdict}'


# def main():
#    """Основная логика работы бота."""


#   bot = telegram.Bot(token=TELEGRAM_TOKEN)
#   timestamp = int(time.time())


#   while True:
#       try:

#

#        except Exception as error:
#            message = f'Сбой в работе программы: {error}'
#
#


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename='homework.log',
        format='%(asctime)s, %(levelname)s, %(name)s, %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
    main()
