import requests
import time
import sys
import os
import logging
import telegram
from pprint import pprint
from dotenv import load_dotenv


logger = logging.getLogger(__file__)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    load_dotenv()
    dvmn_token = os.environ['DVMN_TOKEN']
    bot_token = os.environ['BOT_TOKEN']
    loggs_token = os.environ['LOGGS_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=bot_token)
    log_bot = telegram.Bot(token=loggs_token)
    timeout = 5

    logger.setLevel(logging.INFO)
    log_handler = TelegramLogsHandler(log_bot, chat_id)
    logger.addHandler(log_handler)

    logger.info("Бот запущен!")

    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': dvmn_token,}
    payload = {'timestamp': None,}

    while True:
        try:
            response = requests.get(url, headers=headers, params=payload, timeout=timeout)
            response.raise_for_status()
            format_response = response.json()
            if 'last_attempt_timestamp' in format_response:
                payload['timestamp'] = format_response['last_attempt_timestamp']
                print('Найдены новые события!')
                for attempt in format_response.get('new_attempts', []):
                    pprint(attempt)
                    if not attempt['is_negative']:
                        bot.send_message(chat_id=chat_id,
                                         text=f'''У вас проверили работу "{attempt['lesson_title']}"
Преподавателю всё понравилось, можно приступать к следующему уроку!''')
                        logger.info('Отправлено сообщение')
                        continue
                    bot.send_message(chat_id=chat_id,
                                         text=f'''У вас проверили работу "{attempt['lesson_title']}"
К сожалению, в работе нашлись ошибки.
{attempt['lesson_url']}''')
                    logger.info('Отправлено сообщение')

        except requests.exceptions.ConnectionError:
            print('Соединение прервано. Скрипт продолжает работу', file=sys.stderr)
            time.sleep(1800)
        except requests.exceptions.ReadTimeout:
            continue
        except Exception as err:
            logger.exception(err)


if __name__ == '__main__':
    main()
