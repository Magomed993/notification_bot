import requests
import time
import sys
import os
import telegram
from pprint import pprint
from dotenv import load_dotenv


def main():
    load_dotenv()
    dvmn_token = os.environ['DVMN_TOKEN']
    bot_token = os.environ['BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(token=bot_token)
    number = 5

    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': dvmn_token,}
    payload = {'timestamp': None,}

    while True:
        try:
            response = requests.get(url, headers=headers, params=payload, timeout=number)
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
                        continue
                    bot.send_message(chat_id=chat_id,
                                         text=f'''У вас проверили работу "{attempt['lesson_title']}"
К сожалению, в работе нашлись ошибки.
{attempt['lesson_url']}''')

        except requests.exceptions.ConnectionError:
            print('Соединение прервано. Скрипт продолжает работу', file=sys.stderr)
            time.sleep(1800)
        except requests.exceptions.ReadTimeout:
            continue


if __name__ == '__main__':
    main()
