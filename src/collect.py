import os
import requests 
import json
import time
import logging

os.makedirs('data/raw', exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

url = 'https://api.opendota.com/api/publicMatches'
path = 'data/raw/public_matches.jsonl'
last_id = None 
batches_done = 0  
errors = 0
MAX_BATCHES = 20
ERROR_THRESHOLD = 5

while batches_done < MAX_BATCHES:

    if errors >= ERROR_THRESHOLD:
        logging.error("Too many errors occurred, stopping collection.")
        break
    try:
        response = requests.get(url, params={'less_than_match_id': last_id}, timeout=30)
    except requests.RequestException as e:
        logging.error(f"Error occurred while fetching data: {e}")
        errors += 1
        time.sleep(10)
        continue

    if response.status_code == 200:
        matches = response.json()
        if not matches:
            logging.info("Match is empty, stopping collection.")
            break
        with open(path, 'a', encoding='utf-8') as f:
            for match in matches:
                f.write(json.dumps(match) + '\n')
                current_id = match['match_id']
                if last_id is None or current_id < last_id:
                    last_id = current_id
        batches_done += 1
        logging.info(f"Batch {batches_done}/20: {len(matches)} matches, last_id={last_id}")
        errors = 0

    else:   
        logging.error(f"Error occurred while fetching data: {response.status_code}")
        errors += 1
        time.sleep(10)
    time.sleep(1)  