from datetime import datetime
import json
import random
import requests
from urllib.parse import quote

GET_QUOTE_USERNAME="kodaly"
GET_QUOTE_START_YEAR=2016
GET_QUOTE_START_MONTH=3
GET_QUOTE_END_YEAR=2020
GET_QUOTE_END_MONTH=10
GET_QUOTE_MINIMUM_WORDS=3
GET_QUOTE_MAX_TRIES=100
GET_QUOTE_OUTPUT_PATH="./site/data/quote.json"

def get_rustlesearch_url():
    search_year = random.randint(GET_QUOTE_START_YEAR, GET_QUOTE_END_YEAR)
    search_month = random.randint(GET_QUOTE_START_MONTH, GET_QUOTE_END_MONTH)
    search_day = random.randint(1, 31)
    # https://api-v2.rustlesearch.dev/anon/search?start_date=2010-01-01&end_date=2025-11-11&channel=Destinygg&username=kodaly&search_after=1600574915000
    return ("https://api-v2.rustlesearch.dev/anon/search?"
            f"start_date={search_year}-{search_month:02d}-{search_day:02d}&"
            f"end_date={search_year}-{search_month:02d}-{(search_day+1):02d}&"
            f"channel=Destinygg&username={GET_QUOTE_USERNAME}")

def get_surrounds_url(message):
    # https://rustlesearch.dev/surrounds?channel=Destinygg&date=2018-09-12T02%3A08%3A49.000Z&username=kodaly
    return ("https://rustlesearch.dev/surrounds?"
            "channel=Destinygg&"
            f"date={quote(message['ts'])}&"
            f"username={message['username']}")

def get_rustlesearch_messages():
    url = get_rustlesearch_url()
    output = get_overrustle_data(url)
    return json.loads(output)

def valid_quote_message(message):
    if len(message['text'].split()) < GET_QUOTE_MINIMUM_WORDS:
        return False
    else:
        return True

def valid_rustlesearch_messages(messages):
    if messages['type'] != 'Success':
        print(f"Message type is not 'Success': ({messages['type']})")
        return False
    elif messages['error'] != None:
        print(f"Error should be none: ({messages['error']})")
        return False
    elif len(messages['data']['messages']) <= 0:
        print(f"No messages in this query!")
        return False
    else:
        print("Messages are good!")
        return True

def get_quote_message():
    for _ in range(GET_QUOTE_MAX_TRIES):
        messages_obj = get_rustlesearch_messages()
        if not valid_rustlesearch_messages(messages_obj):
            continue

        messages = messages_obj['data']['messages']
        random.shuffle(messages)
        json.dumps(messages, indent=4)
        for message in messages:
            if valid_quote_message(message):
                return message

def get_overrustle_data(url):
    for _ in range(5):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"Error downloading the page: {e}")

    raise RuntimeError("Failed 5 times to download webpage!")

def get_short_date(message):
    dt = datetime.strptime(message['ts'], "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%d")

if __name__ == "__main__":
    message = get_quote_message()
    short_date = get_short_date(message)
    output = { "quote": message,  "date": short_date, "surrounds": get_surrounds_url(message)}
    with open(GET_QUOTE_OUTPUT_PATH, 'w') as f:
        f.write(json.dumps(output, indent=4))