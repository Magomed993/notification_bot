import requests
from pprint import pprint

url = 'https://dvmn.org/api/long_polling/'
# url = 'https://dvmn.org/api/user_reviews/'
payload = {
    'Authorization': 'Token 3a607f104b61a812631c3e62e58acdde84b01e77'
}

response = requests.get(url, headers=payload)
response.raise_for_status()
format_response = response.json()
pprint(response.url)