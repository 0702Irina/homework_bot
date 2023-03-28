import logging
import os
import sys
import time
from http import HTTPStatus
import requests
import telegram
from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_PERIOD = 600
ENDPOINT = os.getenv('URL')
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='homework.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def check_tokens():
    """Функция проверяет переменные окружения."""
    """При отсутствии одной из переменных выдается ошибка."""
    list_env = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    return all(list_env)


def send_message(bot, message):
    """Функция отправки сообщений."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Сообщение в чат {TELEGRAM_CHAT_ID}: {message}')
    except Exception as error:
        raise logger.error('Ошибка отправки сообщения в Telegramm') from error


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise logging.error(f'Ошибка {response.status_code}')
        return response.json()
    except requests.exceptions.RequestException as error:
        logger.error(f'API Практикума не отвечает. {error}')
        raise Exception(f'API Практикума не отвечает. {error}')


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
    """Извлекает из конкретной домашней работе её статус."""
    if 'homework_name' not in homework:
        raise KeyError('Ключ homework_name отсутствует в homework')
    homework_name = homework['homework_name']
    if 'status' not in homework:
        raise KeyError('Ключ status отсутствует в homework')
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(f'Статус {homework_status} неизвестен')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Ошибочный токен.')
        sys.exit('Ошибочный токен.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if not homework:
                text = 'Обновлений нет'
            else:
                text = parse_status(homework[0])
            current_timestamp = response['current_date']
        except ReferenceError as error:
            text = f'Ошибка: {error}'
            logger.error(error)
        except KeyError as error:
            text = f'Ошибка: {error}'
            logger.error(error)
        except TypeError as error:
            text = f'Ошибка: {error}'
            logger.error(error)
        finally:
            send_message(bot, text)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
