import requests
from lxml import html
import json
import time
import random

CHANNEL_HANDLE = '@TEDx'
BASE_URL = f'https://www.youtube.com/{CHANNEL_HANDLE}/videos'
API_URL = 'https://www.youtube.com/youtubei/v1/browse'
HEADERS = {'Content-Type': 'application/json'}
CLIENT_CONTEXT = {
    'context': {
        'client': {
            'clientName': 'WEB',
            'clientVersion': '2.20240313.05.00'
        }
    }
}

def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def fetch_page_with_retry(url, retries=5, delay=5):
    for i in range(retries):
        try:
            return fetch_page(url)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"Failed to fetch page after {retries} retries")

def parse_initial_data(text):
    tree = html.fromstring(text)
    yt_variable_name = 'ytInitialData'
    yt_variable_declaration = yt_variable_name + ' = '
    for script in tree.xpath('//script'):
        script_content = script.text_content()
        if yt_variable_declaration in script_content:
            return json.loads(script_content.split(yt_variable_declaration)[1][:-1])
    return None

def extract_video_titles(contents, titles):
    for content in contents:
        if 'richItemRenderer' not in content:
            continue
        title = content['richItemRenderer']['content']['videoRenderer']['title']['accessibility']['accessibilityData']['label']
        titles.append(title)

def get_continuation_token(contents):
    last_content = contents[-1]
    if 'continuationItemRenderer' not in last_content:
        return None
    return last_content['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']

def fetch_continuation_data(token):
    request_data = CLIENT_CONTEXT.copy()
    request_data['continuation'] = token
    response = requests.post(API_URL, headers=HEADERS, json=request_data)
    response.raise_for_status()
    return response.json()

def fetch_continuation_data_with_retry(token, retries=5, delay=5):
    for i in range(retries):
        try:
            return fetch_continuation_data(token)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching continuation data: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"Failed to fetch continuation data after {retries} retries")

def random_sleep(min_delay=1, max_delay=3):
    delay = random.uniform(min_delay, max_delay)
    # print(f"Sleeping for {delay:.2f} seconds")
    time.sleep(delay)

def main():
    start_time = time.time()
    titles = []
    
    try:
        text = fetch_page_with_retry(BASE_URL)
        yt_data = parse_initial_data(text)
        if not yt_data:
            print("Failed to retrieve initial data")
            return

        contents = yt_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents']
        
        extract_video_titles(contents, titles)
        continuation_token = get_continuation_token(contents)

        while continuation_token:
            data = fetch_continuation_data_with_retry(continuation_token)
            if 'onResponseReceivedActions' not in data:
                print('Retrying')
                continue
            continuation_items = data['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems']
            extract_video_titles(continuation_items, titles)
            continuation_token = get_continuation_token(continuation_items)
            
            if len(titles) % 5000 == 0:
                print(f"Progress: {len(titles)} video titles extracted")
            
            random_sleep()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        with open('video_titles_TEDx.json', 'w') as file:
            json.dump(titles, file, ensure_ascii=False, indent=4)
        
        end_time = time.time()
        print(f"Processing time: {end_time - start_time} seconds")
        print(f"Total video titles extracted: {len(titles)}")

if __name__ == "__main__":
    main()